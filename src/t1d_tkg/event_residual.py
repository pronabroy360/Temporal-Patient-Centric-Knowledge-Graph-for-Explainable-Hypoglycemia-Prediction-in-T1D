"""Frozen-predictor logistic residuals for incremental event diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable, Iterable, Iterator

from .logistic import LogisticModel


PRESENCE_QUALITY_FEATURE_NAMES = (
    "basal_record_count", "bolus_record_count", "minutes_since_bolus",
    "food_record_count", "minutes_since_food", "basal_missing_count",
    "bolus_missing_count", "food_missing_count", "latest_basal_unresolved",
)
VALUE_TIMING_FEATURE_NAMES = (
    "basal_record_count", "latest_unambiguous_reported_basal_rate",
    "bolus_record_count", "reported_normal_bolus_units", "minutes_since_bolus",
    "food_record_count", "reported_food_carbs_g", "minutes_since_food",
    "basal_missing_count", "bolus_missing_count", "food_missing_count",
    "latest_basal_unresolved",
)


def residual_features(summary: tuple[float, ...], variant: str) -> tuple[float, ...]:
    """Select prespecified event inputs without changing their as-of semantics."""
    if len(summary) != 12:
        raise ValueError("unexpected captured-event summary width")
    if variant == "presence-quality":
        return tuple(summary[index] for index in (0, 2, 4, 5, 7, 8, 9, 10, 11))
    if variant == "value-timing":
        return summary
    raise ValueError("variant must be presence-quality or value-timing")


def sigmoid(value: float) -> float:
    if value < -35:
        return 0.0
    if value > 35:
        return 1.0
    return 1.0 / (1.0 + math.exp(-value))


@dataclass(frozen=True, slots=True)
class EventResidualModel:
    """An additive event logit branch; all-zero coefficients reproduce CGM."""
    means: tuple[float, ...]
    scales: tuple[float, ...]
    weights: tuple[float, ...]
    intercept: float
    training_prevalence: float

    def offset(self, features: Iterable[float]) -> float:
        values = tuple(float(value) for value in features)
        if len(values) != len(self.weights):
            raise ValueError("event residual feature width differs from model")
        return self.intercept + sum(
            weight * ((value - mean) / scale)
            for value, mean, scale, weight in zip(values, self.means, self.scales, self.weights, strict=True)
        )

    def predict_proba(self, base: LogisticModel, cgm_features: Iterable[float], event_features: Iterable[float]) -> float:
        return sigmoid(base.linear_predictor(cgm_features) + self.offset(event_features))


def fit_streaming_event_residual(
    rows_and_labels: Callable[[], Iterator[tuple[Iterable[float], Iterable[float], int]]],
    base: LogisticModel, *, epochs: int, learning_rate: float, l2: float,
) -> EventResidualModel:
    """Fit an event branch while keeping the supplied CGM predictor immutable."""
    count = positives = width = 0
    sums: list[float] = []
    squared: list[float] = []
    for _, raw_events, label in rows_and_labels():
        events = tuple(float(value) for value in raw_events)
        if width == 0:
            width = len(events); sums = [0.0] * width; squared = [0.0] * width
        if not width or len(events) != width or int(label) not in (0, 1):
            raise ValueError("residual rows require fixed-width event features and binary labels")
        count += 1; positives += int(label)
        for index, value in enumerate(events):
            sums[index] += value; squared[index] += value * value
    if not count:
        raise ValueError("residual stream has no rows")
    means = tuple(value / count for value in sums)
    scales = tuple(max(1e-6, math.sqrt(max(0.0, squared[index] / count - means[index] ** 2))) for index in range(width))
    weights = [0.0] * width
    intercept = 0.0
    for epoch in range(epochs):
        rate = learning_rate / math.sqrt(epoch + 1)
        for cgm, raw_events, label in rows_and_labels():
            events = tuple((float(value) - means[index]) / scales[index] for index, value in enumerate(raw_events))
            probability = sigmoid(base.linear_predictor(cgm) + intercept + sum(weight * value for weight, value in zip(weights, events, strict=True)))
            error = probability - int(label)
            intercept -= rate * error
            for index, value in enumerate(events):
                weights[index] -= rate * (error * value + l2 * weights[index])
    return EventResidualModel(means, scales, tuple(weights), intercept, positives / count)
