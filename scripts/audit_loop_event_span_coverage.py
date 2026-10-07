#!/usr/bin/env python3
"""Count raw Loop auxiliary events within protected CGM observation spans."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import median


UTC_FORMAT = "%Y-%m-%d %H:%M:%S"
SPECS = {
    "basal": ("LOOPDeviceBasal*.txt", None),
    "bolus": ("LOOPDeviceBolus.txt", None),
    "food": ("LOOPDeviceFood.txt", "CarbsNet"),
}


def parse(value: bytes) -> datetime | None:
    try:
        return datetime.strptime(value.decode(), UTC_FORMAT).replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("release", type=Path)
    parser.add_argument("--cgm-summary", type=Path, required=True)
    parser.add_argument("--private-output", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = json.loads(args.cgm_summary.read_text(encoding="utf-8"))
    spans = {row["patient_id"]: (datetime.fromisoformat(row["first_utc"]).replace(tzinfo=timezone.utc), datetime.fromisoformat(row["last_utc"]).replace(tzinfo=timezone.utc)) for row in rows}
    counts = {patient: Counter() for patient in spans}
    malformed = Counter()
    tables = args.release / "Data Tables"
    for modality, (pattern, required) in SPECS.items():
        for path in sorted(tables.glob(pattern)):
            with path.open("rb") as handle:
                header = handle.readline().decode("utf-8-sig", "replace").rstrip("\r\n").split("|")
                patient_index, utc_index = header.index("PtID"), header.index("UTCDtTm")
                required_index = header.index(required) if required else None
                for line in handle:
                    fields = line.rstrip(b"\r\n").split(b"|")
                    patient = fields[patient_index].decode("ascii", "replace").strip()
                    if patient not in spans or (required_index is not None and not fields[required_index].strip()):
                        continue
                    timestamp = parse(fields[utc_index].strip())
                    if timestamp is None:
                        malformed[modality] += 1
                    elif spans[patient][0] <= timestamp <= spans[patient][1]:
                        counts[patient][modality] += 1
            print(f"scanned {path}", flush=True)
    private = [{"patient_id": patient, **dict(counts[patient])} for patient in sorted(counts)]
    args.private_output.parent.mkdir(parents=True, exist_ok=True)
    args.private_output.write_text(json.dumps(private, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    aggregate = {"audit_type": "raw auxiliary-event counts within CGM observation spans", "identifiers_emitted": False, "participants": len(private), "malformed_utc_rows": dict(malformed), "modalities": {}}
    for modality in SPECS:
        values = [row.get(modality, 0) for row in private]
        aggregate["modalities"][modality] = {"participants_with_one_or_more": sum(value > 0 for value in values), "min": min(values), "median": median(values), "max": max(values), "raw_records_within_cgm_span": sum(values)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(aggregate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
