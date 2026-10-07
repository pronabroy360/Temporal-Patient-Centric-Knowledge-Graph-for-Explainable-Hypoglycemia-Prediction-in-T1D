#!/usr/bin/env python3
"""Storage-bounded canonical duplicate audit for Loop non-CGM event tables."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from collections import Counter
from pathlib import Path


SPECS = {
    "basal": ("LOOPDeviceBasal*.txt", ["BasalType", "Duration", "ExpectedDuration", "Percnt", "Rate", "SuprBasalType", "SuprDuration", "SuprRate"]),
    "bolus": ("LOOPDeviceBolus.txt", ["BolusType", "Normal", "ExpectedNormal", "Extended", "ExpectedExtended", "Duration", "ExpectedDuration"]),
    "food": ("LOOPDeviceFood.txt", ["CarbsNet", "CarbUnits"]),
    "exercise": ("LOOPDeviceExercise.txt", ["ExerciseName", "DistanceValue", "DistanceUnits", "DurationValue", "DurationUnits", "EnergyValue", "EnergyUnits", "ReportedIntensity"]),
}
BASE_FIELDS = ["PtID", "RecID", "ParentLOOPDeviceUploadsID", "UTCDtTm"]


def _bucket(patient: bytes, count: int) -> int:
    return int.from_bytes(hashlib.blake2b(patient, digest_size=8).digest(), "big") % count


def _partition(paths: list[Path], fields: list[str], directory: Path, count: int) -> tuple[int, list[Path]]:
    outputs = [directory / f"part-{number:02d}.psv" for number in range(count)]
    handles = [path.open("wb") for path in outputs]
    rows = 0
    try:
        for path in paths:
            with path.open("rb") as source:
                header = source.readline().decode("utf-8-sig", "replace").rstrip("\r\n").split("|")
                indexes = [header.index(field) for field in [*BASE_FIELDS, *fields]]
                for raw in source:
                    row = raw.rstrip(b"\r\n").split(b"|")
                    handles[_bucket(row[indexes[0]].strip(), count)].write(b"|".join(row[index] for index in indexes) + b"\n")
                    rows += 1
            print(f"partitioned {path}: {rows} cumulative rows", flush=True)
    finally:
        for handle in handles:
            handle.close()
    return rows, outputs


def _sorted(path: Path, key_field_count: int) -> Path:
    output = path.with_suffix(".sorted")
    keys = ["-k1,1", "-k4,4", *[f"-k{column},{column}" for column in range(5, 5 + key_field_count)], "-k2,2n"]
    subprocess.run(["sort", "-S", "512M", "-t", "|", *keys, "-o", str(output), str(path)], check=True)
    path.unlink()
    return output


def _audit(path: Path) -> Counter[str]:
    counts: Counter[str] = Counter()
    exact_key = timestamp_key = None
    exact_size = distinct_at_timestamp = 0

    def close_timestamp() -> None:
        if timestamp_key is not None and distinct_at_timestamp > 1:
            counts["conflicting_same_time_timestamps"] += 1

    def close_exact() -> None:
        nonlocal timestamp_key, distinct_at_timestamp
        if exact_key is None:
            return
        counts["canonical_rows"] += 1
        counts["exact_duplicates_removed"] += exact_size - 1
        current_timestamp = exact_key[:2]
        if timestamp_key is not None and current_timestamp != timestamp_key:
            close_timestamp()
            distinct_at_timestamp = 0
        timestamp_key = current_timestamp
        distinct_at_timestamp += 1

    with path.open("rb") as handle:
        for raw in handle:
            row = raw.rstrip(b"\n").split(b"|")
            counts["raw_rows"] += 1
            current_key = (row[0], row[3], *row[4:])
            if exact_key is not None and current_key != exact_key:
                close_exact()
                exact_size = 0
            exact_key = current_key
            exact_size += 1
        close_exact()
        close_timestamp()
    path.unlink()
    return counts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("release", type=Path)
    parser.add_argument("modality", choices=sorted(SPECS))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--partitions", type=int, default=64)
    parser.add_argument("--minimum-free-gib", type=float, default=15.0)
    args = parser.parse_args()
    if shutil.disk_usage(args.output.parent).free < args.minimum_free_gib * 1024**3:
        raise RuntimeError("insufficient free space before partitioning")
    pattern, key_fields = SPECS[args.modality]
    paths = sorted((args.release / "Data Tables").glob(pattern))
    with tempfile.TemporaryDirectory(prefix=f"loop-{args.modality}-audit-", dir=args.output.parent) as temporary:
        raw_rows, partitions = _partition(paths, key_fields, Path(temporary), args.partitions)
        totals: Counter[str] = Counter()
        for index, partition in enumerate(partitions, start=1):
            if shutil.disk_usage(args.output.parent).free < args.minimum_free_gib * 1024**3:
                raise RuntimeError("free-space safety floor reached during audit")
            totals.update(_audit(_sorted(partition, len(key_fields))))
            print(f"audited {args.modality} partition {index}/{args.partitions}", flush=True)
    report = {
        "release": str(args.release), "modality": args.modality,
        "audit_type": "participant-hashed and UTC-sorted event canonicalization audit",
        "identifiers_emitted": False, "partitions": args.partitions,
        "raw_rows_partitioned": raw_rows, "counts": dict(totals),
        "policy": "Collapse exact re-exports to the lowest RecID; preserve all differing same-time non-CGM events.",
        "temporary_partitions_removed": True,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
