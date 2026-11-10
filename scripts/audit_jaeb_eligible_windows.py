#!/usr/bin/env python3
"""Aggregate-only screen for Loop-compatible DCLP insulin/CGM windows.

The screen uses a 120-minute CGM history and a fully observed 30-minute
future. It reports eligibility and descriptive hypoglycemia labels, not model
performance or clinically validated availability. Participant identifiers
are used only in memory to group rows and are never written to output.
"""
from __future__ import annotations

import argparse
import csv
import json
from array import array
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from audit_jaeb_temporal_coverage import encoding, parse_time


SPECS = {
    "dclp3": {
        "folder": "DCLP3 Public Dataset - Release 3 - 2022-08-04/Data Files",
        "cgm": "cgm.txt", "time": "DataDtTm", "value": "CGM",
        "status": None, "period": "Period", "primary_period": "2. Post Randomization",
        "basal": "Pump_BasalRateChange.txt", "bolus": "Pump_BolusDelivered.txt",
    },
    "dclp5": {
        "folder": "DCLP5_Dataset_2022-01-20-5e0f3b16-c890-4ace-9e3b-531f3687cf53",
        "cgm": "DCLP5TandemCGMDATAGXB_b.txt", "time": "DataDtTm", "value": "CGMValue",
        "status": "HighLowIndicator", "period": None, "primary_period": None,
        "basal": "DCLP5TandemBASALRATECHG_b.txt",
        "bolus": "DCLP5TandemBolus_Completed_Combined_b.txt",
    },
}

GRID_SEC = 300
GRID_TOLERANCE_SEC = 60
HISTORY_STEPS = 24
FUTURE_STEPS = 6
HYPO_THRESHOLD = 70.0


def stamp_seconds(raw: str, dataset: str) -> int:
    dt = parse_time(raw, dataset)
    return int((dt - datetime(1970, 1, 1)).total_seconds())


def parse_cgm(root: Path, dataset: str, timestamp_policy: str):
    """Load compact arrays; keep raw participant IDs only in an in-memory map."""
    spec = SPECS[dataset]
    path = root / spec["folder"] / spec["cgm"]
    people: dict[str, int] = {}
    person_codes = array("I")
    stamps = array("q")
    values = array("f")
    statuses = array("B")  # 0 numeric/normal, 1 high sentinel, 2 low sentinel, 3 other
    rows_seen = parseable = invalid_time = invalid_value = missing_value = 0
    adjusted_present = adjusted_used = 0
    periods = Counter()
    print(f"loading {dataset} CGM rows from {path}", flush=True)
    with path.open(newline="", encoding=encoding(path), errors="replace") as handle:
        reader = csv.DictReader(handle, delimiter="|")
        for row in reader:
            rows_seen += 1
            patient = (row.get("PtID") or "").strip()
            if not patient:
                continue
            period = (row.get(spec["period"]) or "").strip() if spec["period"] else ""
            periods[period] += 1
            if dataset == "dclp3" and period != spec["primary_period"]:
                continue
            try:
                raw_time = (row.get(spec["time"]) or "").strip()
                adjusted_time = (row.get("DataDtTm_adjusted") or row.get("DataDtTm_adj") or "").strip()
                adjusted_present += bool(adjusted_time)
                use_adjusted = timestamp_policy == "adjusted-preferred" and bool(adjusted_time)
                adjusted_used += use_adjusted
                sec = stamp_seconds(adjusted_time if use_adjusted else raw_time, dataset)
            except ValueError:
                invalid_time += 1
                continue
            raw_value = (row.get(spec["value"]) or "").strip()
            try:
                value = float(raw_value)
                if not np.isfinite(value):
                    raise ValueError
            except ValueError:
                if raw_value:
                    invalid_value += 1
                else:
                    missing_value += 1
                continue
            status_raw = (row.get(spec["status"]) or "0").strip() if spec["status"] else "0"
            status = int(status_raw) if status_raw in {"0", "1", "2"} else 3
            code = people.setdefault(patient, len(people))
            person_codes.append(code)
            stamps.append(sec)
            values.append(value)
            statuses.append(status)
            parseable += 1
    if not stamps:
        raise RuntimeError(f"No parseable CGM rows found for {dataset}: {path}")
    p = np.frombuffer(person_codes, dtype=np.uint32)
    t = np.frombuffer(stamps, dtype=np.int64)
    v = np.frombuffer(values, dtype=np.float32)
    s = np.frombuffer(statuses, dtype=np.uint8)
    order = np.lexsort((t, p))
    del person_codes, stamps, values, statuses
    report = {
        "file": str(path), "source_rows": rows_seen, "period_rows": dict(periods),
        "rows_selected_for_primary_screen": parseable,
        "participants_selected": len(people), "invalid_timestamp_rows_selected": invalid_time,
        "rows_with_adjusted_timestamp": adjusted_present,
        "rows_using_adjusted_timestamp": adjusted_used,
        "timestamp_policy": timestamp_policy,
        "missing_value_rows_selected": missing_value, "invalid_value_rows_selected": invalid_value,
        "primary_period_policy": ("post-randomization only; baseline omitted because release documents a misaligned pre-admission period"
                                  if dataset == "dclp3" else "all release rows; sentinel indicators handled explicitly"),
    }
    return report, people, p[order], t[order], v[order], s[order]


