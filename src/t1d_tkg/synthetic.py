"""Deterministic synthetic data for software and leakage tests only."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .events import Event


def synthetic_events() -> list[Event]:
    """Return two patients with low, missing-future and event-leakage cases."""

    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    events: list[Event] = []
    for patient, offset in (("p1", 0), ("p2", 1000)):
        base = start + timedelta(days=offset)
        for i in range(90):
            value = 125.0
            if 42 <= i <= 48:
                value = 125.0 - (i - 41) * 9.0
            if 49 <= i <= 53:
                value = 62.0
            if patient == "p1" and i == 70:
                # A missing future after this index must remain unknown.
                continue
            events.append(Event(f"{patient}-cgm-{i}", patient, "cgm", base + timedelta(minutes=5 * i), value, "mg/dL", availability_assumption="assumed_immediate", source_type="cgm"))
        events.extend(
            [
                Event(f"{patient}-insulin-40", patient, "insulin", base + timedelta(minutes=200), 3.0, "U", availability_assumption="assumed_immediate", source_type="pump"),
                Event(f"{patient}-meal-38", patient, "meal", base + timedelta(minutes=190), 35.0, "g", availability_assumption="assumed_immediate", source_type="self_report"),
                Event(f"{patient}-exercise-44", patient, "exercise", base + timedelta(minutes=220), attributes={"duration_minutes": 30, "activity_type": "aerobic"}, availability_assumption="assumed_immediate", source_type="self_report"),
                # This event occurs in the future and must not enter G(t).
                Event(f"{patient}-future-meal", patient, "meal", base + timedelta(minutes=600), 99.0, "g", availability_assumption="assumed_immediate", source_type="self_report"),
            ]
        )
    return events
