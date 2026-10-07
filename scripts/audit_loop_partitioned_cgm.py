#!/usr/bin/env python3
"""Run a storage-bounded, participant-sorted canonical CGM audit for Loop.

Temporary files contain only the minimal canonicalization projection and are
removed on successful completion.  The JSON report contains no patient IDs.
"""

from __future__ import annotations

import argparse
import gzip
import json
import shutil
import subprocess
import tempfile
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from t1d_tkg.temporal_eligibility import audit_cadence_tolerant, audit_exact_grid, audit_logical_grid, logical_grid_episode_counts, logical_grid_window_metadata
from t1d_tkg.baselines import persistence_slope_score_from_values
from t1d_tkg.metrics import average_precision


FIELDS = ["PtID", "RecID", "ParentLOOPDeviceUploadsID", "UTCDtTm", "RecordType", "CGMVal", "Units"]
UTC_FORMAT = "%Y-%m-%d %H:%M:%S"


def bucket(patient: bytes, count: int) -> int:
    # The same cryptographic hash used in the footprint estimator.
    import hashlib
    return int.from_bytes(hashlib.blake2b(patient, digest_size=8).digest(), "big") % count


def partition(paths: list[Path], directory: Path, count: int, *, minimum_free_gib: float = 0.0) -> tuple[int, list[Path]]:
    if minimum_free_gib and shutil.disk_usage(directory).free < minimum_free_gib * 1024**3:
        raise RuntimeError("free-space safety floor reached before partitioning")
    scanned = 0
    outputs = [directory / f"cgm-{number:02d}.psv" for number in range(count)]
    handles = [path.open("wb") for path in outputs]
    rows = 0
    try:
        for path in paths:
            with path.open("rb") as source:
                header = source.readline().decode("utf-8-sig", "replace").rstrip("\r\n").split("|")
                indexes = [header.index(field) for field in FIELDS]
                for raw in source:
                    scanned += 1
                    if minimum_free_gib and scanned % 10000 == 0 and shutil.disk_usage(directory).free < minimum_free_gib * 1024**3:
                        raise RuntimeError("free-space safety floor reached during partitioning")
                    parts = raw.rstrip(b"\r\n").split(b"|")
                    selected = b"|".join(parts[index] for index in indexes) + b"\n"
                    handles[bucket(parts[indexes[0]].strip(), count)].write(selected)
                    rows += 1
            print(f"partitioned {path}: {rows} cumulative rows", flush=True)
    finally:
        for handle in handles:
            handle.close()
    return rows, outputs


def sorted_rows(path: Path) -> Path:
    output = path.with_suffix(".sorted")
    # Columns: patient, RecID, upload ID, UTC, RecordType, CGM value, unit.
    subprocess.run(
        ["sort", "-S", "512M", "-t", "|", "-k1,1", "-k4,4", "-k5,5", "-k6,6", "-k7,7", "-k2,2n", "-o", str(output), str(path)],
        check=True,
    )
    path.unlink()
    return output


