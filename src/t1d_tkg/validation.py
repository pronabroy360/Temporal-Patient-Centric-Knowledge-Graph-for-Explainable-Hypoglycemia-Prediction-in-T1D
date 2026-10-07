"""Collection-level checks applied before window construction."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

from .events import Event


KNOWN_EVENT_TYPES = {"cgm", "finger_stick", "physiology", "insulin", "basal", "meal", "exercise", "context"}


def validate_event_collection(events: Iterable[Event]) -> dict[str, object]:
    """Return auditable errors and warnings without resolving source anomalies."""

    event_list = list(events)
    errors: list[dict[str, object]] = []
    warnings: list[dict[str, object]] = []
    ids = Counter(event.event_id for event in event_list)
    duplicate_ids = {event_id: count for event_id, count in ids.items() if count > 1}
    if duplicate_ids:
        errors.append({"code": "duplicate_event_id", "values": duplicate_ids})
    unknown_types = sorted({event.event_type for event in event_list if event.event_type not in KNOWN_EVENT_TYPES})
    if unknown_types:
        warnings.append({"code": "unknown_event_type", "values": unknown_types})
    unknown_availability = sum(
        event.available_time is None and event.availability_assumption == "unknown" for event in event_list
    )
    if unknown_availability:
        warnings.append({"code": "unknown_availability", "count": unknown_availability})
    missing_provenance = sum(event.source_record_id is None for event in event_list)
    if missing_provenance:
        warnings.append({"code": "missing_source_record_id", "count": missing_provenance})
    by_patient: dict[str, list[Event]] = {}
    for event in event_list:
        by_patient.setdefault(event.patient_id, []).append(event)
    non_monotonic = []
    duplicate_cgm: dict[str, dict[str, int]] = {}
    for patient, patient_events in by_patient.items():
        if any(current.event_time < previous.event_time for previous, current in zip(patient_events, patient_events[1:])):
            non_monotonic.append(patient)
        times = Counter(event.event_time.isoformat() for event in patient_events if event.event_type == "cgm")
        repeated = {timestamp: count for timestamp, count in times.items() if count > 1}
        if repeated:
            duplicate_cgm[patient] = repeated
    if non_monotonic:
        warnings.append({"code": "non_monotonic_input_order", "patients": sorted(non_monotonic)})
    if duplicate_cgm:
        warnings.append({"code": "duplicate_cgm_timestamp", "patients": duplicate_cgm})
    return {
        "events": len(event_list),
        "patients": len(by_patient),
        "event_types": dict(sorted(Counter(event.event_type for event in event_list).items())),
        "duplicate_event_ids": duplicate_ids,
        "errors": errors,
        "warnings": warnings,
        "valid": not errors,
    }

