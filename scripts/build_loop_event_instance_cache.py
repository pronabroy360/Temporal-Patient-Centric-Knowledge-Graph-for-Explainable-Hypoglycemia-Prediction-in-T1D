#!/usr/bin/env python3
"""Build a protected canonical record-level Loop event cache for development."""

from __future__ import annotations

import argparse
import json
import math
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from audit_loop_window_event_alignment import SPECS, partition_events, sorted_events
from t1d_tkg.event_cache import EVENT_CACHE_VERSION, MODELED_MODALITIES, protected_event_id, write_partition
from t1d_tkg.manifest import load_manifest, manifest_checksum
from t1d_tkg.source_inventory import require_source_inventory, source_fingerprints


UTC_FORMAT = "%Y-%m-%d %H:%M:%S"


def finite_number(value: str) -> float | None:
    try:
        number = float(value)
    except ValueError:
        return None
    return number if math.isfinite(number) else None


def model_fields(modality: str, source_fields: dict[str, str]) -> tuple[str, float | None, str, bool]:
    """Return subtype, permitted model value, unit and known-value state."""
    if modality == "basal":
        value = finite_number(source_fields["Rate"])
        return source_fields["BasalType"], value, "U/hour", value is not None
    if modality == "bolus":
        # Extended delivery is retained in source_fields but excluded from the
        # initial predictive contract until occurrence-time semantics are known.
        value = finite_number(source_fields["Normal"])
        return source_fields["BolusType"], value, "U", value is not None
    unit = source_fields["CarbUnits"].strip()
    value = finite_number(source_fields["CarbsNet"])
    allowed = unit.lower() == "grams" and value is not None
    return "reported_meal", value if allowed else None, unit, allowed


