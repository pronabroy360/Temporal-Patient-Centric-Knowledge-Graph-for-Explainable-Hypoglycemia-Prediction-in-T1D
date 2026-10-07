"""Provenance-safe evidence records and graph masking helpers."""

from __future__ import annotations

from typing import Iterable

from .graph import AsOfGraph


def evidence_record(
    graph: AsOfGraph,
    node_ids: Iterable[str],
    *,
    model_name: str,
    model_version: str,
    prediction: float,
) -> dict[str, object]:
    """Create a serializable evidence record from nodes in an as-of graph."""

    selected_ids = sorted(set(node_ids))
    nodes_by_id = {node["id"]: node for node in graph.nodes}
    missing = [node_id for node_id in selected_ids if node_id not in nodes_by_id]
    if missing:
        raise ValueError(f"evidence references nodes outside the as-of graph: {missing}")
    evidence = []
    for node_id in selected_ids:
        node = nodes_by_id[node_id]
        evidence.append(
            {
                "id": node["id"],
                "type": node["type"],
                "patient_id": node.get("patient_id"),
                "event_time": node.get("event_time"),
                "age_minutes": node.get("age_minutes"),
                "value": node.get("value"),
                "unit": node.get("unit"),
                "source_type": node.get("source_type"),
                "source_record_id": node.get("source_record_id"),
            }
        )
    return {
        "patient_id": graph.patient_id,
        "prediction_index_time": graph.index_time.isoformat(),
        "model_name": model_name,
        "model_version": model_version,
        "prediction": float(prediction),
        "evidence_nodes": evidence,
    }


def remove_evidence_nodes(graph: AsOfGraph, node_ids: Iterable[str]) -> AsOfGraph:
    """Return a graph with selected evidence nodes and incident edges removed."""

    remove = set(node_ids)
    patient_node = f"patient:{graph.patient_id}"
    if patient_node in remove:
        raise ValueError("PatientContext cannot be removed from an evidence mask")
    known = graph.node_ids()
    unknown = remove - known
    if unknown:
        raise ValueError(f"mask references nodes outside the as-of graph: {sorted(unknown)}")
    nodes = tuple(node for node in graph.nodes if node["id"] not in remove)
    edges = tuple(edge for edge in graph.edges if edge["source"] not in remove and edge["target"] not in remove)
    return AsOfGraph(graph.patient_id, graph.index_time, graph.history_start, nodes, edges)

