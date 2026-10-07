#!/usr/bin/env python3
"""Validate Loop device-event links to Tidepool upload records.

This audit intentionally does not claim that an upload time is a first-usable
time. It establishes the prerequisite linkage and timing diagnostics needed
before that stronger interpretation can be considered.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from statistics import median


ISO_SECOND = re.compile(rb"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")


def parse_time(raw: bytes) -> datetime | None:
    raw = raw.strip()
    if not raw:
        return None
    try:
        return datetime.strptime(raw.decode("ascii"), "%Y-%m-%d %H:%M:%S")
    except (UnicodeDecodeError, ValueError):
        return None


def quantiles(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"min": None, "median": None, "p95": None, "max": None}
    ordered = sorted(values)
    return {
        "min": ordered[0],
        "median": median(ordered),
        "p95": ordered[round((len(ordered) - 1) * 0.95)],
        "max": ordered[-1],
    }


def load_uploads(path: Path) -> tuple[dict[bytes, bytes], dict[str, object]]:
    uploads: dict[bytes, bytes] = {}
    duplicate_ids = missing_upload_utc = malformed_upload_utc = 0
    with path.open("rb") as handle:
        header = handle.readline().decode("utf-8-sig").rstrip("\r\n").split("|")
        rec_i = header.index("RecID")
        utc_i = header.index("UploadUTCDtTm")
        rows = 0
        for raw in handle:
            rows += 1
            parts = raw.rstrip(b"\r\n").split(b"|")
            rec_id = parts[rec_i].strip()
            utc = parts[utc_i].strip()
            if rec_id in uploads:
                duplicate_ids += 1
            uploads[rec_id] = utc
            if not utc:
                missing_upload_utc += 1
            elif not ISO_SECOND.match(utc):
                malformed_upload_utc += 1
    return uploads, {
        "rows": rows,
        "unique_upload_ids": len(uploads),
        "duplicate_upload_ids": duplicate_ids,
        "missing_upload_utc": missing_upload_utc,
        "malformed_upload_utc": malformed_upload_utc,
    }


def scan_events(paths: list[Path], uploads: dict[bytes, bytes]) -> dict[str, object]:
    rows = missing_parent = unresolved = upload_time_missing = event_time_bad = upload_before_event = 0
    sampled_lags_hours: list[float] = []
    referenced_parent_counts: Counter[bytes] = Counter()
    resolved_parent_ids: set[bytes] = set()
    valid_upload_parent_ids: set[bytes] = set()
    for path in paths:
        with path.open("rb") as handle:
            header = handle.readline().decode("utf-8-sig").rstrip("\r\n").split("|")
            parent_i = header.index("ParentLOOPDeviceUploadsID")
            utc_i = header.index("UTCDtTm")
            rec_i = header.index("RecID")
            for raw in handle:
                rows += 1
                parts = raw.rstrip(b"\r\n").split(b"|")
                parent = parts[parent_i].strip()
                if not parent:
                    missing_parent += 1
                    continue
                referenced_parent_counts[parent] += 1
                upload = uploads.get(parent)
                if upload is None:
                    unresolved += 1
                    continue
                resolved_parent_ids.add(parent)
                event_raw = parts[utc_i].strip()
                if not ISO_SECOND.match(event_raw):
                    event_time_bad += 1
                    continue
                if not ISO_SECOND.match(upload):
                    upload_time_missing += 1
                    continue
                valid_upload_parent_ids.add(parent)
                if upload < event_raw:
                    upload_before_event += 1
                # Deterministic 0.1% sample avoids retaining millions of lags.
                try:
                    take_sample = int(parts[rec_i]) % 1000 == 0
                except ValueError:
                    take_sample = False
                if take_sample:
                    event_time = parse_time(event_raw)
                    upload_time = parse_time(upload)
                    assert event_time is not None and upload_time is not None
                    sampled_lags_hours.append((upload_time - event_time).total_seconds() / 3600)
        print(f"scanned {path}: {rows} cumulative rows", flush=True)
    return {
        "files": [str(path) for path in paths],
        "rows": rows,
        "missing_parent_upload_id": missing_parent,
        "unresolved_parent_upload_id": unresolved,
        "resolved_parent_upload_id": rows - missing_parent - unresolved,
        "referenced_parent_ids": len(referenced_parent_counts),
        "referenced_parents_linked_to_multiple_event_rows": sum(count > 1 for count in referenced_parent_counts.values()),
        "resolved_parent_ids": len(resolved_parent_ids),
        "resolved_parent_ids_with_valid_upload_utc": len(valid_upload_parent_ids),
        "event_timestamp_invalid": event_time_bad,
        "parent_upload_timestamp_missing_or_invalid": upload_time_missing,
        "upload_before_event": upload_before_event,
        "valid_upload_utc_not_before_event": rows - missing_parent - unresolved - upload_time_missing - upload_before_event,
        "lag_hours_sample_n": len(sampled_lags_hours),
        "lag_hours_sample": quantiles(sampled_lags_hours),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("release", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    tables = args.release / "Data Tables"
    uploads, upload_report = load_uploads(tables / "LOOPDeviceUploads.txt")
    groups = {
        "cgm": sorted(tables.glob("LOOPDeviceCGM*.txt")),
        "basal": sorted(tables.glob("LOOPDeviceBasal*.txt")),
        "bolus": [tables / "LOOPDeviceBolus.txt"],
        "food": [tables / "LOOPDeviceFood.txt"],
        "exercise": [tables / "LOOPDeviceExercise.txt"],
        "wizard": [tables / "LOOPDeviceWizard.txt"],
    }
    report = {
        "release": str(args.release),
        "upload_table": upload_report,
        "modalities": {name: scan_events(paths, uploads) for name, paths in groups.items()},
        "interpretation_guard": "A resolved upload timestamp establishes provenance and a candidate observed-availability proxy only. It is not called first usable until duplicate/version and coverage checks are completed.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
