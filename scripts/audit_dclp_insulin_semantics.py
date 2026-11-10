#!/usr/bin/env python3
"""Aggregate-only screen of DCLP pump basal/bolus values and timestamps."""
from __future__ import annotations

import argparse
import csv
import json
from array import array
from collections import Counter
from datetime import date, datetime
from pathlib import Path

import numpy as np

from audit_jaeb_temporal_coverage import encoding


SPECS = {
    "dclp3": {
        "folder": "DCLP3 Public Dataset - Release 3 - 2022-08-04/Data Files",
        "basal": "Pump_BasalRateChange.txt", "bolus": "Pump_BolusDelivered.txt",
    },
    "dclp5": {
        "folder": "DCLP5_Dataset_2022-01-20-5e0f3b16-c890-4ace-9e3b-531f3687cf53",
        "basal": "DCLP5TandemBASALRATECHG_b.txt",
        "bolus": "DCLP5TandemBolus_Completed_Combined_b.txt",
    },
}


def parse_timestamp(value: str) -> datetime | None:
    value = value.strip()
    if not value:
        return None
    for fmt in ("%m/%d/%Y %I:%M:%S %p", "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M:%S.%f"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def describe(values: array) -> dict:
    if not values:
        return {"count": 0, "min": None, "p50": None, "p90": None,
                "p99": None, "max": None, "zero": 0, "negative": 0}
    data = np.asarray(values, dtype=np.float64)
    return {
        "count": int(data.size), "min": float(data.min()),
        "p50": float(np.quantile(data, 0.50)),
        "p90": float(np.quantile(data, 0.90)),
        "p99": float(np.quantile(data, 0.99)), "max": float(data.max()),
        "zero": int((data == 0).sum()), "negative": int((data < 0).sum()),
    }


def scan_event_table(path: Path, kind: str) -> dict:
    value_column = "CommandedBasalRate" if kind == "basal" else "BolusAmount"
    values = array("f")
    types = Counter()
    rows = missing = invalid = adjusted_present = adjusted_differs = 0
    timestamp_parse_failures = 0
    delta_seconds = Counter()
    delta_buckets = Counter()
    deltas_for_quantiles = array("q")
    with path.open(newline="", encoding=encoding(path), errors="replace") as handle:
        for row in csv.DictReader(handle, delimiter="|"):
            rows += 1
            raw_value = (row.get(value_column) or "").strip()
            if not raw_value:
                missing += 1
            else:
                try:
                    value = float(raw_value)
                    if not np.isfinite(value):
                        raise ValueError
                    values.append(value)
                except ValueError:
                    invalid += 1
            if kind == "bolus":
                types[(row.get("BolusType") or "").strip() or "<missing>"] += 1
            adjusted = (row.get("DataDtTm_adjusted") or row.get("DataDtTm_adj") or "").strip()
            if adjusted:
                adjusted_present += 1
                raw = (row.get("DataDtTm") or "").strip()
                adjusted_differs += adjusted != raw
                raw_dt, adjusted_dt = parse_timestamp(raw), parse_timestamp(adjusted)
                if (raw_dt is None or adjusted_dt is None or
                        raw_dt.tzinfo is not None or adjusted_dt.tzinfo is not None):
                    timestamp_parse_failures += 1
                else:
                    delta = int((adjusted_dt - raw_dt).total_seconds())
                    if delta:
                        delta_seconds[delta] += 1
                        deltas_for_quantiles.append(delta)
                        magnitude = abs(delta)
                        if magnitude <= 300:
                            delta_buckets["abs_le_5m"] += 1
                        elif magnitude <= 3600:
                            delta_buckets["abs_5m_to_1h"] += 1
                        elif magnitude <= 43200:
                            delta_buckets["abs_1h_to_12h"] += 1
                        elif magnitude <= 86400:
                            delta_buckets["abs_12h_to_24h"] += 1
                        else:
                            delta_buckets["abs_gt_24h"] += 1
    result = {
        "file": str(path), "rows": rows, "missing_value_rows": missing,
        "invalid_numeric_rows": invalid, "numeric_value_summary": describe(values),
        "rows_with_adjusted_timestamp": adjusted_present,
        "adjusted_timestamp_differs_from_raw": adjusted_differs,
        "raw_to_adjusted_naive_delta_seconds": {
            "count_nonzero": len(deltas_for_quantiles),
            "parse_failures_when_adjusted_present": timestamp_parse_failures,
            "min": min(deltas_for_quantiles) if deltas_for_quantiles else None,
            "p50": float(np.quantile(np.asarray(deltas_for_quantiles, dtype=np.float64), 0.50)) if deltas_for_quantiles else None,
            "p90": float(np.quantile(np.asarray(deltas_for_quantiles, dtype=np.float64), 0.90)) if deltas_for_quantiles else None,
            "max": max(deltas_for_quantiles) if deltas_for_quantiles else None,
            "absolute_delta_buckets": {k: int(delta_buckets[k]) for k in
                                        ("abs_le_5m", "abs_5m_to_1h", "abs_1h_to_12h",
                                         "abs_12h_to_24h", "abs_gt_24h")},
            "top_deltas_seconds": {str(k): int(v) for k, v in delta_seconds.most_common(10)},
        },
        "timestamp_policy_note": "Naive arithmetic on source timestamp strings only; not a timezone conversion, clock-validation, event-availability, or occurrence-time determination.",
    }
    if kind == "bolus":
        result["bolus_type_counts"] = dict(sorted(types.items()))
    return result


def audit_dataset(root: Path, name: str) -> dict:
    spec = SPECS[name]
    directory = root / spec["folder"]
    return {
        "dataset": name,
        "basal": scan_event_table(directory / spec["basal"], "basal"),
        "bolus": scan_event_table(directory / spec["bolus"], "bolus"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_root", nargs="?", type=Path, default=Path("data"))
    parser.add_argument("--datasets", nargs="+", choices=tuple(SPECS), default=("dclp3", "dclp5"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = {
        "audit_type": "DCLP pump basal/bolus value and source-timestamp semantics screen",
        "audit_date": date.today().isoformat(), "identifiers_emitted": False,
        "limits": [
            "Value distributions do not establish physical units, delivery state, or event completeness.",
            "Adjusted timestamp counts do not establish first-available time or timezone equivalence.",
            "Extended bolus subtypes require a prespecified cross-release mapping before transfer evaluation.",
        ],
        "datasets": [audit_dataset(args.data_root, name) for name in args.datasets],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
