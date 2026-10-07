"""Small dependency-free logistic regression for smoke benchmarks."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable, Iterable, Iterator


def _sigmoid(value: float) -> float:
    if value < -35:
        return 0.0
    if value > 35:
        return 1.0
    return 1.0 / (1.0 + math.exp(-value))


@dataclass(frozen=True, slots=True)
class LogisticModel:
    means: tuple[float, ...]
    scales: tuple[float, ...]
    weights: tuple[float, ...]
    intercept: float
    training_prevalence: float | None = None

    def linear_predictor(self, row: Iterable[float]) -> float:
        values = tuple(float(value) for value in row)
        if len(values) != len(self.weights):
            raise ValueError("feature width differs from model")
        return self.intercept + sum(
            weight * ((value - mean) / scale)
            for value, mean, scale, weight in zip(values, self.means, self.scales, self.weights, strict=True)
        )

    def predict_proba(self, rows: Iterable[Iterable[float]]) -> list[float]:
        probabilities = []
        for row in rows:
            probabilities.append(_sigmoid(self.linear_predictor(row)))
        return probabilities


def fit_logistic(
    rows: Iterable[Iterable[float]],
    labels: Iterable[int],
    *,
    learning_rate: float = 0.05,
    epochs: int = 1200,
    l2: float = 1e-3,
) -> LogisticModel:
    """Fit a small L2-regularized binary logistic model.

    This is intended for a transparent smoke benchmark. Hyperparameters must
    be selected inside training folds for scientific evaluation.
    """

    x = [tuple(float(value) for value in row) for row in rows]
    y = [int(label) for label in labels]
    if not x or not y or len(x) != len(y):
        raise ValueError("rows and labels must be non-empty and have equal length")
    width = len(x[0])
    if width == 0 or any(len(row) != width for row in x):
        raise ValueError("all rows must have the same non-zero width")
    means = tuple(sum(row[col] for row in x) / len(x) for col in range(width))
    scales = tuple(max(1e-6, math.sqrt(sum((row[col] - means[col]) ** 2 for row in x) / len(x))) for col in range(width))
    z = [tuple((row[col] - means[col]) / scales[col] for col in range(width)) for row in x]
    weights = [0.0] * width
    intercept = math.log((sum(y) + 0.5) / (len(y) - sum(y) + 0.5))
    for _ in range(epochs):
        probabilities = [_sigmoid(intercept + sum(weights[col] * row[col] for col in range(width))) for row in z]
        error = [probability - label for probability, label in zip(probabilities, y)]
        intercept -= learning_rate * sum(error) / len(y)
        for col in range(width):
            gradient = sum(error[row] * z[row][col] for row in range(len(y))) / len(y) + l2 * weights[col]
            weights[col] -= learning_rate * gradient
    return LogisticModel(means, scales, tuple(weights), intercept, sum(y) / len(y))


def fit_streaming_logistic(
    rows_and_labels: Callable[[], Iterator[tuple[Iterable[float], int]]], *,
    epochs: int = 3, learning_rate: float = 0.02, l2: float = 1e-4, positive_weight: float = 1.0,
) -> LogisticModel:
    """Fit a standardized logistic model from repeatable streaming passes.

    The factory must return rows in a deterministic order on every call. This
    keeps large release-backed fitting memory-bounded and makes the class
    weighting choice explicit.
    """
    count = positives = width = 0
    sums: list[float] = []
    squared: list[float] = []
    for raw_row, label in rows_and_labels():
        row = tuple(float(value) for value in raw_row)
        if width == 0:
            width = len(row); sums = [0.0] * width; squared = [0.0] * width
        if len(row) != width or width == 0:
            raise ValueError("all rows must have the same non-zero width")
        count += 1; positives += int(label)
        for index, value in enumerate(row):
            sums[index] += value; squared[index] += value * value
    if count == 0:
        raise ValueError("stream has no rows")
    means = tuple(value / count for value in sums)
    scales = tuple(max(1e-6, math.sqrt(max(0.0, squared[index] / count - means[index] ** 2))) for index in range(width))
    weights = [0.0] * width
    intercept = math.log((positives + 0.5) / (count - positives + 0.5))
    for epoch in range(epochs):
        rate = learning_rate / math.sqrt(epoch + 1)
        for raw_row, label in rows_and_labels():
            row = tuple((float(value) - means[index]) / scales[index] for index, value in enumerate(raw_row))
            probability = _sigmoid(intercept + sum(weight * value for weight, value in zip(weights, row)))
            error = (probability - int(label)) * (positive_weight if int(label) else 1.0)
            intercept -= rate * error
            for index, value in enumerate(row):
                weights[index] -= rate * (error * value + l2 * weights[index])
    return LogisticModel(means, scales, tuple(weights), intercept, positives / count)
