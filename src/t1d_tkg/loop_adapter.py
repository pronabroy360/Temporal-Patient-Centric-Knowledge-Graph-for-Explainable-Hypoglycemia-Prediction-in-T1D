"""Canonical single-row adapter for the Loop public release."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Mapping

from .events import Event


UTC_FORMAT = "%Y-%m-%d %H:%M:%S"


def _number(value: str | None) -> float | None:
    try:
        return float(value) if value and value.strip() else None
    except ValueError:
        return None


def loop_event(row: Mapping[str, str], *, modality: str) -> Event | None:
    """Map one already-canonicalized Loop row without resolving duplicates."""
    patient, record_id, raw_time = row.get("PtID", "").strip(), row.get("RecID", "").strip(), row.get("UTCDtTm", "").strip()
    if not patient or not record_id or not raw_time:
        raise ValueError("Loop event requires PtID, RecID, and UTCDtTm")
    event_time = datetime.strptime(raw_time, UTC_FORMAT).replace(tzinfo=timezone.utc)
    attributes = {"parent_upload_id": row.get("ParentLOOPDeviceUploadsID")}
    if modality == "cgm":
        if row.get("RecordType") != "CGM" or row.get("Units") != "mmol/L":
            return None
        value = _number(row.get("CGMVal"))
        if value is None:
            return None
        return Event(f"loop:cgm:{record_id}", patient, "cgm", event_time, value * 18.0182, "mg/dL", availability_assumption="assumed_immediate", source_type="loop_public", source_record_id=record_id, quality_status="observed_pending_range_validation", attributes={**attributes, "raw_value": row.get("CGMVal"), "raw_unit": "mmol/L"})
    if modality == "basal":
        duration = _number(row.get("Duration"))
        end = event_time + timedelta(milliseconds=duration) if duration and duration > 0 else None
        return Event(f"loop:basal:{record_id}", patient, "basal", event_time, _number(row.get("Rate")), "U/h", end_time=end, availability_assumption="assumed_immediate", source_type="loop_public", source_record_id=record_id, quality_status="observed_valid", attributes={**attributes, "basal_type": row.get("BasalType"), "expected_duration_ms": row.get("ExpectedDuration"), "percent": row.get("Percnt")})
    if modality == "bolus":
        normal, extended = _number(row.get("Normal")) or 0.0, _number(row.get("Extended")) or 0.0
        return Event(f"loop:bolus:{record_id}", patient, "insulin", event_time, normal + extended, "U", availability_assumption="assumed_immediate", source_type="loop_public", source_record_id=record_id, quality_status="observed_valid", attributes={**attributes, "bolus_type": row.get("BolusType"), "normal_u": normal, "extended_u": extended, "duration_ms": row.get("Duration")})
    if modality == "food":
        value = _number(row.get("CarbsNet"))
        return Event(f"loop:food:{record_id}", patient, "meal", event_time, value, row.get("CarbUnits"), availability_assumption="assumed_immediate", source_type="loop_public", source_record_id=record_id, quality_status="observed_valid" if value is not None else "missing", attributes=attributes)
    raise ValueError(f"unsupported Loop modality: {modality}")


def iter_loop_table(path: str | Path, *, modality: str, patient_ids: Iterable[str] | None = None):
    """Yield events from one Loop pipe-delimited table without materializing it."""
    allowed = None if patient_ids is None else {str(patient) for patient in patient_ids}
    with Path(path).open("rb") as handle:
        header = handle.readline().decode("utf-8-sig", "replace").rstrip("\r\n").split("|")
        for raw in handle:
            parts = raw.rstrip(b"\r\n").split(b"|")
            row = {name: parts[index].decode("utf-8", "replace") if index < len(parts) else "" for index, name in enumerate(header)}
            if allowed is not None and row.get("PtID", "").strip() not in allowed:
                continue
            event = loop_event(row, modality=modality)
            if event is not None:
                yield event
