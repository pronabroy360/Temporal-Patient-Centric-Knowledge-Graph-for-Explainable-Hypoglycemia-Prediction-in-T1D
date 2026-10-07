"""Fixed-width summaries for transparent graph control experiments."""

from __future__ import annotations

from collections import Counter
from typing import Iterable, Literal

from .events import Event
from .graph import AsOfGraph, build_asof_graph
from .windows import WindowSample


NODE_TYPES = ("PatientContext", "CGMReading", "InsulinEvent", "MealEvent", "ExerciseEvent", "ContextEvent")
RELATIONS = (
    "has_reading",
    "received",
    "consumed_record",
    "activity_record",
    "context_record",
    "next_observation",
    "prior_insulin",
    "prior_meal",
    "prior_or_active_activity",
)
GENERIC_RELATIONS = ("ownership", "temporal", "prior")
RelationMode = Literal["typed", "generic", "none"]


def _relation_bucket(relation: str, mode: RelationMode) -> str | None:
    if mode == "none":
        return None
    if mode == "typed":
        return relation
    if relation in {"has_reading", "received", "consumed_record", "activity_record", "context_record"}:
        return "ownership"
    if relation == "next_observation":
        return "temporal"
    return "prior"


def graph_summary(graph: AsOfGraph, *, relation_mode: RelationMode = "typed") -> tuple[float, ...]:
    """Summarize an as-of graph without fitting statistics across patients.

    The vector contains node-type counts, relation counts, and simple age/time
    summaries. It is a control feature set, not a learned graph encoder.
    """

    if relation_mode not in {"typed", "generic", "none"}:
        raise ValueError("relation_mode must be 'typed', 'generic', or 'none'")
    node_counts = Counter(node["type"] for node in graph.nodes)
    relation_counts = Counter(_relation_bucket(edge["relation"], relation_mode) for edge in graph.edges)
    values: list[float] = [float(node_counts[node_type]) for node_type in NODE_TYPES]
    values.extend(float(relation_counts[relation]) for relation in (RELATIONS if relation_mode == "typed" else GENERIC_RELATIONS))
    if relation_mode != "typed":
        values.extend([0.0] * (len(RELATIONS) - len(GENERIC_RELATIONS)))
    ages = [float(node["age_minutes"]) for node in graph.nodes if "age_minutes" in node]
    edge_times = [float(edge["time_difference_minutes"]) for edge in graph.edges]
    values.extend([min(120.0, max(0.0, sum(ages) / len(ages))) if ages else 0.0, max(ages, default=0.0)])
    values.extend([sum(edge_times) / len(edge_times) if edge_times else 0.0, max(edge_times, default=0.0)])
    return tuple(values)


def graph_summary_for_sample(
    sample: WindowSample,
    events: Iterable[Event],
    *,
    relation_mode: RelationMode = "typed",
) -> tuple[float, ...]:
    """Build and summarize exactly the graph admissible at ``sample.index_time``."""

    graph = build_asof_graph(
        events,
        patient_id=sample.patient_id,
        index_time=sample.index_time,
        history_minutes=int((sample.index_time - sample.history_start).total_seconds() // 60),
    )
    return graph_summary(graph, relation_mode=relation_mode)
