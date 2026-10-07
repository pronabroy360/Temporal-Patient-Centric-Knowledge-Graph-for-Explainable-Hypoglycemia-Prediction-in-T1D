"""Protected canonical event-instance cache for Loop development models."""

from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
from .cache_io import open_cache


EVENT_CACHE_VERSION = "loop-event-instance-cache-v1"
MODELED_MODALITIES = ("basal", "bolus", "food")


def protected_event_id(patient: str, modality: str, source_record_id: str) -> str:
    """Return a stable private identifier without emitting Loop record IDs."""
    payload = f"{EVENT_CACHE_VERSION}|{patient}|{modality}|{source_record_id}".encode()
    return hashlib.sha256(payload).hexdigest()


def write_partition(path: Path, modality: str, records) -> dict[str, object]:
    """Write canonical records for one modality/hash partition."""
    digest = hashlib.sha256()
    counts = {
        "canonical_events": 0,
        "exact_duplicates_removed": 0,
        "participants": 0,
        "same_time_variant_events": 0,
        "known_model_values": 0,
        "unknown_model_values": 0,
    }
    previous_patient = None
    with gzip.open(path, "xt", encoding="utf-8", newline="") as handle:
        header = {"cache_version": EVENT_CACHE_VERSION, "modality": modality}
        handle.write(json.dumps(header, sort_keys=True, separators=(",", ":")) + "\n")
        for record in records:
            patient = str(record["patient_id"])
            if not patient or "\n" in patient:
                raise ValueError("event cache requires a nonempty one-line participant identifier")
            if record["modality"] != modality:
                raise ValueError("event cache partition mixes modalities")
            if previous_patient is not None and patient < previous_patient:
                raise ValueError("event cache records must be ordered by participant")
            if patient != previous_patient:
                counts["participants"] += 1
                previous_patient = patient
            line = json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
            handle.write(line)
            digest.update(line.encode())
            counts["canonical_events"] += 1
            counts["exact_duplicates_removed"] += int(record["exact_duplicate_count"])
            counts["same_time_variant_events"] += int(record["same_time_variant_count"] > 1)
            counts["known_model_values"] += int(record["model_value_known"])
            counts["unknown_model_values"] += int(not record["model_value_known"])
    return {"file": path.name, "content_sha256": digest.hexdigest(), **counts}


def iter_partition(path: Path):
    with open_cache(path, "rt", encoding="utf-8") as handle:
        header = json.loads(next(handle))
        if header.get("cache_version") != EVENT_CACHE_VERSION:
            raise ValueError(f"unsupported event cache header: {path}")
        modality = header.get("modality")
        if modality not in MODELED_MODALITIES:
            raise ValueError(f"unsupported event cache modality: {path}")
        for number, line in enumerate(handle, start=2):
            record = json.loads(line)
            if record.get("modality") != modality:
                raise ValueError(f"event cache modality mismatch at {path}:{number}")
            yield record


def iter_partition_patients(path: Path):
    """Yield one participant's occurrence-time ordered event records at a time."""
    patient = None
    records: list[dict[str, object]] = []
    previous_time = None
    for record in iter_partition(path):
        current_patient = str(record["patient_id"])
        current_time = str(record["occurrence_time"])
        if patient is not None and current_patient != patient:
            yield patient, records
            records = []
            previous_time = None
        if previous_time is not None and current_time < previous_time:
            raise ValueError(f"event cache records are not UTC ordered: {path}")
        patient = current_patient
        previous_time = current_time
        records.append(record)
    if patient is not None:
        yield patient, records


def load_metadata(directory: Path, *, manifest_sha256: str) -> dict[str, object]:
    metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
    if metadata.get("cache_version") != EVENT_CACHE_VERSION:
        raise ValueError("unsupported event cache version")
    if metadata.get("manifest_sha256") != manifest_sha256:
        raise ValueError("event cache was built for a different model manifest")
    expected = set(metadata.get("files", []))
    actual = {path.name for path in directory.glob("events-*.jsonl.gz")}
    if expected != actual:
        raise ValueError("event cache files do not match metadata")
    return metadata
