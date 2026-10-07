#!/usr/bin/env python3
"""Audit as-of Loop event coverage for frozen CGM window-index partitions."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import shutil
import subprocess
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from t1d_tkg.event_alignment import aligned_event_counts


UTC_FORMAT = "%Y-%m-%d %H:%M:%S"
SPECS = {
    "basal": ("LOOPDeviceBasal*.txt", ["BasalType", "Duration", "ExpectedDuration", "Percnt", "Rate", "SuprBasalType", "SuprDuration", "SuprRate"]),
    "bolus": ("LOOPDeviceBolus.txt", ["BolusType", "Normal", "ExpectedNormal", "Extended", "ExpectedExtended", "Duration", "ExpectedDuration"]),
    "food": ("LOOPDeviceFood.txt", ["CarbsNet", "CarbUnits"]),
}


def bucket(patient: bytes, count: int) -> int:
    return int.from_bytes(hashlib.blake2b(patient, digest_size=8).digest(), "big") % count


def partition_events(paths: list[Path], fields: list[str], directory: Path, count: int, *, minimum_free_gib: float = 0.0) -> list[Path]:
    if minimum_free_gib and shutil.disk_usage(directory).free < minimum_free_gib * 1024**3:
        raise RuntimeError("free-space safety floor reached before partitioning")
    scanned = 0
    outputs = [directory / f"events-{number:02d}.psv" for number in range(1, count + 1)]
    handles = [path.open("wb") for path in outputs]
    try:
        for path in paths:
            with path.open("rb") as source:
                header = source.readline().decode("utf-8-sig", "replace").rstrip("\r\n").split("|")
                indexes = [header.index(field) for field in ["PtID", "RecID", "UTCDtTm", *fields]]
                for raw in source:
                    scanned += 1
                    if minimum_free_gib and scanned % 10000 == 0 and shutil.disk_usage(directory).free < minimum_free_gib * 1024**3:
                        raise RuntimeError("free-space safety floor reached during partitioning")
                    row = raw.rstrip(b"\r\n").split(b"|")
                    handles[bucket(row[indexes[0]].strip(), count)].write(b"|".join(row[index] for index in indexes) + b"\n")
    finally:
        for handle in handles:
            handle.close()
    return outputs


def sorted_events(path: Path, field_count: int) -> Path:
    output = path.with_suffix(".sorted")
    keys = ["-k1,1", "-k3,3", *[f"-k{column},{column}" for column in range(4, 4 + field_count)], "-k2,2n"]
    subprocess.run(["sort", "-S", "512M", "-t", "|", *keys, "-o", str(output), str(path)], check=True)
    path.unlink()
    return output


def index_windows(path: Path) -> dict[str, list[datetime]]:
    result: dict[str, list[datetime]] = defaultdict(list)
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        next(handle)
        for line in handle:
            record = json.loads(line)
            result[str(record["patient_id"])].append(datetime.fromisoformat(str(record["index_time"])))
    return result


def canonical_event_times(path: Path, field_count: int) -> dict[str, list[datetime]]:
    result: dict[str, list[datetime]] = defaultdict(list)
    previous_key: tuple[bytes, ...] | None = None
    with path.open("rb") as handle:
        for raw in handle:
            row = raw.rstrip(b"\n").split(b"|")
            key = (row[0], row[2], *row[3:3 + field_count])
            if key == previous_key:
                continue
            previous_key = key
            result[row[0].decode("ascii", "replace")].append(datetime.strptime(row[2].decode(), UTC_FORMAT).replace(tzinfo=timezone.utc))
    path.unlink()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("release", type=Path)
    parser.add_argument("modality", choices=sorted(SPECS))
    parser.add_argument("--window-index-directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--partitions", type=int, default=64)
    parser.add_argument("--lookback-minutes", type=int, default=120)
    parser.add_argument("--minimum-free-gib", type=float, default=15.0)
    args = parser.parse_args()
    if shutil.disk_usage(args.output.parent).free < args.minimum_free_gib * 1024**3:
        raise RuntimeError("insufficient free space before event alignment")
    pattern, fields = SPECS[args.modality]
    paths = sorted((args.release / "Data Tables").glob(pattern))
    if not paths:
        raise ValueError(f"no source tables found for {args.modality}")
    index_paths = sorted(args.window_index_directory.glob("*.jsonl.gz"))
    if len(index_paths) != args.partitions:
        raise ValueError("window-index partition count does not match --partitions")
    totals: Counter[str] = Counter()
    with tempfile.TemporaryDirectory(prefix=f"loop-{args.modality}-alignment-", dir=args.output.parent) as temporary:
        partitions = partition_events(paths, fields, Path(temporary), args.partitions)
        for number, event_path in enumerate(partitions, start=1):
            if shutil.disk_usage(args.output.parent).free < args.minimum_free_gib * 1024**3:
                raise RuntimeError("free-space safety floor reached during event alignment")
            windows = index_windows(index_paths[number - 1])
            events = canonical_event_times(sorted_events(event_path, len(fields)), len(fields))
            for patient, window_times in windows.items():
                counts = list(aligned_event_counts(window_times, events.get(patient, []), lookback_minutes=args.lookback_minutes))
                totals["windows"] += len(counts)
                totals["windows_with_one_or_more_events"] += sum(count > 0 for _, count in counts)
                totals["aligned_event_records"] += sum(count for _, count in counts)
            print(f"aligned {args.modality} partition {number}/{args.partitions}", flush=True)
    report = {
        "audit_type": "canonical auxiliary-event coverage in frozen eligible CGM windows",
        "release": str(args.release), "modality": args.modality, "lookback_minutes": args.lookback_minutes,
        "partitions": args.partitions, "identifiers_emitted": False,
        "windows": totals["windows"], "windows_with_one_or_more_events": totals["windows_with_one_or_more_events"],
        "aligned_event_records": totals["aligned_event_records"],
        "window_coverage_fraction": totals["windows_with_one_or_more_events"] / totals["windows"] if totals["windows"] else None,
        "policy": "Exact re-exports collapse to the lowest RecID-equivalent sorted record; differing same-time non-CGM records remain. Events are aligned only when occurrence time is in [index-120m, index].",
        "temporary_partitions_removed": True,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
