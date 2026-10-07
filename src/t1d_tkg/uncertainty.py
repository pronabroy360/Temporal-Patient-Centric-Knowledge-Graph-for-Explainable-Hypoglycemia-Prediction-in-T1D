"""Participant-cluster uncertainty for fixed out-of-fold predictions."""

from __future__ import annotations

import random
from collections.abc import Mapping, Sequence

from .metrics import average_precision, brier_score


Prediction = tuple[Sequence[int], Sequence[float]]


def _percentile(values: Sequence[float], probability: float) -> float:
    if not values:
        raise ValueError("cannot compute a percentile from no values")
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] + fraction * (ordered[upper] - ordered[lower])


def _participant_metric(prediction: Prediction, metric: str) -> float | None:
    labels, scores = prediction
    if len(labels) != len(scores):
        raise ValueError("labels and scores must have equal lengths")
    if not labels:
        return None
    if metric == "ap":
        return average_precision(labels, scores)
    if metric == "brier":
        return brier_score(labels, scores)
    raise ValueError("metric must be 'ap' or 'brier'")


def paired_cluster_bootstrap(
    predictions_by_model: Mapping[str, Mapping[str, Prediction]],
    *,
    model_a: str,
    model_b: str,
    metric: str = "ap",
    draws: int = 2000,
    seed: int = 0,
) -> dict[str, object]:
    """Estimate a paired model contrast by resampling participants.

    Predictions must already be fixed out-of-fold outputs. All windows from a
    sampled participant stay together, and each draw uses the same sampled
    participant IDs for both models. AP replicates with no positive participant
    contribution are retained as undefined rather than converted to zero.
    """

    if draws < 1:
        raise ValueError("draws must be positive")
    if model_a not in predictions_by_model or model_b not in predictions_by_model:
        raise KeyError("both model_a and model_b must be present")
    participants = sorted(set(predictions_by_model[model_a]) & set(predictions_by_model[model_b]))
    if not participants:
        raise ValueError("models have no shared participants")

    def macro(model: str, ids: Sequence[str]) -> float | None:
        values = [_participant_metric(predictions_by_model[model][participant], metric) for participant in ids]
        values = [value for value in values if value is not None]
        return None if not values else sum(values) / len(values)

    observed_a = macro(model_a, participants)
    observed_b = macro(model_b, participants)
    assert observed_a is not None and observed_b is not None
    observed_difference = observed_a - observed_b
    rng = random.Random(seed)
    differences: list[float] = []
    undefined = 0
    for _ in range(draws):
        sampled = [participants[rng.randrange(len(participants))] for _ in participants]
        value_a = macro(model_a, sampled)
        value_b = macro(model_b, sampled)
        if value_a is None or value_b is None:
            undefined += 1
            continue
        differences.append(value_a - value_b)
    interval = None if not differences else [_percentile(differences, 0.025), _percentile(differences, 0.975)]
    return {
        "metric": metric,
        "model_a": model_a,
        "model_b": model_b,
        "participants": participants,
        "draws": draws,
        "seed": seed,
        "observed": {model_a: observed_a, model_b: observed_b, "difference": observed_difference},
        "difference_ci95": interval,
        "valid_replicates": len(differences),
        "undefined_replicates": undefined,
    }