def audit_partition(path: Path, *, selected_patients: set[str] | None = None, tolerances: tuple[int, ...] = (), logical_grid_tolerance: int | None = None, window_index_path: Path | None = None, window_index_group: str | None = None, rule_baseline: bool = False) -> dict[str, object]:
    report: Counter[str] = Counter()
    patients: dict[bytes, dict[str, object]] = {}
    exact_key: tuple[bytes, ...] | None = None
    exact_group: list[bytes] = []
    timestamp_key: tuple[bytes, bytes] | None = None
    timestamp_records: list[bytes] = []

    def close_timestamp() -> None:
        if not timestamp_records or timestamp_key is None:
            return
        patient, utc = timestamp_key
        cgm_values = {(row[5], row[6]) for row in timestamp_records if row[4] == b"CGM"}
        report["calibration_canonical_rows"] += sum(row[4] == b"Calibration" for row in timestamp_records)
        if not cgm_values:
            return
        if len(cgm_values) > 1:
            report["ambiguous_cgm_timestamps"] += 1
            return
        value_raw, unit = next(iter(cgm_values))
        try:
            value = float(value_raw)
        except ValueError:
            report["non_numeric_canonical_cgm_timestamps"] += 1
            return
        if not math.isfinite(value):
            report["nonfinite_canonical_cgm_timestamps"] += 1
            return
        if unit != b"mmol/L":
            report["unexpected_cgm_unit_timestamps"] += 1
            return
        report["numeric_mmol_l_canonical_cgm_timestamps"] += 1
        state = patients.setdefault(patient, {"first": utc, "last": utc, "previous": utc, "count": 0, "largest_gap_seconds": 0, "cadence_seconds": Counter(), "readings": {}})
        previous = state["previous"]
        if utc < state["first"]:
            state["first"] = utc
        if utc > state["last"]:
            state["last"] = utc
        if utc != previous:
            gap = (datetime.strptime(utc.decode(), UTC_FORMAT) - datetime.strptime(previous.decode(), UTC_FORMAT)).total_seconds()
            state["largest_gap_seconds"] = max(state["largest_gap_seconds"], gap)
            state["cadence_seconds"][int(gap)] += 1
        state["previous"] = utc
        state["count"] += 1
        state["readings"][datetime.strptime(utc.decode(), UTC_FORMAT).replace(tzinfo=timezone.utc)] = value * 18.0182

    def close_exact_group() -> None:
        nonlocal timestamp_key, timestamp_records
        if not exact_group:
            return
        report["canonical_rows"] += 1
        report["exact_duplicates_removed"] += len(exact_group) - 1
        representative = exact_group[0]  # RecID is the final sort key.
        key = (representative[0], representative[3])
        if timestamp_key is not None and key != timestamp_key:
            close_timestamp()
            timestamp_records = []
        timestamp_key = key
        timestamp_records.append(representative)

    with path.open("rb") as handle:
        for raw in handle:
            row = raw.rstrip(b"\n").split(b"|")
            report["raw_rows"] += 1
            key = (row[0], row[3], row[4], row[5], row[6])
            if exact_key is not None and key != exact_key:
                close_exact_group()
                exact_group = []
            exact_key = key
            exact_group.append(row)
        close_exact_group()
        close_timestamp()
    path.unlink()
    temporal = [] if selected_patients is not None else [
        audit_exact_grid(state["readings"], threshold=70.0, horizon_minutes=30) for state in patients.values()
    ]
    tolerance_results: dict[int, list[dict[str, int]]] = {tolerance: [] for tolerance in tolerances}
    logical_results: list[dict[str, int]] = []
    logical_60_results: list[dict[str, int]] = []
    episode_results: list[dict[str, int]] = []
    private_rows: list[dict[str, object]] = []
    index_counts: Counter[str] = Counter()
    rule_summaries: list[dict[str, float | int | None]] = []
    index_handle = gzip.open(window_index_path, "wt", encoding="utf-8") if window_index_path else None
    if index_handle is not None:
        index_handle.write(json.dumps({"record_type": "window_index", "protocol_version": "loop-logical-grid-v1"}, sort_keys=True, separators=(",", ":")) + "\n")
    for patient, state in patients.items():
        if selected_patients is not None and patient.decode("ascii", "replace") not in selected_patients:
            continue
        for tolerance in tolerances:
            tolerance_results[tolerance].append(audit_cadence_tolerant(
                state["readings"], threshold=70.0, tolerance_seconds=tolerance, horizon_minutes=30
            ))
        if logical_grid_tolerance is not None:
            logical_30 = audit_logical_grid(state["readings"], threshold=70.0, tolerance_seconds=logical_grid_tolerance)
            logical_60 = audit_logical_grid(state["readings"], threshold=70.0, tolerance_seconds=logical_grid_tolerance, horizon_minutes=60)
            episodes = logical_grid_episode_counts(state["readings"], threshold=70.0, tolerance_seconds=logical_grid_tolerance)
            logical_results.append(logical_30)
            logical_60_results.append(logical_60)
            episode_results.append(episodes)
            private_rows.append({
                "patient_id": patient.decode("ascii", "replace"),
                "numeric_cgm_timestamps": state["count"],
                "first_utc": state["first"].decode(),
                "last_utc": state["last"].decode(),
                "largest_gap_seconds": state["largest_gap_seconds"],
                "logical_30m": logical_30,
                "logical_60m": logical_60,
                "episodes": episodes,
            })
            if index_handle is not None:
                patient_id = patient.decode("ascii", "replace")
                for metadata in logical_grid_window_metadata(state["readings"], threshold=70.0, tolerance_seconds=logical_grid_tolerance):
                    if not metadata["input_eligible"] or metadata["label_status"] != "known":
                        continue
                    record = {
                        "sample_id": f"{patient_id}:{metadata['index_time']}:{metadata['horizon_minutes']}",
                        "patient_id": patient_id,
                        "fold_id": None,
                        "analysis_group": window_index_group,
                        **metadata,
                    }
                    index_handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
                    index_counts["records"] += 1
                    index_counts["positive_labels"] += int(metadata["label"] == 1)
            if rule_baseline:
                ordered_times = sorted(state["readings"])
                positions = {timestamp: position for position, timestamp in enumerate(ordered_times)}
                labels: list[int] = []
                scores: list[float] = []
                for metadata in logical_grid_window_metadata(state["readings"], threshold=70.0, tolerance_seconds=logical_grid_tolerance):
                    if not metadata["input_eligible"] or metadata["label_status"] != "known":
                        continue
                    current_time = datetime.fromisoformat(str(metadata["index_time"]))
                    previous_time = ordered_times[positions[current_time] - 1]
                    score = persistence_slope_score_from_values(
                        previous_time, state["readings"][previous_time], current_time, state["readings"][current_time], horizon_minutes=int(metadata["horizon_minutes"])
                    )
                    labels.append(int(metadata["label"])); scores.append(score)
                if labels:
                    rule_summaries.append({
                        "windows": len(labels), "positive_labels": sum(labels),
                        "average_precision": average_precision(labels, scores),
                        "squared_error_sum": sum((score - label) ** 2 for label, score in zip(labels, scores)),
                        "tp": sum(label == 1 and score == 1 for label, score in zip(labels, scores)),
                        "fp": sum(label == 0 and score == 1 for label, score in zip(labels, scores)),
                        "tn": sum(label == 0 and score == 0 for label, score in zip(labels, scores)),
                        "fn": sum(label == 1 and score == 0 for label, score in zip(labels, scores)),
                    })
    if index_handle is not None:
        index_handle.close()
    cadence: Counter[int] = Counter()
    for state in patients.values():
        cadence.update(state["cadence_seconds"])
        del state["readings"]
        del state["cadence_seconds"]
    return {"counts": dict(report), "patients": list(patients.values()), "temporal": temporal, "cadence": dict(cadence), "tolerances": tolerance_results, "logical": logical_results, "logical_60": logical_60_results, "episodes": episode_results, "private_rows": private_rows, "window_index": dict(index_counts), "rule_summaries": rule_summaries}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("release", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--partitions", type=int, default=64)
    parser.add_argument("--minimum-free-before-gib", type=float, default=20.0)
    parser.add_argument("--minimum-free-during-gib", type=float, default=10.0)
    parser.add_argument("--development-manifest", type=Path)
    parser.add_argument("--manifest-group", choices=("development", "holdout", "all_candidates"), default="development")
    parser.add_argument("--tolerances", type=int, nargs="+", default=[0, 1, 2])
    parser.add_argument("--skip-tolerance-comparison", action="store_true")
    parser.add_argument("--logical-grid-tolerance", type=int)
    parser.add_argument("--private-summary-output", type=Path)
    parser.add_argument("--window-index-directory", type=Path, help="private directory for gzip-compressed eligible/known window metadata partitions")
    parser.add_argument("--rule-baseline-output", type=Path, help="aggregate development-only persistence/slope reference result")
    args = parser.parse_args()
    free = shutil.disk_usage(args.output.parent).free
    if free < args.minimum_free_before_gib * 1024**3:
        raise RuntimeError("insufficient free space before partitioning")
    paths = sorted((args.release / "Data Tables").glob("LOOPDeviceCGM*.txt"))
    if args.skip_tolerance_comparison:
        args.tolerances = []
    selected_patients = None
    if args.development_manifest:
        manifest = json.loads(args.development_manifest.read_text(encoding="utf-8"))
        if args.manifest_group == "all_candidates":
            selected_patients = set(manifest["development_patients"]) | set(manifest["holdout_patients"])
        else:
            selected_patients = set(manifest[f"{args.manifest_group}_patients"])
    if args.window_index_directory and args.logical_grid_tolerance is None:
        parser.error("--window-index-directory requires --logical-grid-tolerance")
    if args.rule_baseline_output and args.logical_grid_tolerance is None:
        parser.error("--rule-baseline-output requires --logical-grid-tolerance")
    if args.window_index_directory:
        args.window_index_directory.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="loop-cgm-audit-", dir=args.output.parent) as temporary:
        directory = Path(temporary)
        raw_rows, partitions = partition(paths, directory, args.partitions)
        totals: Counter[str] = Counter()
        participant_summaries: list[dict[str, object]] = []
        temporal_summaries: list[dict[str, int]] = []
        cadence: Counter[int] = Counter()
        tolerance_summaries: dict[int, list[dict[str, int]]] = {tolerance: [] for tolerance in args.tolerances}
        logical_summaries: list[dict[str, int]] = []
        logical_60_summaries: list[dict[str, int]] = []
        episode_summaries: list[dict[str, int]] = []
        private_rows: list[dict[str, object]] = []
        window_index_totals: Counter[str] = Counter()
        rule_summaries: list[dict[str, float | int | None]] = []
        for number, partition_path in enumerate(partitions, start=1):
            if shutil.disk_usage(directory).free < args.minimum_free_during_gib * 1024**3:
                raise RuntimeError("free-space safety floor reached during audit")
            index_path = args.window_index_directory / f"loop-window-index-{number:02d}.jsonl.gz" if args.window_index_directory else None
            result = audit_partition(sorted_rows(partition_path), selected_patients=selected_patients, tolerances=tuple(args.tolerances), logical_grid_tolerance=args.logical_grid_tolerance, window_index_path=index_path, window_index_group=args.manifest_group if args.window_index_directory else None, rule_baseline=bool(args.rule_baseline_output))
            totals.update(result["counts"])
            participant_summaries.extend(result["patients"])
            temporal_summaries.extend(result["temporal"])
            cadence.update(result["cadence"])
            for tolerance, summaries in result["tolerances"].items():
                tolerance_summaries[tolerance].extend(summaries)
            logical_summaries.extend(result["logical"])
            logical_60_summaries.extend(result["logical_60"])
            episode_summaries.extend(result["episodes"])
            private_rows.extend(result["private_rows"])
            window_index_totals.update(result["window_index"])
            rule_summaries.extend(result["rule_summaries"])
            print(f"audited partition {number}/{args.partitions}", flush=True)
    counts = [item["count"] for item in participant_summaries]
    gaps = [item["largest_gap_seconds"] for item in participant_summaries]
    report = {
        "release": str(args.release),
        "audit_type": "participant-hashed and UTC-sorted CGM canonicalization audit",
        "identifiers_emitted": False,
        "partitions": args.partitions,
        "raw_rows_partitioned": raw_rows,
        "counts": dict(totals),
        "participants_with_usable_cgm": len(participant_summaries),
        "participants_with_complete_30m_future": sum(item["complete_future"] > 0 for item in temporal_summaries),
        "participants_with_input_eligible_30m_indices": sum(item["input_eligible"] > 0 for item in temporal_summaries),
        "participants_with_known_30m_labels": sum(item["known_labels"] > 0 for item in temporal_summaries),
        "participants_with_positive_30m_labels": sum(item["positive_labels"] > 0 for item in temporal_summaries),
        "temporal_30m_totals": dict(sum((Counter(item) for item in temporal_summaries), Counter())),
        "cadence_seconds_top": {str(seconds): count for seconds, count in cadence.most_common(12)},
        "selected_population_contiguous_cadence_tolerance_30m_totals": {
            str(tolerance): dict(sum((Counter(item) for item in summaries), Counter()))
            for tolerance, summaries in tolerance_summaries.items()
        } if selected_patients is not None else None,
        "selected_population_logical_grid_30m_totals": dict(sum((Counter(item) for item in logical_summaries), Counter())) if args.logical_grid_tolerance is not None else None,
        "selected_population_logical_grid_60m_totals": dict(sum((Counter(item) for item in logical_60_summaries), Counter())) if args.logical_grid_tolerance is not None else None,
        "selected_population_participants": len(private_rows) if args.logical_grid_tolerance is not None else None,
        "participants_with_logical_30m_input_eligible_indices": sum(item["input_eligible"] > 0 for item in logical_summaries) if args.logical_grid_tolerance is not None else None,
        "participants_with_logical_60m_input_eligible_indices": sum(item["input_eligible"] > 0 for item in logical_60_summaries) if args.logical_grid_tolerance is not None else None,
        "selected_population_episode_totals": dict(sum((Counter(item) for item in episode_summaries), Counter())) if args.logical_grid_tolerance is not None else None,
        "participants_with_confirmed_episode": sum(item["confirmed_episode_onsets"] > 0 for item in episode_summaries) if args.logical_grid_tolerance is not None else None,
        "usable_cgm_timestamps_per_participant": {"min": min(counts, default=0), "max": max(counts, default=0)},
        "largest_within_participant_gap_seconds": {"min": min(gaps, default=0), "max": max(gaps, default=0)},
        "policy": "Exact re-exports collapse to the lowest RecID. Calibration is excluded. Same patient/UTC timestamps with differing CGM values are flagged and excluded from primary windows.",
        "window_index": {"directory": str(args.window_index_directory) if args.window_index_directory else None, "compressed_partitions": args.partitions if args.window_index_directory else 0, **dict(window_index_totals)},
        "temporary_partitions_removed": True,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.rule_baseline_output:
        rule_counts = Counter()
        for summary in rule_summaries:
            rule_counts.update({key: int(summary[key]) for key in ("windows", "positive_labels", "tp", "fp", "tn", "fn")})
        ap_values = [float(summary["average_precision"]) for summary in rule_summaries if summary["average_precision"] is not None]
        baseline_report = {
            "model": "persistence_slope_rule", "population": args.manifest_group,
            "horizon_minutes": 30, "participants_with_positive_labels": len(ap_values),
            "participant_macro_ap": sum(ap_values) / len(ap_values) if ap_values else None,
            "brier_score": sum(float(summary["squared_error_sum"]) for summary in rule_summaries) / rule_counts["windows"] if rule_counts["windows"] else None,
            **dict(rule_counts), "identifiers_emitted": False,
            "policy": "Non-learned score projects the latest observed CGM slope across the 30-minute horizon. This development-only reference uses no holdout participants.",
        }
        args.rule_baseline_output.parent.mkdir(parents=True, exist_ok=True)
        args.rule_baseline_output.write_text(json.dumps(baseline_report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.private_summary_output:
        args.private_summary_output.parent.mkdir(parents=True, exist_ok=True)
        args.private_summary_output.write_text(json.dumps(private_rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
