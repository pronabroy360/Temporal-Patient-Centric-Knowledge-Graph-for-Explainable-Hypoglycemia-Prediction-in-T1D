"""Dependency-free score calibration and reliability diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp
from typing import Iterable, Sequence


def _sigmoid(value: float) -> float:
    if value >= 0:
        z = exp(-value)
        return 1.0 / (1.0 + z)
    z = exp(value)
    return z / (1.0 + z)


@dataclass(frozen=True, slots=True)
class PlattScaler:
    """Logistic calibration map ``sigmoid(intercept + slope * score)``."""

    intercept: float
    slope: float

    def predict(self, scores: Iterable[float]) -> list[float]:
        return [_sigmoid(self.intercept + self.slope * float(score)) for score in scores]


def fit_platt_scaler(
    scores: Sequence[float],
    labels: Sequence[int],
    *,
    learning_rate: float = 0.05,
    iterations: int = 1000,
    l2: float = 1e-3,
) -> PlattScaler:
    """Fit a Platt map on validation scores only.

    The caller is responsible for keeping calibration participants outside
    the training and test folds. A small L2 penalty stabilizes the map for
    tiny validation sets; the intercept is not penalized.
    """

    if len(scores) != len(labels) or not scores:
        raise ValueError("scores and labels must have equal, non-empty lengths")
    if any(label not in (0, 1) for label in labels):
        raise ValueError("labels must be binary")
    if iterations < 1 or learning_rate <= 0 or l2 < 0:
        raise ValueError("iterations and learning_rate must be positive; l2 cannot be negative")
    intercept = 0.0
    slope = 0.0
    count = float(len(scores))
    for _ in range(iterations):
        errors = [_sigmoid(intercept + slope * float(score)) - label for score, label in zip(scores, labels)]
        intercept -= learning_rate * sum(errors) / count
        slope -= learning_rate * (sum(error * float(score) for error, score in zip(errors, scores)) / count + l2 * slope)
    return PlattScaler(intercept, slope)


def reliability_bins(
    labels: Sequence[int],
    probabilities: Sequence[float],
    *,
    n_bins: int = 10,
) -> list[dict[str, float | int]]:
    """Return non-empty equal-width reliability bins in ``[0, 1]``."""

    if len(labels) != len(probabilities) or not labels:
        raise ValueError("labels and probabilities must have equal, non-empty lengths")
    if n_bins < 1:
        raise ValueError("n_bins must be positive")
    bins: list[list[tuple[int, float]]] = [[] for _ in range(n_bins)]
    for label, probability in zip(labels, probabilities):
        if label not in (0, 1):
            raise ValueError("labels must be binary")
        probability = float(probability)
        if not 0.0 <= probability <= 1.0:
            raise ValueError("probabilities must lie in [0, 1]")
        index = min(n_bins - 1, int(probability * n_bins))
        bins[index].append((label, probability))
    result: list[dict[str, float | int]] = []
    for index, values in enumerate(bins):
        if not values:
            continue
        result.append(
            {
                "bin": index,
                "count": len(values),
                "mean_predicted": sum(probability for _, probability in values) / len(values),
                "observed_rate": sum(label for label, _ in values) / len(values),
            }
        )
    return result


def expected_calibration_error(
    labels: Sequence[int],
    probabilities: Sequence[float],
    *,
    n_bins: int = 10,
) -> float:
    """Compute count-weighted equal-width expected calibration error."""

    bins = reliability_bins(labels, probabilities, n_bins=n_bins)
    total = len(labels)
    return sum(
        (float(item["count"]) / total) * abs(float(item["mean_predicted"]) - float(item["observed_rate"]))
        for item in bins
    )

