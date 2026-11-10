#!/usr/bin/env python3
"""Audit temporal CGM/insulin overlap in local DCLP3 and DCLP5 releases.

This screening audit emits only aggregate counts. It compares timestamped
basal/bolus rows against each participant's overall CGM span; it does not
claim event-level capture, availability, or valid prediction labels.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from statistics import median


FORMATS = {
    "dclp3": {
        "cgm": "cgm.txt",
        "cgm_time": "DataDtTm",
        "cgm_value": "CGM",
        "status": None,
        "basal": "Pump_BasalRateChange.txt",
        "bolus": "Pump_BolusDelivered.txt",
        "time_format": "%Y-%m-%d %H:%M:%S",
    },
    "dclp5": {
        "cgm": "DCLP5TandemCGMDATAGXB_b.txt",
        "cgm_time": "DataDtTm",
        "cgm_value": "CGMValue",
        "status": "HighLowIndicator",
        "basal": "DCLP5TandemBASALRATECHG_b.txt",
        "bolus": "DCLP5TandemBolus_Completed_Combined_b.txt",
        "time_format": "%m/%d/%Y %I:%M:%S %p",
    },
}


def parse_time(value: str, dataset: str) -> datetime:
    value = value.strip()
    formats = [FORMATS[dataset]["time_format"], "%Y-%m-%d %H:%M:%S",
               "%m/%d/%Y %I:%M:%S %p", "%m/%d/%Y %H:%M:%S",
               "%d%b%y:%H:%M:%S", "%d%b%Y:%H:%M:%S"]
    for pattern in formats:
        try:
            return datetime.strptime(value, pattern)
        except ValueError:
            continue
    # Some DCLP3 aggregate CGM exports use SAS datetime16.0 numeric values.
    if dataset == "dclp3":
        try:
            seconds = float(value)
            return datetime(1960, 1, 1) + __import__("datetime").timedelta(seconds=seconds)
        except (ValueError, OverflowError):
            pass
    raise ValueError(value)


def encoding(path: Path) -> str:
    with path.open("rb") as handle:
        sample = handle.read(4096)
    return "utf-16" if sample.count(b"\x00") > 100 else "utf-8-sig"


def rows(path: Path):
    with path.open(newline="", encoding=encoding(path), errors="replace") as handle:
        yield from csv.DictReader(handle, delimiter="|")


def q(values):
    if not values:
        return {"min": None, "median": None, "max": None}
    return {"min": min(values), "median": median(values), "max": max(values)}


def scan_cgm(path: Path, dataset: str) -> tuple[dict, dict[str, list]]:
    spec = FORMATS[dataset]
    spans: dict[str, list] = {}
    participants: set[str] = set()
    rows_seen = parsed = missing = invalid_time = invalid_value = 0
    low_status = high_status = normal_status = 0
    below70 = below54 = 0
    last: dict[str, datetime] = {}
    source_backwards = source_duplicates = 0
    cadence = Counter()
    for row in rows(path):
        rows_seen += 1
        patient = (row.get("PtID") or "").strip()
        if not patient:
            continue
        participants.add(patient)
        try:
            stamp = parse_time(row.get(spec["cgm_time"]) or "", dataset)
        except ValueError:
            invalid_time += 1
            continue
        value_raw = (row.get(spec["cgm_value"]) or "").strip()
        if not value_raw:
            missing += 1
            continue
        try:
            glucose = float(value_raw)
        except ValueError:
            invalid_value += 1
            continue
        if not (glucose == glucose and abs(glucose) != float("inf")):
            invalid_value += 1
            continue
        status = (row.get(spec["status"]) or "").strip() if spec["status"] else ""
        if status == "1":
            high_status += 1
        elif status == "2":
            low_status += 1
        elif status == "0":
            normal_status += 1
        if glucose > 0:
            below70 += glucose < 70
            below54 += glucose < 54
        span = spans.setdefault(patient, [stamp, stamp, 0, 0])
        span[0] = min(span[0], stamp)
        span[1] = max(span[1], stamp)
        span[2] += 1
        previous = last.get(patient)
        if previous is not None:
            delta = (stamp - previous).total_seconds()
            if delta < 0:
                source_backwards += 1
            elif delta == 0:
                source_duplicates += 1
            else:
                cadence[round(delta)] += 1
        last[patient] = stamp
        parsed += 1
    span_days = [(s[1] - s[0]).total_seconds() / 86400 for s in spans.values()]
    return {"file": str(path), "rows": rows_seen, "participants_with_rows": len(participants),
             "participants_with_parseable_timestamp_and_value": len(spans),
             "parsed_rows": parsed, "missing_glucose_rows": missing,
             "invalid_timestamp_rows": invalid_time, "invalid_glucose_rows": invalid_value,
             "positive_numeric_glucose_below_70_rows": below70,
             "positive_numeric_glucose_below_54_rows": below54,
             "high_low_indicator_rows": {"normal_0": normal_status,
                                          "high_1": high_status, "low_2": low_status},
             "source_order_backward_transitions": source_backwards,
             "source_order_duplicate_transitions": source_duplicates,
             "within_participant_positive_source_order_cadence_seconds_top": dict(cadence.most_common(10)),
             "cgm_span_days_per_participant": q(span_days),
             "timestamp_basis": "release-local/de-identified chronology; no timezone inferred"}, spans


def scan_event(path: Path, dataset: str, spans: dict[str, list]) -> tuple[dict, set[str]]:
    rows_seen = parsed = invalid = adjusted_present = adjusted_used = 0
    outside = inside = 0
    participants_any: set[str] = set()
    participants_inside: set[str] = set()
    per_patient_inside: Counter[str] = Counter()
    out_of_cgm_ids = 0
    for row in rows(path):
        rows_seen += 1
        patient = (row.get("PtID") or "").strip()
        if not patient:
            continue
        participants_any.add(patient)
        raw = (row.get("DataDtTm") or "").strip()
        adjusted = (row.get("DataDtTm_adjusted") or row.get("DataDtTm_adj") or "").strip()
        stamp_raw = adjusted or raw
        if adjusted:
            adjusted_present += 1
            adjusted_used += adjusted != raw
        try:
            stamp = parse_time(stamp_raw, dataset)
        except ValueError:
            invalid += 1
            continue
        parsed += 1
        span = spans.get(patient)
        if span is not None and span[0] <= stamp <= span[1]:
            inside += 1
            participants_inside.add(patient)
            per_patient_inside[patient] += 1
        else:
            outside += 1
            out_of_cgm_ids += span is None
    return ({"file": str(path), "rows": rows_seen, "participants_with_rows": len(participants_any),
            "parseable_event_rows": parsed, "invalid_event_timestamp_rows": invalid,
            "rows_with_adjusted_timestamp": adjusted_present,
            "rows_where_adjusted_timestamp_differs_from_raw": adjusted_used,
            "events_inside_participant_cgm_first_last_span": inside,
            "events_outside_participant_cgm_first_last_span": outside,
            "events_for_participants_without_parseable_cgm": out_of_cgm_ids,
            "participants_with_event_inside_cgm_span": len(participants_inside),
            "inside_event_rows_per_participant": q(list(per_patient_inside.values())),
            "scope_note": "Span overlap only; does not measure simultaneous sensor/event sampling, capture completeness, or event availability."},
            participants_inside)


def audit_dataset(root: Path, dataset: str) -> dict:
    spec = FORMATS[dataset]
    folder = root / ("DCLP3 Public Dataset - Release 3 - 2022-08-04/Data Files"
                     if dataset == "dclp3" else
                     "DCLP5_Dataset_2022-01-20-5e0f3b16-c890-4ace-9e3b-531f3687cf53")
    cgm_path = folder / spec["cgm"]
    print(f"scanning {dataset} CGM {cgm_path}", flush=True)
    cgm_report, spans = scan_cgm(cgm_path, dataset)
    print(f"scanned {dataset} CGM: {cgm_report['parsed_rows']} rows / "
          f"{cgm_report['participants_with_parseable_timestamp_and_value']} participants", flush=True)
    event_pairs = {}
    for kind in ("basal", "bolus"):
        print(f"scanning {dataset} {kind}", flush=True)
        event_pairs[kind] = scan_event(folder / spec[kind], dataset, spans)
        print(f"scanned {dataset} {kind}: {event_pairs[kind][0]['parseable_event_rows']} timestamped rows", flush=True)
    event_reports = {kind: pair[0] for kind, pair in event_pairs.items()}
    event_participants = {kind: pair[1] for kind, pair in event_pairs.items()}
    shared = set(spans)
    return {"dataset": dataset, "release_directory": str(folder),
            "cgm": cgm_report, "basal": event_reports["basal"],
            "bolus": event_reports["bolus"],
            "cgm_basal_bolus_participants_with_span_overlap": len(
                shared & event_participants["basal"] & event_participants["bolus"]),
            "interpretation": "screening only; no labels, events, duplicate policy, or model predictions are frozen"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("data_root", type=Path, nargs="?", default=Path("data"))
    parser.add_argument("--datasets", nargs="+", choices=tuple(FORMATS), default=("dclp3", "dclp5"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = {"audit_type": "Jaeb DCLP release temporal insulin-CGM span coverage",
              "identifiers_emitted": False,
              "limitations": [
                  "CGM first-to-last spans can overstate simultaneous observation.",
                  "The time basis is local/de-identified; timezone and event arrival are not inferred.",
                  "High/low sentinel rows and duplicate-resolution policies require a separate endpoint audit.",
                  "Roche carbohydrate rows are omitted because prior audit found all Carb fields empty."],
              "datasets": [audit_dataset(args.data_root, name) for name in args.datasets]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
