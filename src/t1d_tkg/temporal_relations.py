"""Deterministic, prediction-time event-to-CGM graph edges.

Relation labels are derived from event modality and admissible time ordering;
they are not independently recorded clinical assertions. This module keeps
that limitation explicit and supplies a NumPy reference implementation for
the GPU model's edge construction.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


HISTORY_STEPS = 24
EVENT_WIDTH = 17
MODALITIES = ("basal", "bolus", "food")


@dataclass(frozen=True)
class TemporalEdges:
    """One edge from each retained event to its nearest observed later CGM slot."""

    target_slot: np.ndarray  # [batch, events], 0 is oldest and 23 is current
    relation_id: np.ndarray  # [batch, events], basal=0, bolus=1, food=2
    elapsed_fraction: np.ndarray  # [batch, events], normalized to 120 minutes
    edge_mask: np.ndarray  # [batch, events], padding is false


def derive_temporal_edges(history_mask: np.ndarray, events: np.ndarray, *,
                          endpoint_policy: str = "nearest") -> TemporalEdges:
    """Derive strictly causal temporal edges for a batch of frozen windows.

    ``endpoint_policy='second-nearest'`` is a causal perturbation used to test
    endpoint sensitivity: choose the next observed CGM point later than the
    event when available, falling back to the nearest admissible point.

    ``events[..., 12]`` stores event age from the prediction index, normalized
    by 120 minutes. History slots are 5-minute grid points oldest-to-current;
    missing slots cannot be targets. For each event, choose the nearest
    observed CGM slot occurring at or after the event. Since age decreases
    toward the current slot, admissible targets satisfy ``cgm_age <= event_age``.
    """

    if endpoint_policy not in ("nearest", "second-nearest"):
        raise ValueError(f"unknown temporal endpoint policy: {endpoint_policy}")
    mask = np.asarray(history_mask)
    event_array = np.asarray(events)
    if mask.ndim != 2 or mask.shape[1] != HISTORY_STEPS:
        raise ValueError(f"history_mask must have shape [batch,{HISTORY_STEPS}]")
    if event_array.ndim != 3 or event_array.shape[0] != mask.shape[0] or event_array.shape[2] != EVENT_WIDTH:
        raise ValueError(f"events must have shape [batch,events,{EVENT_WIDTH}]")
    if not np.isfinite(mask).all() or not np.isfinite(event_array).all():
        raise ValueError("history masks and event features must be finite")
    if np.any((mask != 0) & (mask != 1)):
        raise ValueError("history mask values must be binary")

    active = event_array[:, :, 0] > 0.5
    modalities = event_array[:, :, 1:4]
    if np.any(active & (np.abs(modalities.sum(axis=2) - 1.0) > 1e-6)):
        raise ValueError("every active event must have exactly one known modality")
    if np.any(active & (event_array[:, :, 12] < 0)) or np.any(active & (event_array[:, :, 12] > 1)):
        raise ValueError("active event ages must lie in [0,1]")

    cgm_age = np.arange(HISTORY_STEPS - 1, -1, -1, dtype=np.float64) / 24.0
    event_age = event_array[:, :, 12].astype(np.float64, copy=False)
    delta = event_age[:, :, None] - cgm_age[None, None, :]
    eligible = (mask[:, None, :] > 0.5) & (delta >= -1e-9)
    distance = np.where(eligible, np.maximum(delta, 0.0), np.inf)
    no_target = active & ~eligible.any(axis=2)
    if no_target.any():
        raise ValueError("an active event has no observed, nonfuture CGM target")

    ordered_targets = np.argsort(distance, axis=2, kind="stable")
    nearest_target = ordered_targets[:, :, 0]
    if endpoint_policy == "second-nearest":
        second_target = ordered_targets[:, :, 1]
        has_second = np.isfinite(np.take_along_axis(distance, second_target[:, :, None], axis=2)[:, :, 0])
        target = np.where(has_second, second_target, nearest_target)
    else:
        target = nearest_target
    target = target.astype(np.int16)
    chosen_age = cgm_age[target]
    elapsed = np.where(active, np.maximum(event_age - chosen_age, 0.0), 0.0)
    relation = np.argmax(modalities, axis=2).astype(np.int8)
    target = np.where(active, target, 0).astype(np.int16)
    relation = np.where(active, relation, 0).astype(np.int8)
    return TemporalEdges(target, relation, elapsed.astype(np.float32), active)

