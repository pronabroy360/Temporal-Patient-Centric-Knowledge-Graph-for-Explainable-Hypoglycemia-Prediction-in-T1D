"""Integrity checks for archived out-of-fold predictions."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from .manifest import validate_manifest


def validate_prediction_archive(
    predictions: Mapping[str, Mapping[str, Mapping[str, Sequence[object]]]],
    manifest: Mapping[str, object],
) -> None:
    """Validate participant-keyed predictions against a fold manifest."""

    validate_manifest(manifest)
    patients = set(str(patient) for patient in manifest["patients"])
    fold_test = {
        str(patient)
        for fold in manifest["folds"]
        for patient in fold["test_patients"]
    }
    if fold_test != patients:
        raise ValueError("manifest test coverage is incomplete")
    if not predictions:
        raise ValueError("prediction archive has no models")
    for model, by_patient in predictions.items():
        if not by_patient:
            raise ValueError(f"model {model!r} has no participant predictions")
        unknown = set(by_patient) - patients
        if unknown:
            raise ValueError(f"model {model!r} references unknown participants: {sorted(unknown)}")
        missing = patients - set(by_patient)
        if missing:
            raise ValueError(f"model {model!r} is missing participants: {sorted(missing)}")
        for patient, values in by_patient.items():
            labels = values.get("labels")
            scores = values.get("scores")
            if not isinstance(labels, Sequence) or not isinstance(scores, Sequence) or not labels:
                raise ValueError(f"model {model!r}, participant {patient!r} has no labels/scores")
            if len(labels) != len(scores):
                raise ValueError(f"model {model!r}, participant {patient!r} has length mismatch")
            if any(label not in (0, 1) for label in labels):
                raise ValueError(f"model {model!r}, participant {patient!r} has non-binary labels")
            if any(not 0.0 <= float(score) <= 1.0 for score in scores):
                raise ValueError(f"model {model!r}, participant {patient!r} has probability outside [0, 1]")

