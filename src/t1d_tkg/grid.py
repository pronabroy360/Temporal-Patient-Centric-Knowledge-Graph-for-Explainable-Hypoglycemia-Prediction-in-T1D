"""Provenance-preserving assignment of observed readings to a regular grid."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable


@dataclass(frozen=True, slots=True)
class GridAssignment:
    grid_time: datetime
    observed_time: datetime
    offset_seconds: int


def assign_to_grid(
    observed_times: Iterable[datetime], *, origin: datetime, step_minutes: int = 5, tolerance_seconds: int = 0
) -> tuple[GridAssignment, ...]:
    """Assign each observation to one nearby slot, rejecting nearest-time ties.

    This performs no value interpolation.  A slot with two equally close
    observations is omitted, and an observation can never populate two slots.
    """
    if tolerance_seconds < 0 or step_minutes <= 0:
        raise ValueError("tolerance must be nonnegative and step must be positive")
    step = timedelta(minutes=step_minutes)
    grouped: dict[datetime, list[datetime]] = {}
    for observed in observed_times:
        if observed.tzinfo is None or observed.utcoffset() is None:
            raise ValueError("observed times must be timezone-aware")
        relative = (observed - origin).total_seconds()
        nearest = round(relative / step.total_seconds())
        slot = origin + nearest * step
        if abs((observed - slot).total_seconds()) <= tolerance_seconds:
            grouped.setdefault(slot, []).append(observed)
    assigned: list[GridAssignment] = []
    for slot, candidates in grouped.items():
        candidates.sort(key=lambda value: (abs((value - slot).total_seconds()), value))
        if len(candidates) > 1 and abs((candidates[0] - slot).total_seconds()) == abs((candidates[1] - slot).total_seconds()):
            continue
        observed = candidates[0]
        assigned.append(GridAssignment(slot, observed, int((observed - slot).total_seconds())))
    return tuple(sorted(assigned, key=lambda item: item.grid_time))
