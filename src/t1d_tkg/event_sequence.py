"""Fixed-width individual-event sequence features for a matched comparator.

This is a transparent smoke baseline, not a claim to reproduce a recurrent
sequence model.  It keeps the most recent admissible non-CGM event instances
and encodes their type, age, value presence/value, and interval duration.
The graph and sequence comparators can therefore receive the same event
membership while using different inductive biases.
"""

from __future__ import annotations

from typing import Iterable

from .events import Event
from .features import cgm_summary
from .windows import WindowSample


EVENT_TYPES = ("insulin", "basal", "meal", "exercise", "context", "physiology", "finger_stick")


def _in_history(event: Event, sample: WindowSample) -> bool:
    if event.event_type == "cgm" or not event.available_by(sample.index_time):
        return False
    if event.end_time is not None:
        return event.event_time <= sample.index_time and event.end_time > sample.history_start
    return sample.history_start < event.event_time <= sample.index_time


def event_sequence_summary(
    sample: WindowSample,
    events: Iterable[Event],
    *,
    max_events: int = 8,
) -> tuple[float, ...]:
    """Return CGM summaries plus a fixed-width encoding of recent events.

    Events are ordered by occurrence time and event ID for deterministic ties.
    Older events are truncated only after sorting, and padding is all zero.
    A value-present flag keeps missing event values distinct from numeric zero.
    """

    if max_events < 1:
        raise ValueError("max_events must be positive")
    selected = sorted(
        (event for event in events if event.patient_id == sample.patient_id and _in_history(event, sample)),
        key=lambda event: (event.event_time, event.event_id),
    )[-max_events:]
    feature_values: list[float] = list(cgm_summary(sample))
    for event in selected:
        type_encoding = [1.0 if event.event_type == event_type else 0.0 for event_type in EVENT_TYPES]
        age = min(1.0, max(0.0, (sample.index_time - event.event_time).total_seconds() / (120.0 * 60.0)))
        value_present = 1.0 if event.value is not None else 0.0
        value = float(event.value) if event.value is not None else 0.0
        duration = 0.0
        if event.end_time is not None:
            elapsed = max(0.0, (sample.index_time - event.event_time).total_seconds() / (120.0 * 60.0))
            interval = max(0.0, (event.end_time - event.event_time).total_seconds() / (120.0 * 60.0))
            duration = min(1.0, elapsed, interval)
        feature_values.extend(type_encoding + [age, value_present, value, duration])
    feature_values.extend([0.0] * (max_events - len(selected)) * (len(EVENT_TYPES) + 4))
    return tuple(feature_values)
