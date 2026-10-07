"""Recorded-event summaries; occurrence-time replay, not measured availability."""
from collections import deque, Counter
from datetime import timedelta

FEATURE_POLICY = "recorded-events-v2-open-history-normal-bolus"
FEATURE_NAMES = ["basal_record_count", "latest_unambiguous_reported_basal_rate",
                 "bolus_record_count", "reported_normal_bolus_units", "minutes_since_bolus",
                 "food_record_count", "reported_food_carbs_g", "minutes_since_food",
                 "basal_missing_count", "bolus_missing_count", "food_missing_count",
                 "latest_basal_unresolved"]


def captured_event_features(index_time, records, *, history_minutes=120):
    return next(iter_captured_event_features([index_time], records, history_minutes=history_minutes))[1]


def iter_captured_event_features(index_times, records, *, history_minutes=120):
    """Use (t-history,t]; unknown values have explicit counts, not clinical zeros.

    Basal is a reported rate, not delivered insulin. Distinct values at the
    latest timestamp invalidate that rate. Sorting costs O(E log E); the
    rolling pass costs O(E+W). Unsupported food units retain record presence.
    """
    if history_minutes <= 0:
        raise ValueError("history must be positive")
    events = iter(sorted(records, key=lambda record: record[0]))
    pending = next(events, None)
    active = {kind: deque() for kind in ("basal", "bolus", "food")}
    totals = Counter()
    missing = Counter()
    latest_basal_time = None
    latest_basal_values = set()
    previous = None
    for time in index_times:
        if previous is not None and time < previous:
            raise ValueError("index times must be ordered")
        previous = time
        while pending is not None and pending[0] <= time:
            event_time, kind, value = pending
            if kind in active:
                active[kind].append(pending)
                if value is None:
                    missing[kind] += 1
                else:
                    totals[kind] += value
                if kind == "basal":
                    if latest_basal_time != event_time:
                        latest_basal_time = event_time
                        latest_basal_values = set()
                    latest_basal_values.add(value)
            pending = next(events, None)
        lower = time - timedelta(minutes=history_minutes)
        for kind, values in active.items():
            while values and values[0][0] <= lower:
                _, _, value = values.popleft()
                if value is None:
                    missing[kind] -= 1
                else:
                    totals[kind] -= value
            if not values:
                totals[kind] = 0.0
        basal, bolus, food = (active[kind] for kind in ("basal", "bolus", "food"))
        unresolved = not basal or len(latest_basal_values) != 1 or None in latest_basal_values
        rate = 0.0 if unresolved else next(iter(latest_basal_values))
        def since(values):
            return float(history_minutes) if not values else (time-values[-1][0]).total_seconds()/60
        yield time, (float(len(basal)), float(rate), float(len(bolus)), float(totals["bolus"]),
                     since(bolus), float(len(food)), float(totals["food"]), since(food),
                     float(missing["basal"]), float(missing["bolus"]), float(missing["food"]),
                     float(unresolved))
