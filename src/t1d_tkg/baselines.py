"""Transparent non-learned baseline scores."""

from __future__ import annotations

from .windows import WindowSample


def persistence_slope_score_from_values(
    previous_time, previous: float, current_time, current: float, *, horizon_minutes: int,
) -> float:
    """Reference rule from the two most recent admissible CGM readings."""
    steps = max(1, horizon_minutes // 5)
    elapsed_steps = max(1e-6, (current_time - previous_time).total_seconds() / 300)
    slope = (current - previous) / elapsed_steps
    return persistence_slope_score_from_current_and_slope(current, slope, horizon_minutes=horizon_minutes)


def persistence_slope_score_from_current_and_slope(current: float, slope: float, *, horizon_minutes: int) -> float:
    """Reference score when current glucose and five-minute slope are available."""
    steps = max(1, horizon_minutes // 5)
    projected_minimum = min(current + slope * offset for offset in range(1, steps + 1))
    return float(projected_minimum < 70)


def persistence_slope_score(sample: WindowSample) -> float:
    """Binary risk score from linear extrapolation of the last two CGM values.

    This is a reference rule, not a calibrated probability.  It returns 1.0
    when the extrapolated trajectory crosses <70 within the prediction horizon.
    """

    observed = [(event.event_time, event.value) for event in sample.history if event is not None and event.value is not None]
    if not observed:
        return 0.0
    if len(observed) == 1:
        return float(observed[-1][1] < 70)
    last_time, last = observed[-1]
    previous_time, previous = observed[-2]
    return persistence_slope_score_from_values(previous_time, previous, last_time, last, horizon_minutes=sample.horizon_minutes)
