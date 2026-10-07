#!/usr/bin/env python3
"""Audit the public AIDE T1D release without constructing model events.

The release contains millions of pipe-delimited rows.  This streaming audit
reports cohort size, CGM coverage, value/clock anomalies and treatment-period
metadata while avoiding a full in-memory load.  It intentionally does not
infer insulin delivery, meals, activity or transaction times from CRF tables.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from statistics import median


MONTHS = {name: number for number, name in enumerate(
    ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"), 1
)}


def parse_cgm_time(raw: str) -> datetime:
    """Parse AIDE's de-identified ``DDMONYYYY:HH:MM:SS`` timestamps."""

    date, clock = raw.strip().split(":", 1)
    day = int(date[:2])
    month = MONTHS[date[2:5].upper()]
    year = int(date[5:])
    hour, minute, second = (int(part) for part in clock.split(":"))
    return datetime(year, month, day, hour, minute, second)


def summarize(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"min": None, "median": None, "max": None}
    return {"min": min(values), "median": median(values), "max": max(values)}


def audit_table(path: Path, *, extended: bool = False) -> dict[str, object]:
    participants: set[str] = set()
    rows_by_patient: Counter[str] = Counter()
    dates_by_patient: defaultdict[str, set[str]] = defaultdict(set)
    last_time: dict[str, datetime] = {}
    last_patient: str | None = None
    patient_blocks = 0
    non_monotonic = 0
    duplicate_adjacent = 0
    gap_minutes: list[float] = []
    cadence = Counter()
    values: list[float] = []
    missing_values = 0
    timestamp_parse_errors = 0
    invalid_values = 0
    below70 = below54 = 0
    categories: dict[str, Counter[str]] = {
        "period": Counter(), "weeks": Counter(), "treatment": Counter(), "nightFlg": Counter()
    }
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter="|")
        for row in reader:
            patient = (row.get("PtID") or "").strip()
            participants.add(patient)
            rows_by_patient[patient] += 1
            if patient != last_patient:
                patient_blocks += 1
                last_patient = patient
            raw_time = (row.get("dataDtTm") or "").strip()
            if not raw_time:
                timestamp_parse_errors += 1
                continue
            try:
                current = parse_cgm_time(raw_time)
            except (KeyError, ValueError):
                timestamp_parse_errors += 1
                continue
            dates_by_patient[patient].add(current.date().isoformat())
            previous = last_time.get(patient)
            if previous is not None:
                delta = (current - previous).total_seconds() / 60
                if delta < 0:
                    non_monotonic += 1
                elif delta == 0:
                    duplicate_adjacent += 1
                else:
                    gap_minutes.append(delta)
                    cadence[round(delta, 6)] += 1
            last_time[patient] = current
            for field in categories:
                if row.get(field) is not None:
                    categories[field][row[field]] += 1
            raw_value = (row.get("glucValue") or "").strip()
            if not raw_value:
                missing_values += 1
                continue
            try:
                value = float(raw_value)
            except ValueError:
                invalid_values += 1
                continue
            values.append(value)
            below70 += value < 70
            below54 += value < 54

    span_days: list[float] = []
    # The full timestamp span is not retained per patient above; row counts and
    # unique observed dates are sufficient for the first access gate.  The
    # source dates are de-identified, so no calendar interpretation is made.
    for patient in participants:
        span_days.append(float(len(dates_by_patient[patient])))
    return {
        "file": str(path),
        "rows": sum(rows_by_patient.values()),
        "participants": len(participants),
        "patient_blocks": patient_blocks,
        "patient_blocks_equal_participants": patient_blocks == len(participants),
        "rows_per_participant": summarize([float(value) for value in rows_by_patient.values()]),
        "observed_calendar_dates_per_participant": summarize(span_days),
        "timestamp_parse_errors": timestamp_parse_errors,
        "non_monotonic_adjacent_rows": non_monotonic,
        "duplicate_adjacent_timestamps": duplicate_adjacent,
        "positive_time_deltas_minutes": summarize(gap_minutes),
        "cadence_minutes_top": dict(cadence.most_common(12)),
        "glucose_missing_rows": missing_values,
        "glucose_invalid_rows": invalid_values,
        "glucose_summary_mg_dl": summarize(values),
        "glucose_below_70_rows": below70,
        "glucose_below_54_rows": below54,
        "categories": {field: dict(counter.most_common()) for field, counter in categories.items()},
        "notes": [
            "Dates are de-identified and treated as within-participant chronology only.",
            "No timezone or first-usable/arrival timestamp is inferred.",
            "Rows are descriptive; no hypoglycemia labels or episode claims are frozen by this audit.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("release", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    tables = args.release / "Data Tables"
    required = ["PtRoster.txt", "cgmAnalysis.txt", "cgmAnalysisExt.txt", "AIDEDeviceCGM.txt", "AIDETandemCGMDATAGXB.txt", "AIDEInsulin.txt"]
    missing = [name for name in required if not (tables / name).is_file()]
    report: dict[str, object] = {
        "release": str(args.release),
        "required_files_present": not missing,
        "missing_required_files": missing,
        "roster_rows": None,
        "roster_participants": None,
        "roster_eligible_values": {},
        "roster_status_values": {},
        "tables": {},
        "interpretation": {
            "core_event_graph_ready": False,
            "reason": "Release inventory contains CGM and participant-level insulin inventory, but no timestamped insulin delivery, meal or activity event table was identified.",
            "recommended_role": "CGM benchmark, treatment-period covariate study, or external validation after a release-specific protocol; not the sole dataset for the core clinical-event relation claim.",
        },
    }
    roster = tables / "PtRoster.txt"
    with roster.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter="|")
        rows = list(reader)
    report["roster_rows"] = len(rows)
    report["roster_participants"] = len({row.get("PtID", "") for row in rows})
    for field in ("Eligible", "PtStatus", "TrtGroup"):
        report[f"roster_{field.lower()}_values"] = dict(Counter(row.get(field, "") for row in rows))
    for name in ("cgmAnalysis.txt", "cgmAnalysisExt.txt"):
        report["tables"][name] = audit_table(tables / name)
    report["source_table_inventory"] = {
        "timestamped_cgm_tables": ["AIDEDeviceCGM.txt", "AIDETandemCGMDATAGXB.txt", "cgmAnalysis.txt", "cgmAnalysisExt.txt"],
        "participant_level_insulin_inventory": "AIDEInsulin.txt",
        "timestamped_meal_table_found": False,
        "timestamped_activity_table_found": False,
        "timestamped_insulin_delivery_table_found": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
