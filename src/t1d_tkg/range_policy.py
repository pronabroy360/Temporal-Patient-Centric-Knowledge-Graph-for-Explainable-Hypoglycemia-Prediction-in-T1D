"""Explicit CGM range policies for development sensitivity analyses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, TYPE_CHECKING

if TYPE_CHECKING:
    from .events import Event


@dataclass(frozen=True, slots=True)
class CgmRangePolicy:
    name: str
    lower_mg_dl: float | None = None
    upper_mg_dl: float | None = None

    def accepts(self, value: float | None) -> bool:
        """Return whether a numeric value is retained by this policy."""
        if value is None:
            return False
        if self.lower_mg_dl is not None and value < self.lower_mg_dl:
            return False
        if self.upper_mg_dl is not None and value > self.upper_mg_dl:
            return False
        return True


# The primary policy intentionally applies no clinical cutoff. The bounded
# policies are sensitivity analyses only; they must not be presented as
# device-validity rules without domain validation.
RANGE_POLICIES = {
    "observed_numeric": CgmRangePolicy("observed_numeric"),
    "sensitivity_20_600": CgmRangePolicy("sensitivity_20_600", 20.0, 600.0),
    "sensitivity_40_400": CgmRangePolicy("sensitivity_40_400", 40.0, 400.0),
}


def get_range_policy(name: str) -> CgmRangePolicy:
    try:
        return RANGE_POLICIES[name]
    except KeyError as exc:
        raise ValueError(f"unknown CGM range policy: {name}") from exc


def filter_cgm_events(events: Iterable["Event"], policy: CgmRangePolicy) -> Iterator["Event"]:
    """Stream events under an explicit policy, retaining non-CGM modalities."""
    for event in events:
        if event.event_type != "cgm" or policy.accepts(event.value):
            yield event
