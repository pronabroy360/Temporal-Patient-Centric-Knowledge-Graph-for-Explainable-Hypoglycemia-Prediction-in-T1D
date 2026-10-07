#!/usr/bin/env python3
"""Profile same-timestamp Loop records without deduplicating them.

The profile only describes source-adjacent records. Final canonicalization must
sort/partition by participant and time, then apply the documented key rules.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SPECS = {
    "cgm": ("LOOPDeviceCGM*.txt", ["RecordType", "CGMVal", "Units"]),
    "basal": ("LOOPDeviceBasal*.txt", ["BasalType", "Duration", "ExpectedDuration", "Percnt", "Rate", "SuprBasalType", "SuprDuration", "SuprRate"]),
    "bolus": ("LOOPDeviceBolus.txt", ["BolusType", "Normal", "ExpectedNormal", "Extended", "ExpectedExtended", "Duration", "ExpectedDuration"]),
    "food": ("LOOPDeviceFood.txt", ["CarbsNet", "CarbUnits"]),
    "exercise": ("LOOPDeviceExercise.txt", ["ExerciseName", "DistanceValue", "DistanceUnits", "DurationValue", "DurationUnits", "EnergyValue", "EnergyUnits", "ReportedIntensity"]),
}


def profile(paths: list[Path], fields: list[str]) -> dict[str, object]:
    rows = same_time = exact = conflict = 0
    conflict_fields = {field: 0 for field in fields}
    last = None
    for path in paths:
        with path.open("rb") as handle:
            header = handle.readline().decode("utf-8-sig").rstrip("\r\n").split("|")
            indexes = {field: header.index(field) for field in ["PtID", "UTCDtTm", *fields]}
            for raw in handle:
                rows += 1
                parts = raw.rstrip(b"\r\n").split(b"|")
                current = (
                    parts[indexes["PtID"]],
                    parts[indexes["UTCDtTm"]],
                    tuple(parts[indexes[field]] for field in fields),
                )
                if last is not None and current[:2] == last[:2]:
                    same_time += 1
                    if current[2] == last[2]:
                        exact += 1
                    else:
                        conflict += 1
                        for position, field in enumerate(fields):
                            if current[2][position] != last[2][position]:
                                conflict_fields[field] += 1
                last = current
        print(f"scanned {path}: {rows} cumulative rows", flush=True)
    return {
        "files": [str(path) for path in paths],
        "rows": rows,
        "source_adjacent_same_participant_timestamp": same_time,
        "source_adjacent_exact_key_repetitions": exact,
        "source_adjacent_conflicting_records": conflict,
        "conflicting_field_counts": conflict_fields,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("release", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    tables = args.release / "Data Tables"
    report = {
        "release": str(args.release),
        "scope": "source-adjacent duplicate profile; no records removed",
        "modalities": {},
        "limitation": "Nonadjacent duplicate records are not counted. Use this profile only to design, not validate, canonicalization keys.",
    }
    for modality, (pattern, fields) in SPECS.items():
        paths = sorted(tables.glob(pattern))
        report["modalities"][modality] = profile(paths, fields)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
