"""Dependency-free metrics for the prespecified imbalanced-risk benchmark."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

METRIC_VERSION = "threshold-grouped-ap-v2"


def average_precision(labels: Iterable[int], scores: Iterable[float]) -> float | None:
    """Compute stepwise average precision; return None when no positives exist."""

    pairs = sorted(zip(scores, labels, strict=True), key=lambda pair: pair[0], reverse=True)
    positive_count = sum(label == 1 for _, label in pairs)
    if positive_count == 0:
        return None
    seen = rank = 0
    precision_sum = 0.0
    # All equal scores cross the decision threshold together. Ranking tied
    # positives before negatives would make AP depend on input row order.
    from itertools import groupby
    for _, group in groupby(pairs, key=lambda pair: pair[0]):
        group_positives = 0
        for _, label in group:
            rank += 1
            group_positives += label == 1
        seen += group_positives
        precision_sum += group_positives * seen / rank
    return precision_sum / positive_count


def brier_score(labels: Iterable[int], probabilities: Iterable[float]) -> float:
    values = [(float(probability) - int(label)) ** 2 for label, probability in zip(labels, probabilities)]
    if not values:
        raise ValueError("cannot compute Brier score for no observations")
    return sum(values) / len(values)


def participant_macro_ap(predictions: Mapping[str, tuple[Iterable[int], Iterable[float]]]) -> float | None:
    """Average participant AP, excluding participants with no positive labels."""

    values = [average_precision(labels, scores) for labels, scores in predictions.values()]
    values = [value for value in values if value is not None]
    return None if not values else sum(values) / len(values)


def threshold_counts(labels: Iterable[int], probabilities: Iterable[float], threshold: float) -> dict[str, int]:
    counts = {"tp": 0, "fp": 0, "tn": 0, "fn": 0}
    for label, probability in zip(labels, probabilities):
        predicted = float(probability) >= threshold
        if predicted and label == 1:
            counts["tp"] += 1
        elif predicted:
            counts["fp"] += 1
        elif label == 1:
            counts["fn"] += 1
        else:
            counts["tn"] += 1
    return counts
