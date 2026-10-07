"""Canonical event objects used by adapters and the synthetic fixture.

The package deliberately keeps source and derived data separate.  An Event is
an observed/recorded fact (or a clearly marked derived fact); labels are never
represented as Events and therefore cannot accidentally enter an as-of graph.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping


def _timestamp(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamps must be timezone-aware; no timezone is fabricated")
    return value


@dataclass(frozen=True, slots=True)
class Event:
    """One canonical patient event.

    ``available_time`` is the first time the record could have been used.  For
    datasets without transaction/arrival timestamps, leave it as ``None`` and
    set ``availability_assumption`` to ``assumed_immediate`` in the adapter.
    """

    event_id: str
    patient_id: str
    event_type: str
    event_time: datetime
    value: float | None = None
    unit: str | None = None
    end_time: datetime | None = None
    available_time: datetime | None = None
    availability_assumption: str = "unknown"
    source_type: str = "unknown"
    source_record_id: str | None = None
    quality_status: str = "observed_valid"
    capture_status: str = "known_captured"
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _timestamp(self.event_time)
        if self.end_time is not None:
            _timestamp(self.end_time)
            if self.end_time < self.event_time:
                raise ValueError("end_time cannot precede event_time")
        if self.available_time is not None:
            _timestamp(self.available_time)
        if not self.event_id or not self.patient_id or not self.event_type:
            raise ValueError("event_id, patient_id and event_type are required")

    def available_by(self, index_time: datetime) -> bool:
        """Return whether the event is known at ``index_time``."""

        _timestamp(index_time)
        if self.available_time is None:
            # The adapter must label this assumption explicitly.  Unknown
            # availability is excluded by default to avoid optimistic leakage.
            return self.availability_assumption == "assumed_immediate" and self.event_time <= index_time
        return self.available_time <= index_time

    def occurs_by(self, index_time: datetime) -> bool:
        _timestamp(index_time)
        return self.event_time <= index_time

    def as_dict(self) -> dict[str, Any]:
        """Serialize without changing the original timestamp or provenance."""

        return {
            "event_id": self.event_id,
            "patient_id": self.patient_id,
            "event_type": self.event_type,
            "event_time": self.event_time.isoformat(),
            "value": self.value,
            "unit": self.unit,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "available_time": self.available_time.isoformat() if self.available_time else None,
            "availability_assumption": self.availability_assumption,
            "source_type": self.source_type,
            "source_record_id": self.source_record_id,
            "quality_status": self.quality_status,
            "capture_status": self.capture_status,
            "attributes": dict(self.attributes),
        }
