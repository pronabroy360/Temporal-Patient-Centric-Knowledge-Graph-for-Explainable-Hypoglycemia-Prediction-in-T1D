"""As-of multimodal features for the matched tabular baseline."""

from __future__ import annotations

from typing import Iterable

from .events import Event
from .features import cgm_summary
from .windows import WindowSample


def _in_history(event: Event, sample: WindowSample) -> bool:
    if not event.available_by(sample.index_time):
        return False
    if event.end_time is not None:
        return event.event_time <= sample.index_time and event.end_time > sample.history_start
    return sample.history_start < event.event_time <= sample.index_time


def multimodal_summary(sample: WindowSample, events: Iterable[Event]) -> tuple[float, ...]:
    """Return CGM plus compact event summaries from ``(t-120m, t]`` only.

    This is intentionally the same information contract used by the graph
    candidate. Missing event records are not converted to verified zeros; the
    summary describes captured records and includes counts.
    """

    selected = sorted(
        (event for event in events if event.patient_id == sample.patient_id and _in_history(event, sample)),
        key=lambda event: (event.event_time, event.event_id),
    )
    insulin = [event for event in selected if event.event_type in {"insulin", "basal"}]
    boluses = [event for event in selected if event.event_type == "insulin" and event.unit == "U"]
    basal = [event for event in selected if event.event_type == "basal" and event.value is not None]
    meals = [event for event in selected if event.event_type == "meal" and event.value is not None]
    exercise = [event for event in selected if event.event_type == "exercise"]
    context = [event for event in selected if event.event_type in {"context", "physiology", "finger_stick"}]

    def minutes_since(items: list[Event]) -> float:
        return 120.0 if not items else min(120.0, max(0.0, (sample.index_time - max(item.event_time for item in items)).total_seconds() / 60))

    def as_of_duration(event: Event) -> float:
        elapsed = max(0.0, (sample.index_time - event.event_time).total_seconds() / 60)
        declared = float(event.attributes.get("duration_minutes", 0.0) or 0.0)
        if event.end_time is not None:
            interval_minutes = max(0.0, (event.end_time - event.event_time).total_seconds() / 60)
            return min(declared, elapsed, interval_minutes) if declared else min(elapsed, interval_minutes)
        return min(declared, elapsed) if declared else 0.0

    exercise_minutes = sum(as_of_duration(event) for event in exercise)
    latest_basal = basal[-1].value if basal else 0.0
    return cgm_summary(sample) + (
        sum(float(event.value or 0.0) for event in boluses),
        float(len(boluses)),
        minutes_since(boluses),
        float(latest_basal),
        sum(float(event.value or 0.0) for event in meals),
        float(len(meals)),
        minutes_since(meals),
        float(len(exercise)),
        exercise_minutes,
        minutes_since(exercise),
        float(len(context)),
        float(len(insulin)),
    )
