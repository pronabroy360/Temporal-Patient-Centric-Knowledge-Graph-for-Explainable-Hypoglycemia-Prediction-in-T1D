#!/usr/bin/env python3
"""Estimate a minimal Loop hashed-partition footprint without writing partitions.

It streams every selected raw row once and counts the bytes of a pipe-delimited
projection containing only canonicalization inputs and provenance.  The report
contains aggregate byte totals and no participant identifiers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


SPECS = {
    "cgm": ("LOOPDeviceCGM*.txt", ["RecordType", "CGMVal", "Units"]),
    "basal": ("LOOPDeviceBasal*.txt", ["BasalType", "Duration", "ExpectedDuration", "Percnt", "Rate", "SuprBasalType", "SuprDuration", "SuprRate"]),
    "bolus": ("LOOPDeviceBolus.txt", ["BolusType", "Normal", "ExpectedNormal", "Extended", "ExpectedExtended", "Duration", "ExpectedDuration"]),
    "food": ("LOOPDeviceFood.txt", ["CarbsNet", "CarbUnits"]),
    "exercise": ("LOOPDeviceExercise.txt", ["ExerciseName", "DistanceValue", "DistanceUnits", "DurationValue", "DurationUnits", "EnergyValue", "EnergyUnits", "ReportedIntensity"]),
}
PROVENANCE = ["PtID", "RecID", "ParentLOOPDeviceUploadsID", "UTCDtTm"]


def bucket_for(patient: bytes, count: int) -> int:
    return int.from_bytes(hashlib.blake2b(patient, digest_size=8).digest(), "big") % count


def scan(paths: list[Path], key_fields: list[str], partitions: int) -> dict[str, object]:
    rows = projected_bytes = 0
    bucket_bytes: Counter[int] = Counter()
    for path in paths:
        with path.open("rb") as handle:
            header = handle.readline().decode("utf-8-sig", "replace").rstrip("\r\n").split("|")
            fields = [*PROVENANCE, *key_fields]
            indexes = [header.index(field) for field in fields]
            patient_index = indexes[0]
            for raw in handle:
                parts = raw.rstrip(b"\r\n").split(b"|")
                # One separator between every selected value, plus newline.
                size = sum(len(parts[index]) for index in indexes) + len(indexes)
                patient = parts[patient_index].strip()
                projected_bytes += size
                bucket_bytes[bucket_for(patient, partitions)] += size
                rows += 1
        print(f"scanned {path}: {rows} cumulative rows", flush=True)
    return {
        "files": [str(path) for path in paths],
        "rows": rows,
        "projected_bytes": projected_bytes,
        "largest_partition_bytes": max(bucket_bytes.values(), default=0),
        "nonempty_partitions": len(bucket_bytes),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("release", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--partitions", type=int, default=64)
    args = parser.parse_args()
    if args.partitions < 2:
        raise ValueError("at least two partitions are required")
    tables = args.release / "Data Tables"
    modalities = {
        name: scan(sorted(tables.glob(pattern)), fields, args.partitions)
        for name, (pattern, fields) in SPECS.items()
    }
    total = sum(item["projected_bytes"] for item in modalities.values())
    largest = max(item["largest_partition_bytes"] for item in modalities.values())
    report = {
        "release": str(args.release),
        "audit_type": "read-only minimal-column hashed-partition footprint estimate",
        "identifiers_emitted": False,
        "partition_count": args.partitions,
        "modalities": modalities,
        "total_projected_partition_bytes": total,
        "largest_single_modality_partition_bytes": largest,
        "interpretation": "Actual peak space also needs sort/index scratch and a safety margin; this estimate does not authorize materialization.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
