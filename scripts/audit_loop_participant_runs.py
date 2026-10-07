#!/usr/bin/env python3
"""Determine whether Loop tables can stream as participant-contiguous runs.

The report contains aggregate counts only.  It writes no transformed clinical
records, which lets it select a storage-safe duplicate-audit strategy.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


SPECS = {
    "cgm": "LOOPDeviceCGM*.txt",
    "basal": "LOOPDeviceBasal*.txt",
    "bolus": "LOOPDeviceBolus.txt",
    "food": "LOOPDeviceFood.txt",
    "exercise": "LOOPDeviceExercise.txt",
}


def scan(paths: list[Path]) -> dict[str, object]:
    rows = current_run = 0
    runs_by_patient: Counter[bytes] = Counter()
    largest_run_by_patient: Counter[bytes] = Counter()
    current_patient: bytes | None = None

    def close_run() -> None:
        nonlocal current_run
        if current_patient is not None:
            runs_by_patient[current_patient] += 1
            largest_run_by_patient[current_patient] = max(largest_run_by_patient[current_patient], current_run)
        current_run = 0

    for path in paths:
        with path.open("rb") as handle:
            header = handle.readline().decode("utf-8-sig", "replace").rstrip("\r\n").split("|")
            patient_index = header.index("PtID")
            for raw in handle:
                rows += 1
                patient = raw.rstrip(b"\r\n").split(b"|")[patient_index].strip()
                if patient != current_patient:
                    close_run()
                    current_patient = patient
                current_run += 1
        print(f"scanned {path}: {rows} cumulative rows", flush=True)
    close_run()
    histogram = Counter(runs_by_patient.values())
    return {
        "files": [str(path) for path in paths],
        "rows": rows,
        "participants": len(runs_by_patient),
        "participant_runs": sum(runs_by_patient.values()),
        "participants_in_multiple_source_runs": sum(count > 1 for count in runs_by_patient.values()),
        "maximum_runs_for_one_participant": max(runs_by_patient.values(), default=0),
        "maximum_rows_in_one_contiguous_run": max(largest_run_by_patient.values(), default=0),
        "run_count_histogram": {str(count): frequency for count, frequency in sorted(histogram.items())},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("release", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    tables = args.release / "Data Tables"
    report = {
        "release": str(args.release),
        "audit_type": "source-order participant-contiguity diagnostic",
        "identifiers_emitted": False,
        "purpose": "Choose streaming versus hashed-partition strategy; this is not a sorted duplicate audit.",
        "modalities": {name: scan(sorted(tables.glob(pattern))) for name, pattern in SPECS.items()},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
