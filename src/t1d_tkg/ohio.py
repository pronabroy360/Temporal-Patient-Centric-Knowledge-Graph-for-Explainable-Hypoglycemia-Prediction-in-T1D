"""Conservative adapter for the published OhioT1DM XML layout.

The adapter is intentionally separate from the model code.  It parses the
documented element names and preserves source attributes in ``Event.attributes``;
it does not infer missing data, pair meals with boluses, or treat self-reported
hypo events as CGM outcomes.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
from typing import Iterable
from xml.etree import ElementTree as ET

from .events import Event


OHIO_TIME_FORMAT = "%d-%m-%Y %H:%M:%S"
_MISSING = {"", "nan", "na", "n/a", "none", "null", "-"}


@dataclass(frozen=True, slots=True)
class OhioParseResult:
    patient_id: str
    source_file: str
    source_split: str | None
    metadata: dict[str, str]
    events: tuple[Event, ...]


def _number(raw: str | None) -> float | None:
    if raw is None or raw.strip().lower() in _MISSING:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _parse_time(raw: str | None, timezone) -> datetime:
    if raw is None or not raw.strip():
        raise ValueError("OhioT1DM event has no timestamp")
    try:
        parsed = datetime.strptime(raw.strip(), OHIO_TIME_FORMAT)
    except ValueError as exc:
        raise ValueError(f"unsupported OhioT1DM timestamp {raw!r}; expected {OHIO_TIME_FORMAT}") from exc
    return parsed.replace(tzinfo=timezone)


def _attr(element: ET.Element, *names: str) -> str | None:
    for name in names:
        if name in element.attrib:
            return element.attrib[name]
    return None


def _event(
    *,
    event_id: str,
    patient_id: str,
    event_type: str,
    element: ET.Element,
    timestamp: datetime,
    timezone,
    value: float | None = None,
    unit: str | None = None,
    end_time: datetime | None = None,
    source_file: str,
    source_split: str | None,
    quality_status: str | None = None,
    extra_attributes: dict[str, object] | None = None,
) -> Event:
    attrs = {key: val for key, val in element.attrib.items() if key not in {"ts", "ts_begin", "ts_end", "value", "dose", "carbs"}}
    quality = quality_status or ("observed_valid" if value is not None else "missing")
    return Event(
        event_id=event_id,
        patient_id=patient_id,
        event_type=event_type,
        event_time=timestamp,
        value=value,
        unit=unit,
        end_time=end_time,
        availability_assumption="assumed_immediate",
        source_type="ohiot1dm_xml",
        source_record_id=f"{source_file}:{event_id}",
        quality_status=quality,
        capture_status="known_captured" if value is not None else "unknown",
        attributes={**attrs, **(extra_attributes or {}), "source_split": source_split},
    )


def _children(root: ET.Element, tag: str) -> list[ET.Element]:
    block = root.find(tag)
    return [] if block is None else list(block)


def _patient_id(root: ET.Element, path: Path) -> str:
    value = root.attrib.get("id") or root.attrib.get("patient_id")
    if value:
        return str(value)
    match = re.search(r"(?:^|[-_])([0-9]{3})(?:[-_]|$)", path.stem)
    if match:
        return match.group(1)
    raise ValueError(f"patient id missing from XML root and filename: {path}")


def parse_ohio_xml(path: str | Path, *, timezone, source_split: str | None = None) -> OhioParseResult:
    """Parse one OhioT1DM XML file into canonical events.

    ``timezone`` is required because the published timestamp format has no
    offset.  The caller must choose the documented/deidentified dataset
    timezone; this function never fabricates UTC.
    """

    path = Path(path)
    root = ET.parse(path).getroot()
    patient_id = _patient_id(root, path)
    source_file = path.name
    if source_split is None:
        lowered = path.stem.lower()
        if "training" in lowered:
            source_split = "training"
        elif "testing" in lowered or "test" in lowered:
            source_split = "testing"
    metadata = {key: value for key, value in root.attrib.items()}
    events: list[Event] = []
    serial = 0

    def add_block(tag: str, event_type: str, value_attr: str | None = "value", unit: str | None = None, time_attr: str = "ts") -> None:
        nonlocal serial
        for element in _children(root, tag):
            raw_time = _attr(element, time_attr)
            if raw_time is None and time_attr != "ts":
                raw_time = _attr(element, "ts", "ts_begin")
            if raw_time is None:
                continue
            timestamp = _parse_time(raw_time, timezone)
            value = _number(_attr(element, value_attr)) if value_attr else None
            serial += 1
            events.append(_event(event_id=f"{patient_id}:{tag}:{serial}", patient_id=patient_id, event_type=event_type, element=element, timestamp=timestamp, timezone=timezone, value=value, unit=unit, source_file=source_file, source_split=source_split))

    add_block("glucose_level", "cgm", "value", "mg/dL")
    add_block("finger_stick", "finger_stick", "value", "mg/dL")
    add_block("basis_heart_rate", "physiology", "value", "bpm")
    add_block("basis_gsr", "physiology", "value", "gsr")
    add_block("basis_skin_temperature", "physiology", "value", "degF")
    add_block("basis_air_temperature", "physiology", "value", "degF")
    add_block("basis_steps", "physiology", "value", "steps")
    add_block("acceleration", "physiology", "value", "acceleration")

    # Basal rates persist until the next setting; retaining the interval is
    # important for active-within-window graph construction.
    basal = _children(root, "basal")
    basal_times = [_parse_time(_attr(element, "ts"), timezone) for element in basal if _attr(element, "ts")]
    for index, element in enumerate([element for element in basal if _attr(element, "ts")]):
        timestamp = basal_times[index]
        end = basal_times[index + 1] if index + 1 < len(basal_times) else None
        serial += 1
        events.append(_event(event_id=f"{patient_id}:basal:{serial}", patient_id=patient_id, event_type="basal", element=element, timestamp=timestamp, timezone=timezone, value=_number(_attr(element, "value")), unit="U/h", end_time=end, source_file=source_file, source_split=source_split))

    for tag in ("temp_basal", "sleep", "work", "basis_sleep"):
        for element in _children(root, tag):
            begin = _attr(element, "ts_begin", "ts")
            if begin is None:
                continue
            timestamp = _parse_time(begin, timezone)
            end_raw = _attr(element, "ts_end")
            end = _parse_time(end_raw, timezone) if end_raw else None
            serial += 1
            event_type = "insulin" if tag == "temp_basal" else "context"
            value = _number(_attr(element, "value", "rate")) if tag == "temp_basal" else None
            unit = "U/h" if tag == "temp_basal" else None
            events.append(_event(event_id=f"{patient_id}:{tag}:{serial}", patient_id=patient_id, event_type=event_type, element=element, timestamp=timestamp, timezone=timezone, value=value, unit=unit, end_time=end, source_file=source_file, source_split=source_split))

    for element in _children(root, "bolus"):
        begin = _attr(element, "ts_begin", "ts")
        if begin is None:
            continue
        timestamp = _parse_time(begin, timezone)
        end_raw = _attr(element, "ts_end")
        end = _parse_time(end_raw, timezone) if end_raw else timestamp
        serial += 1
        events.append(_event(event_id=f"{patient_id}:bolus:{serial}", patient_id=patient_id, event_type="insulin", element=element, timestamp=timestamp, timezone=timezone, value=_number(_attr(element, "dose", "value")), unit="U", end_time=end, source_file=source_file, source_split=source_split))

    for element in _children(root, "meal"):
        timestamp_raw = _attr(element, "ts")
        if timestamp_raw is None:
            continue
        serial += 1
        events.append(_event(event_id=f"{patient_id}:meal:{serial}", patient_id=patient_id, event_type="meal", element=element, timestamp=_parse_time(timestamp_raw, timezone), timezone=timezone, value=_number(_attr(element, "carbs", "value")), unit="g", source_file=source_file, source_split=source_split))

    for tag in ("stressors", "hypo_event", "illness", "exercise"):
        for element in _children(root, tag):
            begin = _attr(element, "ts_begin", "ts")
            if begin is None:
                continue
            serial += 1
            end = _parse_time(_attr(element, "ts_end"), timezone) if _attr(element, "ts_end") else None
            attrs = dict(element.attrib)
            if tag == "exercise" and _number(_attr(element, "duration")) is not None:
                attrs["duration_minutes"] = _number(_attr(element, "duration"))
            events.append(_event(event_id=f"{patient_id}:{tag}:{serial}", patient_id=patient_id, event_type="exercise" if tag == "exercise" else "context", element=element, timestamp=_parse_time(begin, timezone), timezone=timezone, end_time=end, source_file=source_file, source_split=source_split, extra_attributes=attrs))

    events.sort(key=lambda event: (event.event_time, event.event_type, event.event_id))
    return OhioParseResult(patient_id, source_file, source_split, metadata, tuple(events))


def load_ohio_directory(directory: str | Path, *, timezone, source_split: str | None = None) -> list[OhioParseResult]:
    """Parse XML files in a directory in deterministic filename order."""

    directory = Path(directory)
    paths = sorted(directory.glob("*.xml"))
    if not paths:
        raise FileNotFoundError(f"no .xml files found in {directory}")
    return [parse_ohio_xml(path, timezone=timezone, source_split=source_split) for path in paths]
