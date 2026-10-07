"""Deterministic, as-of-time patient-event graph construction."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Iterable

from .events import Event


@dataclass(frozen=True, slots=True)
class AsOfGraph:
    patient_id: str
    index_time: datetime
    history_start: datetime
    nodes: tuple[dict[str, Any], ...]
    edges: tuple[dict[str, Any], ...]

    def node_ids(self) -> set[str]:
        return {node["id"] for node in self.nodes}


def _node(event: Event, node_type: str, index_time: datetime) -> dict[str, Any]:
    return {
        "id": event.event_id,
        "type": node_type,
        "patient_id": event.patient_id,
        "event_time": event.event_time.isoformat(),
        "age_minutes": (index_time - event.event_time).total_seconds() / 60,
        "value": event.value,
        "unit": event.unit,
        "quality_status": event.quality_status,
        "source_type": event.source_type,
        "source_record_id": event.source_record_id,
    }


def build_asof_graph(
    events: Iterable[Event],
    *,
    patient_id: str,
    index_time: datetime,
    history_minutes: int = 120,
) -> AsOfGraph:
    """Build G(t) using only events in the historical support and available by t."""

    if index_time.tzinfo is None or index_time.utcoffset() is None:
        raise ValueError("index_time must be timezone-aware")
    history_start = index_time - timedelta(minutes=history_minutes)
    def in_support(event: Event) -> bool:
        # Point events use (history_start, t].  An interval that started before
        # the window is retained when it was still active in the window.
        if event.end_time is not None:
            return event.event_time <= index_time and event.end_time > history_start
        return history_start < event.event_time <= index_time

    candidates = [
        event
        for event in events
        if event.patient_id == patient_id
        and in_support(event)
        and event.available_by(index_time)
        and event.quality_status in {"observed_valid", "derived_valid"}
    ]
    candidates.sort(key=lambda event: (event.event_time, event.event_type, event.event_id))
    nodes: list[dict[str, Any]] = [{"id": f"patient:{patient_id}", "type": "PatientContext", "patient_id": patient_id}]
    type_map = {"cgm": "CGMReading", "insulin": "InsulinEvent", "basal": "InsulinEvent", "meal": "MealEvent", "exercise": "ExerciseEvent", "context": "ContextEvent"}
    for event in candidates:
        nodes.append(_node(event, type_map.get(event.event_type, "ContextEvent"), index_time))

    node_ids = {node["id"] for node in nodes}
    edges: list[dict[str, Any]] = []
    patient_node = f"patient:{patient_id}"
    ownership = {"cgm": "has_reading", "insulin": "received", "basal": "received", "meal": "consumed_record", "exercise": "activity_record", "context": "context_record"}
    for event in candidates:
        edges.append({"source": patient_node, "target": event.event_id, "relation": ownership.get(event.event_type, "context_record"), "time_difference_minutes": 0.0})

    cgms = [event for event in candidates if event.event_type == "cgm"]
    for previous, current in zip(cgms, cgms[1:]):
        edges.append({"source": previous.event_id, "target": current.event_id, "relation": "next_observation", "time_difference_minutes": (current.event_time - previous.event_time).total_seconds() / 60})
    for source in candidates:
        if source.event_type not in {"insulin", "meal", "exercise"}:
            continue
        relation = {"insulin": "prior_insulin", "meal": "prior_meal", "exercise": "prior_or_active_activity"}[source.event_type]
        for target in cgms:
            if source.event_time <= target.event_time:
                edges.append({"source": source.event_id, "target": target.event_id, "relation": relation, "time_difference_minutes": (target.event_time - source.event_time).total_seconds() / 60})

    edges.sort(key=lambda edge: (edge["source"], edge["target"], edge["relation"]))
    if any(edge["source"] not in node_ids or edge["target"] not in node_ids for edge in edges):
        raise AssertionError("graph edge references a node outside the as-of graph")
    return AsOfGraph(patient_id, index_time, history_start, tuple(nodes), tuple(edges))
