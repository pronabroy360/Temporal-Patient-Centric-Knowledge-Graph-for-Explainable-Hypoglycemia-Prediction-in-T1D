"""Small, machine-readable participant audit for the first milestone."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Iterable

from .events import Event
from .episodes import confirmed_episode_onsets
from .validation import validate_event_collection
from .windows import build_prediction_windows


def audit_patient(events: Iterable[Event], patient_id: str) -> dict[str, object]:
    patient_events = [event for event in events if event.patient_id == patient_id]
    cgms = [event for event in patient_events if event.event_type == "cgm" and event.quality_status in {"observed_valid", "derived_valid"}]
    ordered_cgms = sorted(cgms, key=lambda event: event.event_time)
    days = {(event.event_time.date()).isoformat() for event in cgms}
    counts = Counter(event.event_type for event in patient_events)
    try:
        w30 = build_prediction_windows(patient_events, patient_id=patient_id, horizon_minutes=30)
        w60 = build_prediction_windows(patient_events, patient_id=patient_id, horizon_minutes=60)
        window_build_status = "ok"
    except ValueError as exc:
        # Do not choose a duplicate-resolution policy during the audit.  Keep
        # the anomaly visible and defer window construction until the adapter
        # contract is frozen on the authorized release.
        w30, w60 = [], []
        window_build_status = f"blocked:{exc}"
    duplicate_groups = Counter(event.event_time for event in cgms)
    gaps = [
        (current.event_time - previous.event_time).total_seconds() / 60
        for previous, current in zip(ordered_cgms, ordered_cgms[1:])
    ]
    availability = Counter(
        "known_arrival_time" if event.available_time is not None else event.availability_assumption
        for event in patient_events
    )
    return {
        "patient_id": patient_id,
        "valid_monitoring_days": len(days),
        "cgm_readings": len(cgms),
        "cgm_coverage_start": ordered_cgms[0].event_time.isoformat() if ordered_cgms else None,
        "cgm_coverage_end": ordered_cgms[-1].event_time.isoformat() if ordered_cgms else None,
        "longest_cgm_gap_minutes": max(gaps, default=0.0),
        "duplicate_cgm_timestamp_groups": sum(count > 1 for count in duplicate_groups.values()),
        "duplicate_cgm_records": sum(max(0, count - 1) for count in duplicate_groups.values()),
        "event_counts": dict(sorted(counts.items())),
        "availability_time_metadata": dict(sorted(availability.items())),
        "window_build_status": window_build_status,
        "hypo_readings_below_70": sum(event.value is not None and event.value < 70 for event in cgms),
        "hypo_readings_below_54": sum(event.value is not None and event.value < 54 for event in cgms),
        "confirmed_episode_onsets_below_70": len(confirmed_episode_onsets(cgms, threshold=70)),
        "confirmed_episode_onsets_below_54": len(confirmed_episode_onsets(cgms, threshold=54)),
        "valid_30m_windows": sum(sample.input_eligible and sample.label_status == "known" for sample in w30),
        "valid_60m_windows": sum(sample.input_eligible and sample.label_status == "known" for sample in w60),
        "unknown_30m_labels": sum(sample.input_eligible and sample.label_status == "unknown" for sample in w30),
        "unknown_60m_labels": sum(sample.input_eligible and sample.label_status == "unknown" for sample in w60),
        "labelled_30m_positive_rate": _rate([sample.label for sample in w30 if sample.input_eligible and sample.label_status == "known"]),
        "labelled_60m_positive_rate": _rate([sample.label for sample in w60 if sample.input_eligible and sample.label_status == "known"]),
    }


def _rate(labels: list[int | None]) -> float | None:
    return None if not labels else sum(label == 1 for label in labels) / len(labels)


def audit_dataset(events: Iterable[Event]) -> dict[str, object]:
    event_list = list(events)
    patients = sorted({event.patient_id for event in event_list})
    return {
        "patients": len(patients),
        "validation": validate_event_collection(event_list),
        "patient_summaries": [audit_patient(event_list, patient) for patient in patients],
    }
