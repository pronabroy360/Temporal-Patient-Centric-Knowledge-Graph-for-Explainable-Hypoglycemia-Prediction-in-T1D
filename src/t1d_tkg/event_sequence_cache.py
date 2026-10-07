"""Position-aware features from canonical cached Loop event instances."""

from __future__ import annotations

import hashlib
import math
from collections import deque
from datetime import datetime, timedelta
from collections import Counter
from typing import Iterable, Iterator, Mapping


MODALITIES = ("basal", "bolus", "food")
SUBTYPE_BUCKETS = 8
EVENT_FEATURE_WIDTH = 1 + len(MODALITIES) + SUBTYPE_BUCKETS + 5


def _subtype_bucket(value: str) -> int:
    return int.from_bytes(hashlib.sha256(value.encode()).digest()[:8], "big") % SUBTYPE_BUCKETS


def encode_event(record: Mapping[str, object], index_time: datetime, *, history_minutes: int) -> tuple[float, ...]:
    """Encode one event with explicit validity and value-quality masks."""
    occurrence = datetime.fromisoformat(str(record["occurrence_time"]))
    age = (index_time - occurrence).total_seconds() / (60 * history_minutes)
    modality = str(record["modality"])
    if modality not in MODALITIES or not 0 <= age <= 1:
        raise ValueError("event is outside the declared sequence contract")
    values = [1.0]
    values.extend(float(modality == candidate) for candidate in MODALITIES)
    subtype = [0.0] * SUBTYPE_BUCKETS
    subtype[_subtype_bucket(str(record["subtype"]))] = 1.0
    values.extend(subtype)
    known = bool(record["model_value_known"])
    value = float(record["model_value"]) if known else 0.0
    values.extend((age, value, float(known), math.log1p(float(record["same_time_variant_count"]) - 1), math.log1p(float(record["exact_duplicate_count"]))))
    return tuple(values)


def iter_sequence_features(index_times: Iterable[datetime], records: Iterable[Mapping[str, object]], *, max_events: int, history_minutes: int = 120, include_modality_counts: bool = False):
    """Yield newest-first fixed-width event sequences and truncation counts."""
    if max_events < 1 or history_minutes < 1:
        raise ValueError("max_events and history_minutes must be positive")
    ordered = iter(sorted(records, key=lambda item: str(item["occurrence_time"])))
    pending = next(ordered, None)
    active: deque[Mapping[str, object]] = deque()
    previous = None
    for index_time in index_times:
        if previous is not None and index_time < previous:
            raise ValueError("index times must be ordered")
        previous = index_time
        while pending is not None and datetime.fromisoformat(str(pending["occurrence_time"])) <= index_time:
            active.append(pending); pending = next(ordered, None)
        lower = index_time - timedelta(minutes=history_minutes)
        while active and datetime.fromisoformat(str(active[0]["occurrence_time"])) <= lower:
            active.popleft()
        selected = list(active)[-max_events:]
        feature = []
        for record in reversed(selected):
            feature.extend(encode_event(record, index_time, history_minutes=history_minutes))
        feature.extend([0.0] * (max_events - len(selected)) * EVENT_FEATURE_WIDTH)
        if include_modality_counts:
            active_counts = Counter(str(record["modality"]) for record in active)
            retained_counts = Counter(str(record["modality"]) for record in selected)
            yield index_time, tuple(feature), len(active), max(0, len(active) - max_events), dict(active_counts), dict(retained_counts)
        else:
            yield index_time, tuple(feature), len(active), max(0, len(active) - max_events)
