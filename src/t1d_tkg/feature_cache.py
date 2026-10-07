"""Protected, reusable CGM feature cache for development pilots."""

from __future__ import annotations

import gzip
import hashlib
import json
import math
from pathlib import Path
from typing import Iterator
from .cache_io import open_cache


CACHE_VERSION = "loop-cgm-feature-cache-v1"
FEATURE_NAMES = ("current_glucose_mg_dl", "recent_slope_mg_dl_per_5m")


def write_partition(path: Path, rows) -> dict[str, object]:
    """Write one patient-ordered cache partition and return its content digest."""
    digest = hashlib.sha256()
    count = positives = participants = 0
    previous_patient: str | None = None
    with gzip.open(path, "xt", encoding="utf-8", newline="") as handle:
        handle.write(json.dumps({"cache_version": CACHE_VERSION, "features": FEATURE_NAMES}) + "\n")
        for patient, index_time, label, current, slope in rows:
            patient = str(patient)
            if not patient or "\t" in patient or "\n" in patient:
                raise ValueError("participant identifier is unsafe for cache serialization")
            if int(label) not in (0, 1) or not all(math.isfinite(float(value)) for value in (current, slope)):
                raise ValueError("cache rows require a binary label and finite features")
            if previous_patient is not None and patient < previous_patient:
                raise ValueError("cache rows must be ordered by participant")
            if patient != previous_patient:
                participants += 1
                previous_patient = patient
            fields = (patient, str(index_time), str(int(label)), repr(float(current)), repr(float(slope)))
            line = "\t".join(fields) + "\n"
            handle.write(line)
            digest.update(line.encode())
            count += 1
            positives += int(label)
    return {
        "file": path.name,
        "records": count,
        "positive_labels": positives,
        "participants": participants,
        "content_sha256": digest.hexdigest(),
    }


def iter_partition(path: Path) -> Iterator[tuple[str, str, int, tuple[float, float]]]:
    with open_cache(path, "rt", encoding="utf-8") as handle:
        header = json.loads(next(handle))
        if header != {"cache_version": CACHE_VERSION, "features": list(FEATURE_NAMES)}:
            raise ValueError(f"unsupported feature cache header: {path}")
        for number, line in enumerate(handle, start=2):
            fields = line.rstrip("\n").split("\t")
            if len(fields) != 5:
                raise ValueError(f"malformed feature cache row {path}:{number}")
            patient, index_time, label, current, slope = fields
            if label not in {"0", "1"}:
                raise ValueError(f"nonbinary feature cache label {path}:{number}")
            features = (float(current), float(slope))
            if not all(math.isfinite(value) for value in features):
                raise ValueError(f"nonfinite feature cache row {path}:{number}")
            yield patient, index_time, int(label), features


def iter_partition_patients(path: Path):
    """Yield participant-grouped rows from one cache partition."""
    patient: str | None = None
    rows: list[tuple[str, int, tuple[float, float]]] = []
    for row_patient, index_time, label, features in iter_partition(path):
        if patient is not None and row_patient != patient:
            yield patient, rows
            rows = []
        patient = row_patient
        rows.append((index_time, label, features))
    if patient is not None:
        yield patient, rows


def iter_patients(directory: Path):
    """Yield each participant's complete ordered rows from partitioned cache."""
    for path in sorted(directory.glob("features-*.tsv.gz")):
        yield from iter_partition_patients(path)


def load_metadata(directory: Path, *, manifest_sha256: str) -> dict[str, object]:
    metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
    if metadata.get("cache_version") != CACHE_VERSION:
        raise ValueError("unsupported feature cache version")
    if metadata.get("manifest_sha256") != manifest_sha256:
        raise ValueError("feature cache was built for a different model manifest")
    paths = sorted(directory.glob("features-*.tsv.gz"))
    if len(paths) != metadata.get("partitions"):
        raise ValueError("feature cache partition count mismatch")
    names = [item.get("file") for item in metadata.get("partition_summaries", [])]
    if names != [path.name for path in paths]:
        raise ValueError("feature cache files do not match metadata")
    return metadata
