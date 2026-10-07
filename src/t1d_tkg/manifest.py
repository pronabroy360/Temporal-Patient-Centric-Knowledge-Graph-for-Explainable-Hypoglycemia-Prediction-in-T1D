"""Versionable patient-disjoint evaluation manifests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping


def build_loso_manifest(patient_ids: Iterable[str], *, version: str = "loso-v1") -> dict[str, object]:
    """Build deterministic leave-one-patient-out folds."""

    patients = sorted(set(str(patient) for patient in patient_ids))
    if not patients or any(not patient for patient in patients):
        raise ValueError("patient_ids must contain at least one non-empty ID")
    return {
        "version": version,
        "strategy": "leave_one_patient_out",
        "patients": patients,
        "folds": [
            {
                "fold_id": f"test-{patient}",
                "train_patients": [candidate for candidate in patients if candidate != patient],
                "test_patients": [patient],
            }
            for patient in patients
        ],
    }


def build_hashed_kfold_manifest(
    patient_ids: Iterable[str], *, folds: int = 5, version: str = "hashed-kfold-v1",
    salt: str = "t1d-tkg-model-folds-v1",
) -> dict[str, object]:
    """Build fixed patient-disjoint outer folds with a distinct validation fold."""
    patients = sorted(set(str(patient) for patient in patient_ids))
    if folds < 3:
        raise ValueError("at least three folds are required for train/validation/test separation")
    if len(patients) < folds or any(not patient for patient in patients):
        raise ValueError("patient_ids must contain at least one non-empty ID per fold")
    groups = {number: [] for number in range(folds)}
    for patient in patients:
        assignment = int(hashlib.sha256(f"{salt}:{patient}".encode()).hexdigest(), 16) % folds
        groups[assignment].append(patient)
    return {
        "version": version,
        "strategy": "patient_hashed_kfold_with_disjoint_validation",
        "folds_requested": folds,
        "patients": patients,
        "folds": [
            {
                "fold_id": f"outer-{test}",
                "train_patients": [patient for group, members in groups.items() if group not in {test, (test + 1) % folds} for patient in members],
                "validation_patients": groups[(test + 1) % folds],
                "test_patients": groups[test],
            }
            for test in range(folds)
        ],
    }


def validate_manifest(manifest: Mapping[str, object], *, expected_patients: Iterable[str] | None = None) -> None:
    """Validate disjoint fold membership and complete test coverage."""

    patients = set(str(patient) for patient in manifest.get("patients", []))
    if not patients:
        raise ValueError("manifest has no patients")
    if patients & set(map(str, manifest.get("locked_holdout_patients", []))):
        raise ValueError("locked holdout overlaps development patients")
    if expected_patients is not None and patients != set(str(patient) for patient in expected_patients):
        raise ValueError("manifest patients do not match expected patients")
    folds = manifest.get("folds")
    if not isinstance(folds, list) or not folds:
        raise ValueError("manifest has no folds")
    seen_test: list[str] = []
    for fold in folds:
        if not isinstance(fold, Mapping):
            raise ValueError("each fold must be an object")
        train = set(str(patient) for patient in fold.get("train_patients", []))
        validation = set(str(patient) for patient in fold.get("validation_patients", []))
        test = set(str(patient) for patient in fold.get("test_patients", []))
        if not test or train & test or train & validation or validation & test:
            raise ValueError("fold train, validation, and test patients must be disjoint; test cannot be empty")
        if train | validation | test != patients:
            raise ValueError("each fold must cover exactly the manifest patients")
        seen_test.extend(test)
    if set(seen_test) != patients or len(seen_test) != len(set(seen_test)):
        raise ValueError("each manifest patient must appear in exactly one test fold")


def manifest_checksum(manifest: Mapping[str, object]) -> str:
    """Return SHA-256 of canonical manifest JSON."""

    payload = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def save_manifest(path: str | Path, manifest: Mapping[str, object]) -> str:
    """Validate and save a manifest, returning its canonical checksum."""

    validate_manifest(manifest)
    path = Path(path)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest_checksum(manifest)


def load_manifest(path: str | Path) -> dict[str, object]:
    """Load and validate a JSON manifest."""

    manifest = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("manifest JSON must be an object")
    validate_manifest(manifest)
    return manifest


def fold_by_patient(manifest: Mapping[str, object]) -> dict[str, str]:
    """Return the unique test-fold assignment for every manifest patient."""
    validate_manifest(manifest)
    result: dict[str, str] = {}
    for fold in manifest["folds"]:
        fold_id = str(fold.get("fold_id", ""))
        if not fold_id:
            raise ValueError("fold_id is required when deriving assignments")
        for patient in fold["test_patients"]:
            result[str(patient)] = fold_id
    return result
