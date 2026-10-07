#!/usr/bin/env python3
"""One-fold, patient-disjoint Loop captured-event logistic pilot."""

from __future__ import annotations

import argparse
import math
import json
import shutil
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from audit_loop_partitioned_cgm import partition, sorted_rows
from audit_loop_window_event_alignment import SPECS, partition_events, sorted_events
from run_loop_cgm_logistic_pilot import iter_patient_readings
from t1d_tkg.baselines import persistence_slope_score_from_current_and_slope
from t1d_tkg.captured_events import FEATURE_NAMES, FEATURE_POLICY, iter_captured_event_features
from t1d_tkg.features import cgm_recent_features
from t1d_tkg.feature_cache import iter_partition_patients, load_metadata as load_cache_metadata
from t1d_tkg.logistic import fit_streaming_logistic
from t1d_tkg.manifest import load_manifest, manifest_checksum
from t1d_tkg.pilot_artifacts import PilotArtifacts, verify_windows
from t1d_tkg.metrics import METRIC_VERSION, average_precision
from t1d_tkg.temporal_eligibility import logical_grid_window_metadata


def number(value: bytes) -> float | None:
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except ValueError:
        return None


def canonical_records(path: Path, modality: str) -> dict[str, list[tuple[datetime, str, float | None]]]:
    """Collapse exact re-exports and retain distinct same-time event records."""
    fields = SPECS[modality][1]
    result: dict[str, list[tuple[datetime, str, float | None]]] = {}
    previous_key = None
    with path.open("rb") as handle:
        for raw in handle:
            row = raw.rstrip(b"\n").split(b"|")
            key = (row[0], row[2], *row[3:3 + len(fields)])
            if key == previous_key:
                continue
            previous_key = key
            patient = row[0].decode("ascii", "replace")
            timestamp = datetime.strptime(row[2].decode(), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            if modality == "basal":
                value = number(row[3 + fields.index("Rate")])
            elif modality == "bolus":
                value = number(row[3 + fields.index("Normal")])
                # Extended delivery totals are intentionally unavailable to this model.
            else:
                # The audited release uses grams except for five blank-unit rows.
                # Do not silently treat a future or unexpected carbohydrate unit
                # as grams.
                if row[3 + fields.index("CarbUnits")].strip().lower() != b"grams":
                    value = None
                else:
                    value = number(row[3 + fields.index("CarbsNet")])
            result.setdefault(patient, []).append((timestamp, modality, value))
    return result


def eligible_cgm_rows(readings: dict[datetime, float]):
    """Yield timestamped CGM features and labels under the frozen window rule."""
    ordered = sorted(readings)
    positions = {value: index for index, value in enumerate(ordered)}
    for metadata in logical_grid_window_metadata(readings, threshold=70.0, tolerance_seconds=1):
        if not metadata["input_eligible"] or metadata["label_status"] != "known":
            continue
        index_time = datetime.fromisoformat(str(metadata["index_time"]))
        previous_time = ordered[positions[index_time] - 1]
        yield (
            index_time,
            cgm_recent_features(previous_time, readings[previous_time], index_time, readings[index_time]),
            int(metadata["label"]),
        )


def join_event_rows(cgm_rows, records: list[tuple[datetime, str, float | None]]):
    """Join timestamped CGM rows to as-of event summaries."""
    cgm_rows = list(cgm_rows)
    event_rows = iter_captured_event_features((row[0] for row in cgm_rows), records)
    for (index_time, cgm_features, label), (event_time, event_features) in zip(cgm_rows, event_rows):
        if index_time != event_time:
            raise RuntimeError("event iterator lost CGM window ordering")
        yield index_time, cgm_features + event_features, label, cgm_features


def joined_patient_rows(readings: dict[datetime, float], records: list[tuple[datetime, str, float | None]]):
    """Join one patient's regenerated eligible CGM windows to event summaries."""
    yield from join_event_rows(eligible_cgm_rows(readings), records)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("release", type=Path)
    parser.add_argument("--model-manifest", type=Path, default=Path("private/loop_model_manifest.json"))
    parser.add_argument("--fold", default="outer-0")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--learning-rate", type=float, default=0.002)
    parser.add_argument("--partitions", type=int, default=64)
    parser.add_argument("--minimum-free-before-gib", type=float, default=20.0)
    parser.add_argument("--minimum-free-during-gib", type=float, default=10.0)
    parser.add_argument("--evaluate-development-test", action="store_true")
    parser.add_argument(
        "--evaluation-scope", choices=("validation", "development-test", "both"),
        default="validation", help="prediction group; use development-test only after configuration freeze",
    )
    parser.add_argument("--window-index-directory", type=Path, default=Path("private/loop_window_index"))
    parser.add_argument("--feature-cache-directory", type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Choose a new output path; historical reports must be preserved")
    if args.epochs < 1 or args.learning_rate <= 0 or args.partitions < 1:
        raise ValueError("epochs, learning rate and partitions must be positive")
    if args.evaluate_development_test and args.evaluation_scope != "validation":
        raise ValueError("use either legacy --evaluate-development-test or --evaluation-scope")
    evaluation_scope = "both" if args.evaluate_development_test else args.evaluation_scope
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(args.output.parent).free < args.minimum_free_before_gib * 1024**3:
        raise RuntimeError("insufficient free space before event logistic pilot")
    manifest = load_manifest(args.model_manifest)
    fold = next((item for item in manifest["folds"] if item["fold_id"] == args.fold), None)
    if fold is None:
        raise ValueError("requested fold is not in model manifest")
    groups = {"train": set(fold["train_patients"]), "validation": set(fold["validation_patients"]), "development_test": set(fold["test_patients"])}
    tables = args.release / "Data Tables"
    cgm_paths = sorted(tables.glob("LOOPDeviceCGM*.txt")) if args.feature_cache_directory is None else []
    event_paths = {modality: sorted(tables.glob(SPECS[modality][0])) for modality in ("basal", "bolus", "food")}
    if (args.feature_cache_directory is None and not cgm_paths) or any(not paths for paths in event_paths.values()):
        raise ValueError("required source tables are missing")
    cache_paths = []
    cache_metadata = None
    if args.feature_cache_directory is not None:
        cache_metadata = load_cache_metadata(
            args.feature_cache_directory, manifest_sha256=manifest_checksum(manifest)
        )
        cache_paths = sorted(args.feature_cache_directory.glob("features-*.tsv.gz"))
        if len(cache_paths) != args.partitions:
            raise ValueError("feature cache and requested partition counts differ")
    artifacts = PilotArtifacts(Path("private/pilot_runs") / args.output.stem, {
        "manifest_sha256": manifest_checksum(manifest), "arguments": {key: str(value) for key, value in vars(args).items()}})
    with tempfile.TemporaryDirectory(prefix="loop-event-logistic-", dir=args.output.parent) as temporary:
        directory = Path(temporary)
        raw_cgm = []
        if args.feature_cache_directory is None:
            cgm_directory = directory / "cgm"; cgm_directory.mkdir()
            _, raw_cgm = partition(cgm_paths, cgm_directory, args.partitions, minimum_free_gib=args.minimum_free_during_gib)
        raw_events = {}
        for modality, paths in event_paths.items():
            event_directory = directory / modality; event_directory.mkdir()
            raw_events[modality] = partition_events(paths, SPECS[modality][1], event_directory, args.partitions, minimum_free_gib=args.minimum_free_during_gib)
        sorted_cgm = []
        for path in raw_cgm:
            if shutil.disk_usage(directory).free < args.minimum_free_during_gib * 1024**3:
                raise RuntimeError("free-space safety floor reached while sorting CGM partitions")
            sorted_cgm.append(sorted_rows(path))
        sorted_events_by_modality = {}
        for modality, paths in raw_events.items():
            sorted_events_by_modality[modality] = []
            for path in paths:
                if shutil.disk_usage(directory).free < args.minimum_free_during_gib * 1024**3:
                    raise RuntimeError("free-space safety floor reached while sorting event partitions")
                sorted_events_by_modality[modality].append(sorted_events(path, len(SPECS[modality][1])))

        if cache_metadata is None:
            window_verification = verify_windows(args.window_index_directory, sorted_cgm, iter_patient_readings, set(manifest["patients"]))
        else:
            window_verification = cache_metadata["window_verification"]

        def events_for_partition(number_index):
            events = {}
            for modality in ("basal", "bolus", "food"):
                records_by_patient = canonical_records(sorted_events_by_modality[modality][number_index], modality)
                for patient, records in records_by_patient.items():
                    events.setdefault(patient, []).extend(records)
            return events

        def patient_rows_for_partition(number_index):
            events = events_for_partition(number_index)
            if cache_metadata is not None:
                for patient, rows in iter_partition_patients(cache_paths[number_index]):
                    cgm_rows = (
                        (datetime.fromisoformat(index_time), features, label)
                        for index_time, label, features in rows
                    )
                    yield patient, join_event_rows(cgm_rows, events.get(patient, []))
            else:
                for patient, readings in iter_patient_readings(sorted_cgm[number_index]):
                    yield patient, joined_patient_rows(readings, events.get(patient, []))

        def joined_rows(patients):
            for number_index in range(args.partitions):
                for patient, rows in patient_rows_for_partition(number_index):
                    if patient not in patients:
                        continue
                    for _, feature, label, _ in rows:
                        yield feature, label

        def training_rows():
            yield from joined_rows(groups["train"])

        model = fit_streaming_logistic(training_rows, epochs=args.epochs, learning_rate=args.learning_rate)
        artifacts.model(model)
        evaluation_groups = {
            "validation": ("validation",), "development-test": ("development_test",),
            "both": ("validation", "development_test"),
        }[evaluation_scope]
        outcomes = {name: Counter() for name in evaluation_groups}
        for group in evaluation_groups:
            for number_index in range(args.partitions):
                for patient, rows in patient_rows_for_partition(number_index):
                    if patient not in groups[group]:
                        continue
                    times: list[str] = []; labels: list[int] = []; scores: list[float] = []; rule_scores: list[float] = []
                    for index_time, feature, label, cgm_features in rows:
                        times.append(index_time.isoformat())
                        labels.append(label); scores.append(model.predict_proba([feature])[0]); rule_scores.append(persistence_slope_score_from_current_and_slope(cgm_features[0], cgm_features[1], horizon_minutes=30))
                    if labels:
                        artifacts.predictions(group, patient, times, labels, scores, rule_scores)
                        outcomes[group]["participants"] += 1; outcomes[group]["windows"] += len(labels); outcomes[group]["positive_labels"] += sum(labels)
                        for name, values in (("event_logistic", scores), ("rule", rule_scores)):
                            outcomes[group][f"{name}_squared_error_sum"] += sum((score - label) ** 2 for label, score in zip(labels, values))
                            ap = average_precision(labels, values)
                            if ap is not None:
                                outcomes[group][f"{name}_ap_sum"] += ap; outcomes[group][f"{name}_ap_count"] += 1
        for path in sorted_cgm:
            path.unlink()
    report_groups = {}
    for group, counts in outcomes.items():
        report_groups[group] = {"participants": counts["participants"], "windows": counts["windows"], "positive_labels": counts["positive_labels"], "event_summary_logistic": {"ap_defined_participants": counts["event_logistic_ap_count"], "participant_macro_ap": counts["event_logistic_ap_sum"] / counts["event_logistic_ap_count"] if counts["event_logistic_ap_count"] else None, "brier_score": counts["event_logistic_squared_error_sum"] / counts["windows"] if counts["windows"] else None}, "persistence_slope_rule": {"ap_defined_participants": counts["rule_ap_count"], "participant_macro_ap": counts["rule_ap_sum"] / counts["rule_ap_count"] if counts["rule_ap_count"] else None, "brier_score": counts["rule_squared_error_sum"] / counts["windows"] if counts["windows"] else None}}
    report = {
        "model": "event_summary_logistic",
        "fold": args.fold, "epochs": args.epochs, "learning_rate": args.learning_rate,
        "evaluation_scope": evaluation_scope,
        "metric_version": METRIC_VERSION, "manifest_sha256": manifest_checksum(manifest), "identifiers_emitted": False,
        "features": ["current_glucose_mg_dl", "recent_slope_mg_dl_per_5m"] + FEATURE_NAMES,
        "feature_policy": FEATURE_POLICY,
        "availability_policy": "retrospective occurrence-time replay; immediate availability assumed, not measured",
        "groups": report_groups,
        "policy": "Development-only captured-event summary pilot. Zero event features mean no retained source record, not verified clinical absence. Training excludes validation, internal development-test, and locked holdout participants.",
    }
    report["optimizer"] = {"l2": 1e-4, "positive_weight": 1.0, "order": "deterministic participant partitions", "learning_rate_schedule": "initial/sqrt(epoch+1)"}
    for group in report["groups"].values():
        prevalence = model.training_prevalence
        group["training_prevalence_reference"] = {
            "probability": prevalence,
            "brier_score": ((group["windows"]-group["positive_labels"])*prevalence**2 + group["positive_labels"]*(1-prevalence)**2)/group["windows"] if group["windows"] else None}
    report["window_verification"] = window_verification
    report["input_source"] = "protected_cgm_feature_cache_and_canonicalized_events" if cache_metadata is not None else "canonicalized_raw_cgm_and_events"
    report["artifacts"] = str(artifacts.path)
    artifacts.complete(report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
