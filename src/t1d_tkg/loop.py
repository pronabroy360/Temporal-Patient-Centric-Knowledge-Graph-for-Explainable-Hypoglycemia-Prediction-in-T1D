"""Pure, release-specific canonicalization rules for Jaeb's Loop release.

These functions intentionally operate on small in-memory record groups.  The
release adapter will stream and partition the raw files before calling them;
this module must never require a second materialized copy of the release.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable, Mapping


_KEY_FIELDS: dict[str, tuple[str, ...]] = {
    "cgm": ("RecordType", "CGMVal", "Units"),
    "basal": (
        "BasalType", "Duration", "ExpectedDuration", "Percnt", "Rate",
        "SuprBasalType", "SuprDuration", "SuprRate",
    ),
    "bolus": (
        "BolusType", "Normal", "Extended", "ExpectedNormal", "ExpectedExtended",
        "Duration", "ExpectedDuration",
    ),
    "food": ("CarbsNet", "CarbUnits"),
    "exercise": (
        "ExerciseName", "DistanceValue", "DistanceUnits", "DurationValue", "DurationUnits",
        "EnergyValue", "EnergyUnits", "ReportedIntensity",
    ),
}


@dataclass(frozen=True, slots=True)
class LoopRecord:
    """One parsed Loop source row after its UTC occurrence time is validated."""

    modality: str
    patient_id: str
    occurrence_time: datetime
    source_record_id: int
    fields: Mapping[str, Any]
    parent_upload_id: str | None = None

    def __post_init__(self) -> None:
        if self.modality not in _KEY_FIELDS:
            raise ValueError(f"unsupported Loop modality: {self.modality}")
        if self.occurrence_time.tzinfo is None or self.occurrence_time.utcoffset() is None:
            raise ValueError("Loop UTC occurrence_time must be timezone-aware")
        if not self.patient_id:
            raise ValueError("patient_id is required")


@dataclass(frozen=True, slots=True)
class CanonicalLoopRecord:
    """A record retained after exact-repeat collapse, with duplicate provenance."""

    record: LoopRecord
    duplicate_source_record_ids: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class CanonicalizationResult:
    records: tuple[CanonicalLoopRecord, ...]
    ambiguous_cgm_times: frozenset[tuple[str, datetime]]
    exact_duplicates_removed: int


def exact_repeat_key(record: LoopRecord) -> tuple[Any, ...]:
    """Return the release-contract key that proves two source rows identical."""

    return (
        record.patient_id,
        record.occurrence_time,
        *(_freeze(record.fields.get(name)) for name in _KEY_FIELDS[record.modality]),
    )


def canonicalize_records(records: Iterable[LoopRecord]) -> CanonicalizationResult:
    """Collapse exact re-exports and flag conflicting same-time CGM values.

    The caller must provide records from one modality, sorted by patient and
    UTC occurrence time.  Different non-CGM records at the same time remain
    separate.  Differing CGM values remain in provenance but make their
    patient/time unusable for the primary CGM grid.
    """

    source = tuple(records)
    _validate_sorted_one_modality(source)
    by_key: dict[tuple[Any, ...], list[LoopRecord]] = defaultdict(list)
    for record in source:
        by_key[exact_repeat_key(record)].append(record)

    retained: list[CanonicalLoopRecord] = []
    for group in by_key.values():
        representative = min(group, key=lambda item: item.source_record_id)
        duplicates = tuple(sorted(item.source_record_id for item in group if item != representative))
        retained.append(CanonicalLoopRecord(representative, duplicates))
    retained.sort(key=lambda item: (item.record.patient_id, item.record.occurrence_time, item.record.source_record_id))

    ambiguous: set[tuple[str, datetime]] = set()
    if source and source[0].modality == "cgm":
        values_by_time: dict[tuple[str, datetime], set[Any]] = defaultdict(set)
        for item in retained:
            values_by_time[(item.record.patient_id, item.record.occurrence_time)].add(
                _freeze(item.record.fields.get("CGMVal"))
            )
        ambiguous = {time for time, values in values_by_time.items() if len(values) > 1}

    return CanonicalizationResult(
        records=tuple(retained),
        ambiguous_cgm_times=frozenset(ambiguous),
        exact_duplicates_removed=len(source) - len(retained),
    )


def _validate_sorted_one_modality(records: tuple[LoopRecord, ...]) -> None:
    if not records:
        return
    modality = records[0].modality
    previous = (records[0].patient_id, records[0].occurrence_time)
    for record in records:
        if record.modality != modality:
            raise ValueError("canonicalize one Loop modality at a time")
        current = (record.patient_id, record.occurrence_time)
        if current < previous:
            raise ValueError("records must be sorted by patient_id and UTC occurrence_time")
        previous = current


def _freeze(value: Any) -> Any:
    """Make parsed values suitable for a deterministic key without coercion."""

    if isinstance(value, Mapping):
        return tuple(sorted((key, _freeze(item)) for key, item in value.items()))
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return tuple(sorted(_freeze(item) for item in value))
    return value
