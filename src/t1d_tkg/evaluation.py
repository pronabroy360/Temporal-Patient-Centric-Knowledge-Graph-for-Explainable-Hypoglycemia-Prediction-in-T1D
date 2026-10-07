"""Fold-isolated evaluation for the first CGM-only benchmark."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from .baselines import persistence_slope_score
from .features import cgm_summary
from .logistic import fit_logistic
from .metrics import brier_score, participant_macro_ap
from .multimodal import multimodal_summary
from .event_sequence import event_sequence_summary
from .graph_features import graph_summary_for_sample, RelationMode
from .windows import WindowSample
from .manifest import validate_manifest


def _folds(samples_by_patient: Mapping[str, Sequence[WindowSample]], manifest: Mapping[str, object] | None):
    if manifest is None:
        return [(patient, [candidate for candidate in sorted(samples_by_patient) if candidate != patient]) for patient in sorted(samples_by_patient)]
    validate_manifest(manifest, expected_patients=samples_by_patient)
    folds = []
    for fold in manifest["folds"]:
        test_patients = [str(patient) for patient in fold["test_patients"]]
        if len(test_patients) != 1:
            raise ValueError("LOSO evaluators require exactly one test patient per fold")
        folds.append((test_patients[0], [str(patient) for patient in fold["train_patients"]]))
    return folds


def _eligible(samples: Sequence[WindowSample]) -> list[WindowSample]:
    return [sample for sample in samples if sample.input_eligible and sample.label_status == "known" and sample.label is not None]


def evaluate_loso_cgm(
    samples_by_patient: Mapping[str, Sequence[WindowSample]],
    *,
    include_predictions: bool = False,
    manifest: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Evaluate rule and logistic baselines with leave-one-patient-out folds."""

    rule_predictions: dict[str, tuple[list[int], list[float]]] = {}
    logistic_predictions: dict[str, tuple[list[int], list[float]]] = {}
    fold_counts: dict[str, dict[str, int]] = {}
    for test_patient, train_patients in _folds(samples_by_patient, manifest):
        test = _eligible(samples_by_patient[test_patient])
        train = [sample for patient in train_patients for sample in _eligible(samples_by_patient[patient])]
        if not test:
            fold_counts[test_patient] = {"train": len(train), "test": 0}
            continue
        labels_test = [sample.label for sample in test]
        rule_scores = [persistence_slope_score(sample) for sample in test]
        rule_predictions[test_patient] = (labels_test, rule_scores)
        if train:
            model = fit_logistic([cgm_summary(sample) for sample in train], [sample.label for sample in train])
            logistic_scores = model.predict_proba(cgm_summary(sample) for sample in test)
        else:
            logistic_scores = [0.0] * len(test)
        logistic_predictions[test_patient] = (labels_test, logistic_scores)
        fold_counts[test_patient] = {"train": len(train), "test": len(test), "positives": sum(labels_test)}

    def brier_by_patient(predictions: Mapping[str, tuple[list[int], list[float]]]) -> float | None:
        values = [brier_score(labels, scores) for labels, scores in predictions.values() if labels]
        return None if not values else sum(values) / len(values)

    result: dict[str, object] = {
        "fold_counts": fold_counts,
        "rule": {"participant_macro_ap": participant_macro_ap(rule_predictions), "macro_brier": brier_by_patient(rule_predictions)},
        "logistic_cgm": {"participant_macro_ap": participant_macro_ap(logistic_predictions), "macro_brier": brier_by_patient(logistic_predictions)},
    }
    if include_predictions:
        result["predictions"] = {
            "rule": {patient: {"labels": labels, "scores": scores} for patient, (labels, scores) in rule_predictions.items()},
            "logistic_cgm": {patient: {"labels": labels, "scores": scores} for patient, (labels, scores) in logistic_predictions.items()},
        }
    return result