def parse_events(root: Path, dataset: str, people: dict[str, int], timestamp_policy: str):
    spec = SPECS[dataset]
    event_arrays: dict[str, list[array]] = {
        kind: [array("q") for _ in range(len(people))] for kind in ("basal", "bolus")
    }
    summary = {}
    for kind in ("basal", "bolus"):
        path = root / spec["folder"] / spec[kind]
        rows_seen = parsed = invalid = not_in_cgm_people = adjusted_differs = 0
        with path.open(newline="", encoding=encoding(path), errors="replace") as handle:
            for row in csv.DictReader(handle, delimiter="|"):
                rows_seen += 1
                patient = (row.get("PtID") or "").strip()
                code = people.get(patient)
                if code is None:
                    not_in_cgm_people += 1
                    continue
                raw = (row.get("DataDtTm") or "").strip()
                adjusted = (row.get("DataDtTm_adjusted") or row.get("DataDtTm_adj") or "").strip()
                chosen = adjusted if timestamp_policy == "adjusted-preferred" and adjusted else raw
                adjusted_differs += bool(adjusted and adjusted != raw)
                try:
                    sec = stamp_seconds(chosen, dataset)
                except ValueError:
                    invalid += 1
                    continue
                event_arrays[kind][code].append(sec)
                parsed += 1
        summary[kind] = {
            "file": str(path), "source_rows": rows_seen, "parseable_rows_for_selected_cgm_participants": parsed,
            "invalid_timestamp_rows_for_selected_cgm_participants": invalid,
            "rows_for_participants_not_in_selected_cgm": not_in_cgm_people,
            "rows_where_adjusted_timestamp_differs_from_raw": adjusted_differs,
            "timestamp_policy": timestamp_policy,
        }
    # Sort compact per-person arrays once for searchsorted lookups.
    events = {k: [np.sort(np.frombuffer(a, dtype=np.int64)) for a in v]
              for k, v in event_arrays.items()}
    return summary, events


def canonical_patient_rows(t, v, s, begin: int, end: int):
    """Collapse exact same-time rows; discard conflicting timestamps."""
    times, vals, stats = [], [], []
    exact_duplicate_rows = conflicting_timestamps = 0
    i = begin
    while i < end:
        j = i + 1
        while j < end and t[j] == t[i]:
            j += 1
        unique = {(float(v[k]), int(s[k])) for k in range(i, j)}
        if len(unique) == 1:
            times.append(int(t[i])); vals.append(float(v[i])); stats.append(int(s[i]))
            exact_duplicate_rows += j - i - 1
        else:
            conflicting_timestamps += 1
        i = j
    return (np.asarray(times, dtype=np.int64), np.asarray(vals, dtype=np.float32),
            np.asarray(stats, dtype=np.uint8), exact_duplicate_rows, conflicting_timestamps)


