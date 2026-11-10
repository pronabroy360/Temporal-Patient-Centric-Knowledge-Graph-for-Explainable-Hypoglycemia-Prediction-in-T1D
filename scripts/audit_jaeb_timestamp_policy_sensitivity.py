#!/usr/bin/env python3
"""Compare raw and adjusted Jaeb event timestamps against participant CGM spans.

Aggregate-only diagnostic. It does not infer timezone, event availability,
continuous CGM coverage, or event-window eligibility.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path

from audit_jaeb_temporal_coverage import FORMATS, encoding, parse_time, scan_cgm


def scan_event(path: Path, dataset: str, spans: dict[str, list]) -> dict:
    rows = adjusted_present = invalid_raw = invalid_preferred = 0
    raw_inside = preferred_inside = raw_only = preferred_only = 0
    participants_raw: set[str] = set()
    participants_preferred: set[str] = set()
    participants_changed: set[str] = set()
    changed_by = Counter()
    with path.open(newline="", encoding=encoding(path), errors="replace") as handle:
        for row in csv.DictReader(handle, delimiter="|"):
            rows += 1
            patient = (row.get("PtID") or "").strip()
            if not patient:
                continue
            raw_text = (row.get("DataDtTm") or "").strip()
            adjusted_text = (row.get("DataDtTm_adjusted") or row.get("DataDtTm_adj") or "").strip()
            adjusted_present += bool(adjusted_text)
            try:
                raw_dt = parse_time(raw_text, dataset)
            except ValueError:
                raw_dt = None
                invalid_raw += 1
            preferred_dt = raw_dt
            if adjusted_text:
                try:
                    preferred_dt = parse_time(adjusted_text, dataset)
                except ValueError:
                    preferred_dt = None
            if preferred_dt is None:
                invalid_preferred += 1
            span = spans.get(patient)
            in_raw = bool(raw_dt is not None and span is not None and span[0] <= raw_dt <= span[1])
            in_preferred = bool(preferred_dt is not None and span is not None and
                                span[0] <= preferred_dt <= span[1])
            raw_inside += in_raw
            preferred_inside += in_preferred
            if in_raw:
                participants_raw.add(patient)
            if in_preferred:
                participants_preferred.add(patient)
            if in_raw and not in_preferred:
                raw_only += 1
                changed_by["raw_only"] += 1
                participants_changed.add(patient)
            elif in_preferred and not in_raw:
                preferred_only += 1
                changed_by["adjusted_only"] += 1
                participants_changed.add(patient)
    return {
        "file": str(path), "rows": rows,
        "rows_with_adjusted_timestamp": adjusted_present,
        "invalid_raw_timestamp_rows": invalid_raw,
        "invalid_preferred_timestamp_rows": invalid_preferred,
        "raw_policy_events_inside_cgm_first_last_span": raw_inside,
        "adjusted_preferred_with_raw_fallback_events_inside_cgm_first_last_span": preferred_inside,
        "raw_only_inside_span": raw_only, "adjusted_preferred_only_inside_span": preferred_only,
        "participants_with_raw_policy_overlap": len(participants_raw),
        "participants_with_adjusted_preferred_overlap": len(participants_preferred),
        "participants_with_at_least_one_event_changing_inside_outside_status": len(participants_changed),
        "scope_note": "Overall first-to-last CGM span only; not continuous coverage, event availability, or prediction-window overlap.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_root", nargs="?", type=Path, default=Path("data"))
    parser.add_argument("--datasets", nargs="+", choices=tuple(FORMATS), default=("dclp3", "dclp5"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    results = []
    for dataset in args.datasets:
        folder = args.data_root / ("DCLP3 Public Dataset - Release 3 - 2022-08-04/Data Files"
                                  if dataset == "dclp3" else
                                  "DCLP5_Dataset_2022-01-20-5e0f3b16-c890-4ace-9e3b-531f3687cf53")
        cgm_path = folder / FORMATS[dataset]["cgm"]
        print(f"scanning {dataset} CGM participant spans", flush=True)
        cgm_summary, spans = scan_cgm(cgm_path, dataset)
        modalities = {}
        for modality in ("basal", "bolus"):
            path = folder / FORMATS[dataset][modality]
            print(f"comparing {dataset} {modality} timestamps", flush=True)
            modalities[modality] = scan_event(path, dataset, spans)
        results.append({"dataset": dataset, "cgm_participants_with_parsed_spans":
                        cgm_summary["participants_with_parseable_timestamp_and_value"],
                        "modalities": modalities})
    report = {
        "audit_type": "raw versus adjusted-preferred event timestamp span-overlap sensitivity",
        "audit_date": date.today().isoformat(), "identifiers_emitted": False,
        "policy_a": "Use DataDtTm as the event timestamp.",
        "policy_b": "Use DataDtTm_adjusted (or DataDtTm_adj) when nonempty; otherwise use DataDtTm.",
        "datasets": results,
        "limits": [
            "CGM comparison uses participant first-to-last span, not continuous sensor coverage.",
            "This is timestamp-field sensitivity only; no timezone, event availability, or true occurrence time is inferred.",
            "A change in span overlap does not quantify prediction-window feature or label changes.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
