"""Causal 24-slot CGM histories for the frozen Loop development windows."""

from __future__ import annotations

import gzip
import hashlib
import json
import math
from collections import deque
from datetime import datetime
from itertools import zip_longest
from pathlib import Path
from typing import Iterator, Mapping

from .temporal_eligibility import logical_grid_window_metadata


CACHE_VERSION = "loop-cgm-history-cache-v1"
HISTORY_STEPS = 24
STEP_SECONDS = 300
TOLERANCE_SECONDS = 1
HEADER = {"cache_version": CACHE_VERSION, "history_steps": HISTORY_STEPS,
          "step_minutes": 5, "order": "oldest_to_current", "missing_value": 0.0,
          "mask_meaning": "1=observed,0=missing"}


def iter_history_samples(readings: Mapping[datetime, float]) -> Iterator[tuple[str, int, tuple[float, ...], tuple[int, ...]]]:
    """Yield only eligible known-label windows, without filling missing CGM.

    Grid runs and labels come from the frozen window policy. The separate
    24-slot deque reconstructs only information observed through index time.
    """
    slots: deque[float | None] = deque(maxlen=HISTORY_STEPS)
    previous: datetime | None = None
    metadata = logical_grid_window_metadata(readings, threshold=70.0,
                                            tolerance_seconds=TOLERANCE_SECONDS)
    for reading, row in zip_longest(sorted(readings.items()), metadata):
        if reading is None or row is None:
            raise ValueError("CGM and window metadata lengths differ")
        timestamp, value = reading
        if row["index_time"] != timestamp.isoformat() or not math.isfinite(value):
            raise ValueError("CGM and window metadata disagree")
        if previous is not None:
            delta = (timestamp - previous).total_seconds()
            intervals = round(delta / STEP_SECONDS)
            if intervals >= 1 and abs(delta - intervals * STEP_SECONDS) <= TOLERANCE_SECONDS:
                missing = intervals - 1
                if missing >= HISTORY_STEPS - 1:
                    slots.clear()
                    slots.extend([None] * (HISTORY_STEPS - 1))
                else:
                    slots.extend([None] * missing)
            else:
                slots.clear()
        slots.append(value)
        previous = timestamp
        if not row["input_eligible"] or row["label_status"] != "known":
            continue
        if len(slots) != HISTORY_STEPS or slots[-1] != value:
            raise ValueError("eligible window lacks its complete logical history")
        mask = tuple(int(item is not None) for item in slots)
        if sum(mask) < 22 or any(mask[i:i + 3] == (0, 0, 0) for i in range(HISTORY_STEPS - 2)):
            raise ValueError("eligible window violates history coverage policy")
        values = tuple(0.0 if item is None else float(item) for item in slots)
        yield row["index_time"], int(row["label"]), values, mask


def write_partition(path: Path, rows) -> dict[str, object]:
    digest = hashlib.sha256()
    count = positives = participants = 0
    previous_patient: str | None = None
    with gzip.open(path, "xt", encoding="utf-8", newline="") as handle:
        handle.write(json.dumps(HEADER, sort_keys=True) + "\n")
        for patient, index_time, label, values, mask in rows:
            if len(values) != HISTORY_STEPS or len(mask) != HISTORY_STEPS:
                raise ValueError("history rows require exactly 24 slots")
            if not patient or "\t" in patient or "\n" in patient:
                raise ValueError("unsafe participant identifier")
            if previous_patient is not None and patient < previous_patient:
                raise ValueError("history rows must be ordered by participant")
            if int(label) not in (0, 1) or any(bit not in (0, 1) for bit in mask):
                raise ValueError("history rows require binary label and mask")
            if mask[-1] != 1 or sum(mask) < 22 or any(
                tuple(mask[i:i + 3]) == (0, 0, 0) for i in range(HISTORY_STEPS - 2)
            ):
                raise ValueError("history mask violates input eligibility")
            if not all(math.isfinite(float(value)) for value in values):
                raise ValueError("nonfinite CGM history value")
            if any(not bit and value != 0 for value, bit in zip(values, mask, strict=True)):
                raise ValueError("missing history slots must have zero payload")
            if patient != previous_patient:
                participants += 1
                previous_patient = patient
            line = "\t".join((str(patient), str(index_time), str(int(label)),
                              ",".join(repr(float(value)) for value in values),
                              "".join(str(bit) for bit in mask))) + "\n"
            handle.write(line)
            digest.update(line.encode())
            count += 1
            positives += int(label)
    return {"file": path.name, "records": count, "positive_labels": positives,
            "participants": participants, "content_sha256": digest.hexdigest()}


def iter_partition(path: Path):
    from .cache_io import open_cache

    with open_cache(path, "rt", encoding="utf-8") as handle:
        if json.loads(next(handle)) != HEADER:
            raise ValueError("unsupported CGM history cache header")
        for number, line in enumerate(handle, start=2):
            fields = line.rstrip("\n").split("\t")
            if len(fields) != 5 or len(fields[4]) != HISTORY_STEPS or set(fields[4]) - {"0", "1"}:
                raise ValueError(f"malformed history cache row {path}:{number}")
            patient, index_time, label, values_text, mask_text = fields
            values = tuple(float(value) for value in values_text.split(","))
            mask = tuple(int(bit) for bit in mask_text)
            if label not in {"0", "1"} or len(values) != HISTORY_STEPS or any(not math.isfinite(value) for value in values):
                raise ValueError(f"invalid history cache row {path}:{number}")
            if mask[-1] != 1 or sum(mask) < 22 or any(
                mask[i:i + 3] == (0, 0, 0) for i in range(HISTORY_STEPS - 2)
            ):
                raise ValueError(f"ineligible history mask {path}:{number}")
            if any(not bit and value != 0 for value, bit in zip(values, mask, strict=True)):
                raise ValueError(f"unmasked missing history value {path}:{number}")
            yield patient, index_time, int(label), values, mask