def canonical_records(path: Path, modality: str):
    """Yield exact-repeat-collapsed records annotated within a source timestamp."""
    fields = SPECS[modality][1]
    exact_key = None
    exact_rows: list[list[bytes]] = []
    time_key = None
    time_records: list[dict[str, object]] = []

    def flush_time():
        nonlocal time_records
        if not time_records:
            return []
        variant_count = len(time_records)
        for record in time_records:
            record["same_time_variant_count"] = variant_count
        output = time_records
        time_records = []
        return output

    def finish_exact():
        nonlocal exact_rows, time_key
        if not exact_rows:
            return []
        representative = exact_rows[0]
        patient = representative[0].decode("ascii", "replace")
        occurrence = datetime.strptime(representative[2].decode(), UTC_FORMAT).replace(tzinfo=timezone.utc)
        source_fields = {
            field: representative[3 + index].decode("utf-8", "replace")
            for index, field in enumerate(fields)
        }
        subtype, model_value, unit, known = model_fields(modality, source_fields)
        record = {
            "event_id": protected_event_id(patient, modality, representative[1].decode("ascii", "replace")),
            "patient_id": patient,
            "occurrence_time": occurrence.isoformat(),
            "modality": modality,
            "subtype": subtype,
            "model_value": model_value,
            "model_value_unit": unit,
            "model_value_known": known,
            "source_fields": source_fields,
            "exact_duplicate_count": len(exact_rows) - 1,
        }
        key = (patient, occurrence)
        output = []
        if time_key is not None and key != time_key:
            output = flush_time()
        time_key = key
        time_records.append(record)
        exact_rows = []
        return output

    with path.open("rb") as handle:
        for raw in handle:
            row = raw.rstrip(b"\n").split(b"|")
            key = (row[0], row[2], *row[3 : 3 + len(fields)])
            if exact_key is not None and key != exact_key:
                yield from finish_exact()
            exact_key = key
            exact_rows.append(row)
    yield from finish_exact()
    yield from flush_time()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("release", type=Path)
    parser.add_argument("--model-manifest", type=Path, default=Path("private/loop_model_manifest.json"))
    parser.add_argument("--cgm-cache-directory", type=Path, default=Path("private/loop_cgm_feature_cache"))
    parser.add_argument("--output-directory", type=Path, default=Path("private/loop_event_instance_cache"))
    parser.add_argument("--summary-output", type=Path, default=Path("audit/loop_event_instance_cache.json"))
    parser.add_argument("--partitions", type=int, default=64)
    parser.add_argument("--source-inventory", type=Path, help="JSON modality-to-filename lists for an explicitly documented alternate export; defaults to the complete 2023-01-31 Loop export")
    parser.add_argument("--minimum-free-before-gib", type=float, default=20.0)
    parser.add_argument("--minimum-free-during-gib", type=float, default=10.0)
    args = parser.parse_args()
    if args.output_directory.exists() or args.summary_output.exists():
        raise FileExistsError("event-cache and summary outputs must be new paths")
    if args.partitions < 1:
        raise ValueError("partitions must be positive")
    manifest = load_manifest(args.model_manifest)
    cgm_metadata = json.loads((args.cgm_cache_directory / "metadata.json").read_text(encoding="utf-8"))
    if cgm_metadata.get("manifest_sha256") != manifest_checksum(manifest):
        raise ValueError("CGM cache was built for a different model manifest")
    if int(cgm_metadata.get("partitions", 0)) != args.partitions:
        raise ValueError("CGM cache and requested partition counts differ")
    tables = args.release / "Data Tables"
    source_paths = {modality: sorted(tables.glob(SPECS[modality][0])) for modality in MODELED_MODALITIES}
    if any(not paths for paths in source_paths.values()):
        raise ValueError("required Loop event source tables are missing")
    expected_inventory = json.loads(args.source_inventory.read_text()) if args.source_inventory else None
    require_source_inventory(tables, source_paths, expected_inventory)
    if shutil.disk_usage(args.output_directory.parent).free < args.minimum_free_before_gib * 1024**3:
        raise RuntimeError("insufficient free space before event-cache build")
    development = set(manifest["patients"])
    source_identity = source_fingerprints([path for paths in source_paths.values() for path in paths])
    args.output_directory.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="loop-event-cache-build-", dir=args.output_directory.parent) as temporary:
        workspace = Path(temporary)
        destination = workspace / "cache"
        destination.mkdir()
        sorted_by_modality = {}
        for modality, paths in source_paths.items():
            partition_directory = workspace / modality
            partition_directory.mkdir()
            raw_paths = partition_events(
                paths, SPECS[modality][1], partition_directory, args.partitions,
                minimum_free_gib=args.minimum_free_during_gib,
            )
            sorted_paths = []
            for raw_path in raw_paths:
                if shutil.disk_usage(workspace).free < args.minimum_free_during_gib * 1024**3:
                    raise RuntimeError("free-space safety floor reached while sorting event partitions")
                sorted_paths.append(sorted_events(raw_path, len(SPECS[modality][1])))
            sorted_by_modality[modality] = sorted_paths

        summaries = []
        for modality in MODELED_MODALITIES:
            for number, sorted_path in enumerate(sorted_by_modality[modality]):
                def records():
                    for record in canonical_records(sorted_path, modality):
                        if record["patient_id"] in development:
                            yield record

                summaries.append(write_partition(destination / f"events-{modality}-{number:02d}.jsonl.gz", modality, records()))
        metadata = {
            "cache_version": EVENT_CACHE_VERSION,
            "modalities": list(MODELED_MODALITIES),
            "manifest_sha256": manifest_checksum(manifest),
            "cgm_window_identity_sha256": cgm_metadata["window_verification"]["window_identity_sha256"],
            "development_participants": len(development),
            "partitions": args.partitions,
            "files": [item["file"] for item in summaries],
            "summaries": summaries,
            "canonical_events": sum(int(item["canonical_events"]) for item in summaries),
            "exact_duplicates_removed": sum(int(item["exact_duplicates_removed"]) for item in summaries),
            "known_model_values": sum(int(item["known_model_values"]) for item in summaries),
            "unknown_model_values": sum(int(item["unknown_model_values"]) for item in summaries),
            "same_time_variant_events": sum(int(item["same_time_variant_events"]) for item in summaries),
            "identifiers_emitted_publicly": False,
            "source_inventory": source_identity,
        }
        (destination / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        destination.rename(args.output_directory)
    public = {key: value for key, value in metadata.items() if key not in {"files", "summaries"}}
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(json.dumps(public, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(public, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
