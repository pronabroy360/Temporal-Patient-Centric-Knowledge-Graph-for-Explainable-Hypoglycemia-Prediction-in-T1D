"""As-of alignment of timestamped clinical events to prediction windows."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable, Iterator


def aligned_event_counts(
    window_times: Iterable[datetime], event_times: Iterable[datetime], *, lookback_minutes: int,
) -> Iterator[tuple[datetime, int]]:
    """Yield each window time with events in its closed historical interval.

    Both inputs must be ordered for one participant. Events at the prediction
    time are admissible; later events are never used. The function retains only
    timestamps inside the current lookback interval.
    """
    if lookback_minutes <= 0:
        raise ValueError("lookback_minutes must be positive")
    events = iter(event_times)
    active: list[datetime] = []
    next_event = next(events, None)
    last_window: datetime | None = None
    for window in window_times:
        if last_window is not None and window < last_window:
            raise ValueError("window_times must be ordered")
        last_window = window
        while next_event is not None and next_event <= window:
            active.append(next_event)
            next_event = next(events, None)
        lower = window - timedelta(minutes=lookback_minutes)
        active = [event for event in active if event >= lower]
        yield window, len(active)