def evaluate_loso_multimodal(
    events: Sequence,
    samples_by_patient: Mapping[str, Sequence[WindowSample]],
    *,
    include_predictions: bool = False,
    manifest: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Evaluate a matched multimodal logistic baseline with LOSO folds."""

    event_list = list(events)
    predictions: dict[str, tuple[list[int], list[float]]] = {}
    fold_counts: dict[str, dict[str, int]] = {}
    for test_patient, train_patients in _folds(samples_by_patient, manifest):
        test = _eligible(samples_by_patient[test_patient])
        train = [sample for patient in train_patients for sample in _eligible(samples_by_patient[patient])]
        fold_counts[test_patient] = {"train": len(train), "test": len(test), "positives": sum(sample.label for sample in test)}
        if not test:
            continue
        if train:
            model = fit_logistic(
                [multimodal_summary(sample, event_list) for sample in train],
                [sample.label for sample in train],
            )
            scores = model.predict_proba(multimodal_summary(sample, event_list) for sample in test)
        else:
            scores = [0.0] * len(test)
        predictions[test_patient] = ([sample.label for sample in test], scores)
    briers = [brier_score(labels, scores) for labels, scores in predictions.values() if labels]
    result: dict[str, object] = {
        "fold_counts": fold_counts,
        "logistic_multimodal": {
            "participant_macro_ap": participant_macro_ap(predictions),
            "macro_brier": None if not briers else sum(briers) / len(briers),
        },
    }
    if include_predictions:
        result["predictions"] = {
            "logistic_multimodal": {patient: {"labels": labels, "scores": scores} for patient, (labels, scores) in predictions.items()},
        }
    return result


def evaluate_loso_event_sequence(
    events: Sequence,
    samples_by_patient: Mapping[str, Sequence[WindowSample]],
    *,
    max_events: int = 8,
    include_predictions: bool = False,
    manifest: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Evaluate the individual-event sequence smoke comparator with LOSO."""

    event_list = list(events)
    predictions: dict[str, tuple[list[int], list[float]]] = {}
    fold_counts: dict[str, dict[str, int]] = {}
    for test_patient, train_patients in _folds(samples_by_patient, manifest):
        test = _eligible(samples_by_patient[test_patient])
        train = [sample for patient in train_patients for sample in _eligible(samples_by_patient[patient])]
        fold_counts[test_patient] = {"train": len(train), "test": len(test), "positives": sum(sample.label for sample in test)}
        if not test:
            continue
        if train:
            model = fit_logistic(
                [event_sequence_summary(sample, event_list, max_events=max_events) for sample in train],
                [sample.label for sample in train],
            )
            scores = model.predict_proba(event_sequence_summary(sample, event_list, max_events=max_events) for sample in test)
        else:
            scores = [0.0] * len(test)
        predictions[test_patient] = ([sample.label for sample in test], scores)
    briers = [brier_score(labels, scores) for labels, scores in predictions.values() if labels]
    result: dict[str, object] = {
        "fold_counts": fold_counts,
        "logistic_event_sequence": {
            "participant_macro_ap": participant_macro_ap(predictions),
            "macro_brier": None if not briers else sum(briers) / len(briers),
        },
    }
    if include_predictions:
        result["predictions"] = {
            "logistic_event_sequence": {patient: {"labels": labels, "scores": scores} for patient, (labels, scores) in predictions.items()},
        }
    return result


def evaluate_loso_graph(
    events: Sequence,
    samples_by_patient: Mapping[str, Sequence[WindowSample]],
    *,
    relation_mode: RelationMode = "typed",
    include_predictions: bool = False,
    manifest: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Evaluate the transparent as-of graph summary control with LOSO folds."""

    event_list = list(events)
    predictions: dict[str, tuple[list[int], list[float]]] = {}
    fold_counts: dict[str, dict[str, int]] = {}
    for test_patient, train_patients in _folds(samples_by_patient, manifest):
        test = _eligible(samples_by_patient[test_patient])
        train = [sample for patient in train_patients for sample in _eligible(samples_by_patient[patient])]
        fold_counts[test_patient] = {"train": len(train), "test": len(test), "positives": sum(sample.label for sample in test)}
        if not test:
            continue
        if train:
            model = fit_logistic(
                [graph_summary_for_sample(sample, event_list, relation_mode=relation_mode) for sample in train],
                [sample.label for sample in train],
            )
            scores = model.predict_proba(graph_summary_for_sample(sample, event_list, relation_mode=relation_mode) for sample in test)
        else:
            scores = [0.0] * len(test)
        predictions[test_patient] = ([sample.label for sample in test], scores)
    briers = [brier_score(labels, scores) for labels, scores in predictions.values() if labels]
    key = f"logistic_graph_{relation_mode}"
    result: dict[str, object] = {
        "fold_counts": fold_counts,
        key: {
            "participant_macro_ap": participant_macro_ap(predictions),
            "macro_brier": None if not briers else sum(briers) / len(briers),
        },
    }
    if include_predictions:
        result["predictions"] = {
            key: {patient: {"labels": labels, "scores": scores} for patient, (labels, scores) in predictions.items()},
        }
    return result
