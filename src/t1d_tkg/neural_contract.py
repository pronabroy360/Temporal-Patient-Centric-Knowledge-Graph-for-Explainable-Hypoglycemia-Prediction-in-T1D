"""Content and checkpoint guards for new controlled neural experiments.

The historical GRU checkpoints deliberately do not satisfy this new contract.
"""
from __future__ import annotations
import hashlib
import json
import math
from datetime import datetime
from .cache_io import logical_name, open_cache

CONTRACT_VERSION = "loop-controlled-neural-v1"
VARIANTS = ("cgm-mlp", "cgm-gru-mask", "clean-gru", "recording-gru", "type-timing-gru", "no-age-gru")


def object_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def membership_digest(patients):
    return object_digest(sorted(patients))


def verify_content(path, summary, expected_header):
    """Check uncompressed bytes; writer digests exclude the header line."""
    digest = hashlib.sha256()
    rows = 0
    with open_cache(path, "rb") as handle:
        if json.loads(handle.readline()) != expected_header:
            raise ValueError(f"cache header mismatch: {path.name}")
        for line in handle:
            digest.update(line)
            rows += 1
    if digest.hexdigest() != summary.get("content_sha256"):
        raise ValueError(f"cache content digest mismatch: {path.name}")
    if rows != summary.get("records", summary.get("canonical_events")):
        raise ValueError(f"cache record count mismatch: {path.name}")
    return digest.hexdigest()


def verify_inputs(cgm_meta, event_meta, cgm_paths, event_paths, patients, progress=None):
    from .feature_cache import CACHE_VERSION, FEATURE_NAMES, iter_partition
    from .event_cache import EVENT_CACHE_VERSION
    summaries = {logical_name(item["file"]): item for item in event_meta["summaries"]}
    if len(summaries) != len(event_meta["summaries"]):
        raise ValueError("duplicate event metadata entry")
    content = []
    identities = {}
    for path, summary in zip(cgm_paths, cgm_meta["partition_summaries"], strict=True):
        digest = verify_content(path, summary, {"cache_version": CACHE_VERSION, "features": list(FEATURE_NAMES)})
        content.append((logical_name(path.name), digest))
        # These identities are recomputed independently of the producer. They
        # bind predictions and training counts to every frozen cache row.
        current = None
        for patient, time, label, _ in iter_partition(path):
            if patient not in patients:
                raise ValueError("CGM cache contains a participant outside development")
            if patient != current:
                if patient in identities:
                    raise ValueError("CGM participant appears in multiple cache groups")
                if current is not None and patient <= current:
                    raise ValueError("CGM participant groups are not ordered")
                identities[patient] = {"records": 0, "positive_labels": 0, "digest": hashlib.sha256(), "last_time": None}
                current = patient
            item = identities[patient]
            parsed = datetime.fromisoformat(time)
            if parsed.utcoffset() is None or (item["last_time"] is not None and parsed <= item["last_time"]):
                raise ValueError("CGM timestamps must be timezone aware and strictly increasing")
            item["last_time"] = parsed
            item["records"] += 1
            item["positive_labels"] += label
            item["digest"].update(f"{parsed.isoformat()}|{label}\n".encode())
        if progress:
            progress({"stage": "verify_cgm", "partition": path.name})
    for modality, paths in event_paths.items():
        for path in paths:
            digest = verify_content(path, summaries[logical_name(path.name)], {"cache_version": EVENT_CACHE_VERSION, "modality": modality})
            content.append((logical_name(path.name), digest))
            if progress:
                progress({"stage": "verify_events", "partition": path.name})
    if set(identities) != set(patients):
        raise ValueError("CGM cache does not cover exactly the development participant set")
    for item in identities.values():
        item["digest"] = item["digest"].hexdigest()
        del item["last_time"]
    return object_digest(sorted(content)), identities


def checkpoint_contract(configuration):
    keys = ("contract_version", "fixture_only", "variant", "fold", "seed", "hidden", "epochs", "batch_size", "workers", "max_events", "manifest_sha256", "window_identity_sha256", "input_content_sha256", "training_membership_sha256", "optimizer", "source_sha256")
    return {key: configuration[key] for key in keys}


def validate_checkpoint(checkpoint, expected):
    if checkpoint.get("contract") != checkpoint_contract(expected):
        raise ValueError("checkpoint contract mismatch: fold, membership, inputs, variant or configuration differs")
    if not isinstance(checkpoint.get("epoch"), int) or not 1 <= checkpoint["epoch"] <= expected["epochs"]:
        raise ValueError("checkpoint has no completed training epoch")


def validate_prediction_row(row, patient, previous):
    if row.get("patient_id") != patient or row.get("label") not in (0, 1):
        raise ValueError("prediction participant or label mismatch")
    score = row.get("score")
    if not isinstance(score, (int, float)) or not math.isfinite(score) or not 0 <= score <= 1:
        raise ValueError("prediction score must be finite and within [0,1]")
    time = datetime.fromisoformat(row["index_time"])
    if time.utcoffset() is None or (previous is not None and time <= previous):
        raise ValueError("prediction timestamps must be timezone aware and strictly increasing")
    return time
