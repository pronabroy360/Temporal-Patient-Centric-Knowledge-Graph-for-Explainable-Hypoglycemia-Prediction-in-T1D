"""Leakage-aware prediction-window construction.

The builder uses the native five-minute grid described by the protocol.  It
returns unknown labels for incomplete futures instead of silently converting
missing follow-up to a negative outcome.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable

from .events import Event


@dataclass(frozen=True, slots=True)
class WindowSample:
    sample_id: str
    patient_id: str
    index_time: datetime
    history_start: datetime
    horizon_minutes: int
    history: tuple[Event | None, ...]
    future: tuple[Event | None, ...]
    input_eligible: bool
    eligibility_reason: str
    label_status: str
    label: int | None

    @property
    def observed_history_count(self) -> int:
        return sum(event is not None for event in self.history)

    @property
    def observed_future_count(self) -> int:
        return sum(event is not None for event in self.future)


def _grid_times(index_time: datetime, minutes: int, step: int) -> list[datetime]:
    count = minutes // step
    return [index_time - timedelta(minutes=step * offset) for offset in range(count - 1, -1, -1)]


def _by_time(events: Iterable[Event], event_type: str, patient_id: str) -> dict[datetime, Event]:
    result: dict[datetime, Event] = {}
    for event in events:
        if event.patient_id != patient_id or event.event_type != event_type:
            continue
        if event.quality_status not in {"observed_valid", "derived_valid"}:
            continue
        if event.event_time in result:
            raise ValueError(f"duplicate valid {event_type} timestamp for {patient_id}: {event.event_time}")
        result[event.event_time] = event
    return result


def _missing_run(history: list[Event | None]) -> int:
    longest = current = 0
    for event in history:
        if event is None:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def build_prediction_windows(
    events: Iterable[Event],
    *,
    patient_id: str,
    horizon_minutes: int,
    history_minutes: int = 120,
    step_minutes: int = 5,
    min_history_points: int = 22,
    max_consecutive_missing: int = 2,
) -> list[WindowSample]:
    """Build one sample per CGM timestamp for one patient.

    The history interval is ``(t-history_minutes, t]``.  The future interval is
    ``(t, t+horizon_minutes]``.  Events with unknown availability are excluded
    unless an adapter explicitly marks them ``assumed_immediate``.
    """

    if history_minutes % step_minutes or horizon_minutes % step_minutes:
        raise ValueError("history and horizon must be divisible by step_minutes")
    all_events = list(events)
    cgm = _by_time(all_events, "cgm", patient_id)
    if not cgm:
        return []
    ordered_times = sorted(cgm)
    samples: list[WindowSample] = []
    history_count = history_minutes // step_minutes
    future_count = horizon_minutes // step_minutes

    for index_time in ordered_times:
        history_times = _grid_times(index_time, history_minutes, step_minutes)
        future_times = [index_time + timedelta(minutes=step_minutes * offset) for offset in range(1, future_count + 1)]
        # Inputs are an as-of view.  A historical value that was entered later
        # must not be visible merely because it is present in the eventual
        # release.  Future values are handled separately for retrospective
        # outcome labeling below.
        history = [
            event if event is not None and event.available_by(index_time) else None
            for timestamp in history_times
            for event in [cgm.get(timestamp)]
        ]
        future = [cgm.get(timestamp) for timestamp in future_times]
        current = cgm[index_time]
        reasons: list[str] = []

        if not current.available_by(index_time):
            reasons.append("current_cgm_not_available")
        if current.value is None:
            reasons.append("current_cgm_missing_value")
        elif current.value < 70:
            reasons.append("current_glucose_below_70")
        recovery_times = [index_time - timedelta(minutes=10), index_time - timedelta(minutes=5), index_time]
        recovery = [cgm.get(timestamp) for timestamp in recovery_times]
        if any(event is None or not event.available_by(index_time) or event.value is None or event.value < 70 for event in recovery):
            reasons.append("not_recovered_for_three_readings")
        if sum(event is not None and event.available_by(index_time) for event in history) < min_history_points:
            reasons.append("insufficient_history_coverage")
        if _missing_run(history) > max_consecutive_missing:
            reasons.append("history_gap_too_long")

        eligible = not reasons
        # Labels use eventual, valid observations in the future interval.  Their
        # arrival time is not an input restriction; it belongs to the separate
        # availability-sensitivity experiment.
        future_complete = all(event is not None and event.value is not None for event in future)
        if not future_complete:
            label_status = "unknown"
            label = None
        else:
            values = [event.value for event in future]
            if any(value is None for value in values):
                label_status = "unknown"
                label = None
            else:
                label_status = "known"
                label = int(min(values) < 70)

        samples.append(
            WindowSample(
                sample_id=f"{patient_id}:{index_time.isoformat()}:{horizon_minutes}",
                patient_id=patient_id,
                index_time=index_time,
                history_start=index_time - timedelta(minutes=history_minutes),
                horizon_minutes=horizon_minutes,
                history=tuple(history),
                future=tuple(future),
                input_eligible=eligible,
                eligibility_reason="eligible" if eligible else ";".join(reasons),
                label_status=label_status,
                label=label,
            )
        )
    return samples
