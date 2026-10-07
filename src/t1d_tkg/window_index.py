"""Compact, versionable index for leakage-aware prediction windows."""

from __future__ import annotations

import hashlib
import gzip
import json
from pathlib import Path
from typing import Iterable, Iterator, Mapping

from .windows import WindowSample


def window_index_record(sample: WindowSample, *, fold_id: str | None = None) -> dict[str, object]:
    """Serialize window metadata without copying CGM or auxiliary event payloads."""
    return {
        "sample_id": sample.sample_id,
        "patient_id": sample.patient_id,
        "fold_id": fold_id,
        "index_time": sample.index_time.isoformat(),
        "history_start": sample.history_start.isoformat(),
        "horizon_minutes": sample.horizon_minutes,
        "input_eligible": sample.input_eligible,
        "eligibility_reason": sample.eligibility_reason,
        "label_status": sample.label_status,
        "label": sample.label,
        "observed_history_count": sample.observed_history_count,
        "observed_future_count": sample.observed_future_count,
    }


def write_window_index(
    path: str | Path,
    samples: Iterable[WindowSample],
    *,
    fold_by_patient: Mapping[str, str] | None = None,
    protocol_version: str = "loop-window-index-v1",
) -> dict[str, object]:
    """Write newline-delimited metadata and return a reconciliation summary.

    Only one sample is held at a time. The returned SHA-256 is over the exact
    bytes written, making a private index auditable without exposing payloads.
    """
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    counts = {"records": 0, "input_eligible": 0, "known_labels": 0, "positive_labels": 0}
    with destination.open("wb") as handle:
        header = {"record_type": "window_index", "protocol_version": protocol_version}
        line = (json.dumps(header, sort_keys=True, separators=(",", ":")) + "\n").encode()
        handle.write(line); digest.update(line)
        for sample in samples:
            fold_id = None if fold_by_patient is None else fold_by_patient.get(sample.patient_id)
            record = window_index_record(sample, fold_id=fold_id)
            line = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode()
            handle.write(line); digest.update(line)
            counts["records"] += 1
            counts["input_eligible"] += int(sample.input_eligible)
            counts["known_labels"] += int(sample.label_status == "known")
            counts["positive_labels"] += int(sample.label == 1)
    return {"path": str(destination), "protocol_version": protocol_version, **counts, "sha256": digest.hexdigest()}


def iter_window_index(path: str | Path) -> Iterator[dict[str, object]]:
    """Yield metadata records, validating the index header."""
    source = Path(path)
    opener = gzip.open if source.suffix == ".gz" else open
    with opener(source, "rt", encoding="utf-8") as handle:
        header = json.loads(next(handle))
        if header.get("record_type") != "window_index":
            raise ValueError("not a window index")
        for line in handle:
            if line.strip():
                yield json.loads(line)


def validate_window_index(path: str | Path, *, expected_folds: Mapping[str, str] | None = None) -> dict[str, object]:
    """Validate metadata invariants and return aggregate counts.

    This deliberately does not require identifiers to be public; callers may
    supply a protected patient-to-fold mapping when validating private files.
    """
    records = {"records": 0, "input_eligible": 0, "known_labels": 0, "positive_labels": 0}
    patients: set[str] = set()
    sample_ids: set[str] = set()
    patient_folds: dict[str, object] = {}
    for record in iter_window_index(path):
        required = ("sample_id", "patient_id", "index_time", "horizon_minutes", "input_eligible", "label_status", "label")
        if any(key not in record for key in required):
            raise ValueError("window index record is missing required metadata")
        patient = str(record["patient_id"])
        sample_id = str(record["sample_id"])
        if not patient or not sample_id:
            raise ValueError("window index identifiers cannot be empty")
        if sample_id in sample_ids:
            raise ValueError(f"duplicate sample_id: {sample_id}")
        sample_ids.add(sample_id)
        fold_id = record.get("fold_id")
        if patient in patient_folds and patient_folds[patient] != fold_id:
            raise ValueError("patient appears in multiple folds")
        patient_folds[patient] = fold_id
        from datetime import datetime
        datetime.fromisoformat(str(record["index_time"]))
        if int(record["horizon_minutes"]) <= 0:
            raise ValueError("horizon_minutes must be positive")
        eligible = bool(record["input_eligible"])
        status = str(record["label_status"])
        label = record["label"]
        if status == "known" and label not in (0, 1):
            raise ValueError("known labels must be binary")
        if status != "known" and label is not None:
            raise ValueError("unknown labels must be null")
        if expected_folds is not None and fold_id != expected_folds.get(patient):
            raise ValueError("record fold does not match expected protected manifest")
        records["records"] += 1; records["input_eligible"] += int(eligible)
        records["known_labels"] += int(status == "known"); records["positive_labels"] += int(label == 1)
        patients.add(patient)
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    return {**records, "participants": len(patients), "path": str(path), "sha256": digest}


def validate_window_index_directory(path: str | Path, *, expected_folds: Mapping[str, str] | None = None) -> dict[str, object]:
    """Validate every compressed partition and aggregate non-identifying totals."""
    directory = Path(path)
    partitions = sorted(directory.glob("*.jsonl.gz"))
    if not partitions:
        raise ValueError("window-index directory has no .jsonl.gz partitions")
    summaries = [validate_window_index(partition, expected_folds=expected_folds) for partition in partitions]
    digest = hashlib.sha256("\n".join(summary["sha256"] for summary in summaries).encode()).hexdigest()
    return {
        "path": str(directory), "partitions": len(summaries),
        "records": sum(int(summary["records"]) for summary in summaries),
        "input_eligible": sum(int(summary["input_eligible"]) for summary in summaries),
        "known_labels": sum(int(summary["known_labels"]) for summary in summaries),
        "positive_labels": sum(int(summary["positive_labels"]) for summary in summaries),
        "participants_within_partitions": sum(int(summary["participants"]) for summary in summaries),
        "partition_digest_sha256": digest,
    }