def audit_dataset(root: Path, dataset: str, cgm_timestamp_policy: str,
                  event_timestamp_policy: str) -> dict:
    cgm_report, people, p, t, v, s = parse_cgm(root, dataset, cgm_timestamp_policy)
    event_summary, events = parse_events(root, dataset, people, event_timestamp_policy)
    participant_rows = np.bincount(p, minlength=len(people))
    starts = np.r_[0, np.cumsum(participant_rows[:-1])]
    totals = Counter()
    eligible_per_person = []
    positive_per_person = []
    overlap_per_person = Counter()
    cadence = Counter()
    for code in range(len(people)):
        begin, end = int(starts[code]), int(starts[code] + participant_rows[code])
        pt, pv, ps, dup, conflict = canonical_patient_rows(t, v, s, begin, end)
        totals["exact_duplicate_rows_collapsed"] += dup
        totals["conflicting_timestamps_removed"] += conflict
        if len(pt) > 1:
            delta = np.diff(pt)
            for d in delta[(delta > 0) & (delta <= 3600)]:
                cadence[int(d)] += 1
        # Invalid/censored CGM (DCLP5 HighLowIndicator != 0) cannot be a numeric
        # model input or a known numeric endpoint under the primary policy.
        usable = (ps == 0) & (pv >= 20) & (pv <= 600)
        valid_indices = np.flatnonzero(usable)
        if len(valid_indices) < HISTORY_STEPS + FUTURE_STEPS + 1:
            totals["participants_without_minimum_usable_records"] += 1
            continue
        tt = pt[valid_indices]
        vv = pv[valid_indices]
        # Windows use 25 readings spanning 120 min through current time and six
        # subsequent readings spanning 30 min. Every adjacent gap must be within
        # 5 min +/- 60 sec, and the endpoints must match the nominal durations.
        d = np.diff(tt)
        regular = (d >= GRID_SEC - GRID_TOLERANCE_SEC) & (d <= GRID_SEC + GRID_TOLERANCE_SEC)
        # A break counter makes a candidate valid only when all 30 intervals
        # between input start and final future observation are regular.
        bad_prefix = np.r_[0, np.cumsum(~regular, dtype=np.int32)]
        candidate_i = np.arange(HISTORY_STEPS, len(tt) - FUTURE_STEPS)
        left = candidate_i - HISTORY_STEPS
        right_interval = candidate_i + FUTURE_STEPS - 1
        continuous = (bad_prefix[right_interval + 1] - bad_prefix[left] == 0)
        span_history = tt[candidate_i] - tt[left]
        span_future = tt[candidate_i + FUTURE_STEPS] - tt[candidate_i]
        continuous &= np.abs(span_history - 7200) <= GRID_TOLERANCE_SEC
        continuous &= np.abs(span_future - 1800) <= GRID_TOLERANCE_SEC
        idx = candidate_i[continuous]
        if not len(idx):
            totals["participants_without_eligible_windows"] += 1
            continue
        labels = (np.lib.stride_tricks.sliding_window_view(vv, FUTURE_STEPS + 1)[:, 1:] < HYPO_THRESHOLD).any(axis=1)
        # labels array aligns with each future-start index (0..n-7); select rows
        # using candidate positions translated from the full valid timestamp array.
        y = labels[idx]
        eligible_per_person.append(int(len(idx)))
        positive_per_person.append(int(y.sum()))
        totals["eligible_windows"] += len(idx)
        totals["positive_windows"] += int(y.sum())
        # Include lows represented by DCLP5's dedicated low sentinel as an
        # endpoint sensitivity only. Inputs remain numeric-only; high sentinel
        # values stay unknown. This never silently treats sentinels as glucose.
        if dataset == "dclp5":
            # Separate sensitivity: history and anchor are numeric status-0
            # rows, while each of the six future steps may be numeric status 0
            # or an explicit low sentinel (status 2). High sentinels remain
            # unknown. This is evaluated on the raw canonical timeline so low
            # sentinels are not discarded before candidate windows are built.
            for anchor_pos in range(HISTORY_STEPS, len(valid_indices)):
                raw_anchor = int(valid_indices[anchor_pos])
                raw_history = valid_indices[anchor_pos - HISTORY_STEPS:anchor_pos + 1]
                if len(raw_history) != HISTORY_STEPS + 1:
                    continue
                # Require all history observations including anchor to be
                # adjacent rows on the canonical timeline.
                if np.any(np.diff(raw_history) != 1):
                    continue
                if raw_anchor + FUTURE_STEPS >= len(pt):
                    continue
                raw_future = np.arange(raw_anchor + 1, raw_anchor + FUTURE_STEPS + 1)
                statuses = ps[raw_future]
                values_future = pv[raw_future]
                if np.any(~np.isin(statuses, (0, 2))):
                    continue
                if np.any((statuses == 0) & ((values_future < 20) | (values_future > 600))):
                    continue
                window_t = pt[raw_history[0]:raw_anchor + FUTURE_STEPS + 1]
                gaps = np.diff(window_t)
                if len(gaps) != HISTORY_STEPS + FUTURE_STEPS or np.any(
                    (gaps < GRID_SEC - GRID_TOLERANCE_SEC) | (gaps > GRID_SEC + GRID_TOLERANCE_SEC)
                ):
                    continue
                if abs(int(pt[raw_anchor] - pt[raw_history[0]]) - 7200) > GRID_TOLERANCE_SEC:
                    continue
                if abs(int(pt[raw_anchor + FUTURE_STEPS] - pt[raw_anchor]) - 1800) > GRID_TOLERANCE_SEC:
                    continue
                totals["sentinel_sensitivity_windows"] += 1
                if np.any((statuses == 2) | ((statuses == 0) & (values_future < HYPO_THRESHOLD))):
                    totals["sentinel_sensitivity_positive_windows"] += 1
        # Occurrence-time overlap with basal/bolus in [t-120m,t], descriptive
        # only. The model input availability times have not been measured.
        has = {kind: np.zeros(len(idx), dtype=bool) for kind in ("basal", "bolus")}
        for kind in ("basal", "bolus"):
            et = events[kind][code]
            if not len(et):
                continue
            anchors = tt[idx]
            right = np.searchsorted(et, anchors, side="right")
            left_event = np.searchsorted(et, anchors - 7200, side="left")
            has[kind] = right > left_event
        both = has["basal"] & has["bolus"]
        any_event = has["basal"] | has["bolus"]
        totals["windows_with_basal_in_lookback"] += int(has["basal"].sum())
        totals["windows_with_bolus_in_lookback"] += int(has["bolus"].sum())
        totals["windows_with_both_event_types_in_lookback"] += int(both.sum())
        totals["windows_with_neither_event_type_in_lookback"] += int((~any_event).sum())
        if has["basal"].any(): overlap_per_person["basal"] += 1
        if has["bolus"].any(): overlap_per_person["bolus"] += 1
        if both.any(): overlap_per_person["both"] += 1
    eligible = int(totals["eligible_windows"])
    out = {
        "dataset": dataset,
        "cgm": cgm_report,
        "events": event_summary,
        "timestamp_policy_pair": {
            "cgm": cgm_timestamp_policy,
            "events": event_timestamp_policy,
            "note": "These policies select timestamp fields only; they do not resolve timezone, true occurrence, or first availability.",
        },
        "canonicalization": {
            "exact_duplicate_rows_collapsed": int(totals["exact_duplicate_rows_collapsed"]),
            "conflicting_same_timestamp_groups_removed": int(totals["conflicting_timestamps_removed"]),
            "same_timestamp_policy": "collapse only if glucose and status are identical; remove differing-value/status timestamp groups",
        },
        "window_policy": {
            "input_history_minutes": 120, "future_minutes": 30, "nominal_cadence_seconds": GRID_SEC,
            "adjacent_gap_tolerance_seconds": GRID_TOLERANCE_SEC,
            "history_readings_including_anchor": HISTORY_STEPS + 1,
            "future_readings_after_anchor": FUTURE_STEPS,
            "numeric_value_policy": "only status 0 and 20-600 mg/dL rows; DCLP5 HighLowIndicator 1/2 excluded from numeric windows",
            "label": "any numeric CGM <70 mg/dL among the six future readings",
            "event_features": "presence of timestamped basal/bolus event in occurrence-time lookback [anchor-120 min, anchor]; availability not measured",
        },
        "results": {
            "participants_with_selected_cgm": len(people),
            "participants_with_at_least_one_eligible_window": len(eligible_per_person),
            "participants_without_minimum_usable_records": int(totals["participants_without_minimum_usable_records"]),
            "participants_without_eligible_windows": int(totals["participants_without_eligible_windows"]),
            "eligible_windows": eligible,
            "positive_windows": int(totals["positive_windows"]),
            "positive_prevalence": (totals["positive_windows"] / eligible if eligible else None),
            "eligible_windows_per_participant": {
                "min": min(eligible_per_person) if eligible_per_person else None,
                "median": float(np.median(eligible_per_person)) if eligible_per_person else None,
                "max": max(eligible_per_person) if eligible_per_person else None,
            },
            "eligible_windows_with_basal_in_lookback": int(totals["windows_with_basal_in_lookback"]),
            "eligible_windows_with_bolus_in_lookback": int(totals["windows_with_bolus_in_lookback"]),
            "eligible_windows_with_both_event_types_in_lookback": int(totals["windows_with_both_event_types_in_lookback"]),
            "eligible_windows_with_neither_event_type_in_lookback": int(totals["windows_with_neither_event_type_in_lookback"]),
            "participants_with_any_eligible_window_containing_basal": overlap_per_person["basal"],
            "participants_with_any_eligible_window_containing_bolus": overlap_per_person["bolus"],
            "participants_with_any_eligible_window_containing_both": overlap_per_person["both"],
        },
        "cadence_seconds_top_after_sort": dict(cadence.most_common(12)),
        "scope_limitations": [
            "These are release-local feasibility counts only; no model was run and no external validation claim is supported.",
            "Hypoglycemia labels are derived from the public release's sampled CGM values and do not establish event capture or clinical outcomes.",
            "DCLP3 baseline rows were excluded from the primary screen due to the release note about a misaligned pre-admission period; post-randomization only is used.",
            "DCLP5 low-sentinel sensitivity counts treat the explicit low indicator as a low event; the primary numeric analysis excludes all sentinel rows.",
            "Timestamped pump events are matched by occurrence time; event arrival/availability and treatment-period comparability remain unverified.",
        ],
    }
    if dataset == "dclp5":
        out["dclp5_low_sentinel_label_sensitivity"] = {
            "eligible_windows_scanned": int(totals["sentinel_sensitivity_windows"]),
            "positive_windows_if_low_indicator_counts_as_hypoglycemia": int(totals["sentinel_sensitivity_positive_windows"]),
            "note": "Sensitivity is descriptive; a low sentinel is an explicit censored low indication, not a numeric glucose value.",
        }
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("data_root", nargs="?", type=Path, default=Path("data"))
    parser.add_argument("--datasets", nargs="+", choices=tuple(SPECS), default=("dclp3", "dclp5"))
    parser.add_argument("--cgm-timestamp-policy", choices=("raw", "adjusted-preferred"), default="raw")
    parser.add_argument("--event-timestamp-policy", choices=("raw", "adjusted-preferred"), default="adjusted-preferred")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = {
        "audit_type": "DCLP 120-minute CGM history and fully observed 30-minute future feasibility",
        "audit_date": datetime.now(timezone.utc).date().isoformat(),
        "identifiers_emitted": False,
        "timestamp_policy_pair": {"cgm": args.cgm_timestamp_policy,
                                  "events": args.event_timestamp_policy},
        "datasets": [audit_dataset(args.data_root, name, args.cgm_timestamp_policy,
                                   args.event_timestamp_policy) for name in args.datasets],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
