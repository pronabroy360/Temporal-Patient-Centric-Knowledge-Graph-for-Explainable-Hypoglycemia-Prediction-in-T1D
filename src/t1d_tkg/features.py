"""Leakage-safe CGM-only features for the first benchmark."""

from __future__ import annotations

import math
from datetime import datetime

from .windows import WindowSample


def cgm_recent_features(previous_time: datetime, previous: float, current_time: datetime, current: float) -> tuple[float, float]:
    """Current CGM and elapsed-time-adjusted recent slope for streaming input."""
    elapsed_steps = max(1e-6, (current_time - previous_time).total_seconds() / 300)
    return (current, (current - previous) / elapsed_steps)


def cgm_summary(sample: WindowSample) -> tuple[float, ...]:
    """Return fixed CGM summaries from the as-of history only.

    Missing values are excluded from summaries and represented by a fraction;
    no future field or outcome is consulted.
    """

    observed = [(event.event_time, event.value) for event in sample.history if event is not None and event.value is not None]
    if not observed:
        return (0.0,) * 9
    current_time, current = observed[-1]
    previous_time, previous = observed[-2] if len(observed) >= 2 else (current_time, current)
    elapsed_steps = max(1e-6, (current_time - previous_time).total_seconds() / 300)
    fifteen_candidates = [item for item in observed if (current_time - item[0]).total_seconds() >= 15 * 60]
    fifteen_time, fifteen_back = fifteen_candidates[-1] if fifteen_candidates else observed[0]
    fifteen_steps = max(1e-6, (current_time - fifteen_time).total_seconds() / 300)
    first_time, first = observed[0]
    total_steps = max(1e-6, (current_time - first_time).total_seconds() / 300)
    values = [value for _, value in observed]
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    recent = cgm_recent_features(previous_time, previous, current_time, current)
    return (
        *recent,
        current - fifteen_back,
        (current - first) / total_steps,
        mean,
        math.sqrt(variance),
        min(values),
        max(values),
        1.0 - len(values) / max(1, len(sample.history)),
    )
