"""Exact-grid temporal eligibility rules used by the Loop audit."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Mapping


def audit_exact_grid(
    readings: Mapping[datetime, float], *, threshold: float, horizon_minutes: int = 30,
    history_minutes: int = 120, step_minutes: int = 5,
) -> dict[str, int]:
    """Count exact-grid label and input eligibility without interpolation."""
    if horizon_minutes % step_minutes or history_minutes % step_minutes:
        raise ValueError("history and horizon must divide the grid step")
    times = sorted(readings)
    result = {"timestamps": len(times), "complete_future": 0, "input_eligible": 0, "known_labels": 0, "positive_labels": 0}
    for timestamp in times:
        history = [timestamp - timedelta(minutes=step_minutes * i) for i in range(history_minutes // step_minutes - 1, -1, -1)]
        observed = [point in readings for point in history]
        recovery = [timestamp - timedelta(minutes=10), timestamp - timedelta(minutes=5), timestamp]
        if sum(observed) >= 22 and _longest_missing(observed) <= 2 and not any(
            point not in readings or readings[point] < threshold for point in recovery
        ):
            result["input_eligible"] += 1
        future = [timestamp + timedelta(minutes=step_minutes * i) for i in range(1, horizon_minutes // step_minutes + 1)]
        if all(point in readings for point in future):
            result["complete_future"] += 1
            result["known_labels"] += 1
            result["positive_labels"] += int(min(readings[point] for point in future) < threshold)
    return result


def _longest_missing(observed: list[bool]) -> int:
    longest = current = 0
    for present in observed:
        current = 0 if present else current + 1
        longest = max(longest, current)
    return longest


def audit_cadence_tolerant(
    readings: Mapping[datetime, float], *, threshold: float, tolerance_seconds: int,
    horizon_minutes: int = 30, history_minutes: int = 120, step_minutes: int = 5,
) -> dict[str, int]:
    """Audit complete contiguous runs with a per-interval cadence tolerance.

    This makes no absolute clock-phase assumption and creates no readings. It
    is used to compare tolerance candidates; the final missing-history policy
    remains a separate, explicit window-construction rule.
    """
    if tolerance_seconds < 0:
        raise ValueError("tolerance must be nonnegative")
    ordered = sorted(readings.items())
    history_count = history_minutes // step_minutes
    future_count = horizon_minutes // step_minutes
    expected = step_minutes * 60
    continuous = [False] + [
        abs((ordered[index][0] - ordered[index - 1][0]).total_seconds() - expected) <= tolerance_seconds
        for index in range(1, len(ordered))
    ]
    result = {"timestamps": len(ordered), "complete_future": 0, "input_eligible": 0, "known_labels": 0, "positive_labels": 0}
    for index, (_, value) in enumerate(ordered):
        history_complete = index >= history_count - 1 and all(continuous[index - history_count + 2:index + 1])
        recovery = index >= 2 and all(ordered[position][1] >= threshold for position in range(index - 2, index + 1))
        if history_complete and recovery:
            result["input_eligible"] += 1
        future_complete = index + future_count < len(ordered) and all(continuous[index + 1:index + future_count + 1])
        if future_complete:
            result["complete_future"] += 1
            result["known_labels"] += 1
            result["positive_labels"] += int(min(ordered[position][1] for position in range(index + 1, index + future_count + 1)) < threshold)
    return result


def audit_logical_grid(
    readings: Mapping[datetime, float], *, threshold: float, tolerance_seconds: int,
    horizon_minutes: int = 30, history_minutes: int = 120, step_minutes: int = 5,
) -> dict[str, int]:
    """Apply the protocol's history/future rules on cadence-derived grid runs.

    A gap close to an integer number of sample intervals creates missing slots;
    an irregular interval starts a new run. No slot receives an invented value.
    """
    if tolerance_seconds < 0:
        raise ValueError("tolerance must be nonnegative")
    ordered = sorted(readings.items())
    step_seconds = step_minutes * 60
    runs: list[list[float | None]] = []
    current: list[float | None] = []
    previous: datetime | None = None
    for timestamp, value in ordered:
        if previous is None:
            current = [value]
            runs.append(current)
        else:
            delta = (timestamp - previous).total_seconds()
            intervals = round(delta / step_seconds)
            if intervals >= 1 and abs(delta - intervals * step_seconds) <= tolerance_seconds:
                current.extend([None] * (intervals - 1))
                current.append(value)
            else:
                current = [value]
                runs.append(current)
        previous = timestamp
    history_count = history_minutes // step_minutes
    future_count = horizon_minutes // step_minutes
    result = {"timestamps": len(ordered), "complete_future": 0, "input_eligible": 0, "known_labels": 0, "positive_labels": 0}
    for run in runs:
        for index, value in enumerate(run):
            if value is None:
                continue
            future = run[index + 1:index + future_count + 1]
            if len(future) == future_count and all(item is not None for item in future):
                result["complete_future"] += 1
                result["known_labels"] += 1
                result["positive_labels"] += int(min(future) < threshold)
            history = run[index - history_count + 1:index + 1]
            if len(history) != history_count or sum(item is not None for item in history) < 22:
                continue
            observed = [item is not None for item in history]
            if _longest_missing(observed) > 2:
                continue
            recovery = run[index - 2:index + 1]
            if len(recovery) == 3 and all(item is not None and item >= threshold for item in recovery):
                result["input_eligible"] += 1
    return result


def logical_grid_episode_counts(
    readings: Mapping[datetime, float], *, threshold: float, tolerance_seconds: int,
    step_minutes: int = 5, min_consecutive: int = 3,
) -> dict[str, int]:
    """Count confirmed and boundary-censored low runs without interpolation."""
    ordered = sorted(readings.items())
    step_seconds = step_minutes * 60
    runs: list[list[float | None]] = []
    current: list[float | None] = []
    previous: datetime | None = None
    for timestamp, value in ordered:
        delta = None if previous is None else (timestamp - previous).total_seconds()
        intervals = None if delta is None else round(delta / step_seconds)
        if intervals is not None and intervals >= 1 and abs(delta - intervals * step_seconds) <= tolerance_seconds:
            current.extend([None] * (intervals - 1)); current.append(value)
        else:
            current = [value]; runs.append(current)
        previous = timestamp
    result = {"confirmed_episode_onsets": 0, "censored_boundary_low_runs": 0, "unconfirmed_short_low_runs": 0}
    for run in runs:
        index = 0
        while index < len(run):
            if run[index] is None or run[index] >= threshold:
                index += 1; continue
            start = index
            while index < len(run) and run[index] is not None and run[index] < threshold:
                index += 1
            length = index - start
            preceding_high = start > 0 and run[start - 1] is not None and run[start - 1] >= threshold
            following = run[index:index + 3]
            complete_recovery = len(following) == 3 and all(value is not None and value >= threshold for value in following)
            if length >= min_consecutive and preceding_high and complete_recovery:
                result["confirmed_episode_onsets"] += 1
            elif not preceding_high or not complete_recovery:
                result["censored_boundary_low_runs"] += 1
            else:
                result["unconfirmed_short_low_runs"] += 1
    return result


def logical_grid_window_metadata(
    readings: Mapping[datetime, float], *, threshold: float, tolerance_seconds: int,
    horizon_minutes: int = 30, history_minutes: int = 120, step_minutes: int = 5,
):
    """Yield compact eligibility/label metadata without event payloads."""
    ordered = sorted(readings.items()); step_seconds = step_minutes * 60
    runs: list[list[tuple[datetime | None, float | None]]] = []; current = []; previous = None
    for timestamp, value in ordered:
        delta = None if previous is None else (timestamp - previous).total_seconds()
        intervals = None if delta is None else round(delta / step_seconds)
        if intervals is not None and intervals >= 1 and abs(delta - intervals * step_seconds) <= tolerance_seconds:
            current.extend([(None, None)] * (intervals - 1)); current.append((timestamp, value))
        else:
            current = [(timestamp, value)]; runs.append(current)
        previous = timestamp
    history_count = history_minutes // step_minutes; future_count = horizon_minutes // step_minutes
    for run in runs:
        for index, (timestamp, value) in enumerate(run):
            if timestamp is None: continue
            history = run[index - history_count + 1:index + 1]
            future = run[index + 1:index + future_count + 1]
            observed = [item[0] is not None for item in history]
            eligible = (len(history) == history_count and sum(observed) >= 22 and _longest_missing(observed) <= 2 and index >= 2 and all(run[pos][1] is not None and run[pos][1] >= threshold for pos in range(index - 2, index + 1)))
            known = len(future) == future_count and all(item[1] is not None for item in future)
            yield {"index_time": timestamp.isoformat(), "history_start": (timestamp - timedelta(minutes=history_minutes)).isoformat(), "horizon_minutes": horizon_minutes, "input_eligible": eligible, "label_status": "known" if known else "unknown", "label": int(min(item[1] for item in future) < threshold) if known else None}
