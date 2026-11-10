#!/usr/bin/env python3
"""Strictly compare paired full-history graph and non-graph sequence predictions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from compare_controlled_neural_archives import _check_reported_metrics
from compare_loop_pilot_archives import compare, metadata, window_identity


GRAPH_VARIANT = "graph-generic"
SEQUENCE_VARIANT = "history-event-capacity-matched"
EXPECTED_PARAMETERS = 36_883
COMMON_FIELDS = (
    "fold", "seed", "epochs", "batch_size", "workers", "max_events",
    "history_steps", "manifest_sha256", "input_content_sha256",
    "training_membership_sha256", "train_windows_expected",
    "train_positive_labels_expected", "evaluation_scope", "metric_version",
)


def optimizer_signature(report: dict) -> tuple:
    optimizer = report.get("optimizer")
    if not isinstance(optimizer, dict):
        raise ValueError("archive is missing optimizer metadata")
    keys = ("name", "learning_rate", "weight_decay", "loss")
    if any(key not in optimizer for key in keys):
        raise ValueError("archive has an incomplete optimizer contract")
    # Some full-history reports explicitly serialize the default positive
    # weight while relation reports omit it. Require the same effective value.
    positive_weight = optimizer.get("positive_weight", 1.0)
    return (*(optimizer[key] for key in keys), positive_weight)


def availability_signature(report: dict) -> str:
    value = report.get("availability_policy")
    if not isinstance(value, str):
        raise ValueError("archive is missing event-availability metadata")
    normalized = value.lower().replace("-", " ")
    if "occurrence time" not in normalized or "immediate availability assumed" not in normalized:
        raise ValueError("both runs must use occurrence-time replay with the same immediate-availability assumption")
    return "retrospective occurrence time; immediate availability assumed, not measured"


def validate_run(report: dict, variant: str, group: str) -> None:
    if report.get("variant") != variant:
        raise ValueError(f"expected {variant} archive")
    if (report.get("mode") != "train" or report.get("fixture_only") is not False
            or report.get("complete") is not True
            or report.get("prediction_identity_verified") is not True
            or report.get("locked_holdout_used") is not False):
        raise ValueError("comparison requires complete verified development training runs")
    if group not in report.get("groups", {}):
        raise ValueError(f"archive is missing the {group} group")
    if report.get("trainable_parameters") != EXPECTED_PARAMETERS:
        raise ValueError("both models must have exactly 36,883 trainable parameters")


def compare_graph_sequence(graph_directory: Path, sequence_directory: Path,
                           *, draws: int = 2000, seed: int = 20261003) -> dict:
    group = "validation"
    graph = metadata(graph_directory, group)
    sequence = metadata(sequence_directory, group)
    validate_run(graph, GRAPH_VARIANT, group)
    validate_run(sequence, SEQUENCE_VARIANT, group)

    if any(graph.get(key) is None or sequence.get(key) is None
           for key in COMMON_FIELDS):
        raise ValueError("one archive has an incomplete shared training contract")
    mismatches = [key for key in COMMON_FIELDS if graph[key] != sequence[key]]
    if mismatches:
        raise ValueError("graph and sequence runs differ in: " + ", ".join(mismatches))
    if optimizer_signature(graph) != optimizer_signature(sequence):
        raise ValueError("graph and sequence optimizer settings differ")
    if availability_signature(graph) != availability_signature(sequence):
        raise ValueError("graph and sequence event-availability assumptions differ")
    if window_identity(graph) != window_identity(sequence):
        raise ValueError("graph and sequence runs use different frozen windows")
    graph_metrics = graph["groups"][group]
    sequence_metrics = sequence["groups"][group]
    if graph_metrics.get("prediction_window_identity_sha256") != sequence_metrics.get(
            "prediction_window_identity_sha256"):
        raise ValueError("graph and sequence prediction identities differ")
    for key in ("participants", "windows", "positive_labels"):
        if graph_metrics.get(key) != sequence_metrics.get(key):
            raise ValueError(f"validation {key} counts differ")

    paired = compare(graph_directory, sequence_directory, group=group,
                     draws=draws, seed=seed)
    _check_reported_metrics(graph, paired, "first", group)
    _check_reported_metrics(sequence, paired, "second", group)
    paired.update({
        "comparison_contract": "loop-graph-vs-sequence-capacity-matched-v1",
        "first_variant": GRAPH_VARIANT,
        "second_variant": SEQUENCE_VARIANT,
        "parameter_counts": {"graph_generic": EXPECTED_PARAMETERS,
                             "non_graph_sequence": EXPECTED_PARAMETERS},
        "training_contract": {
            key: graph[key] for key in COMMON_FIELDS
        } | {"optimizer": graph["optimizer"],
             "availability_policy": availability_signature(graph),
             "input_content_sha256": graph["input_content_sha256"],
             "window_identity_sha256": window_identity(graph),
             "prediction_window_identity_sha256": graph_metrics[
                 "prediction_window_identity_sha256"]},
        "source_sha256": {"graph_generic": graph.get("source_sha256"),
                          "non_graph_sequence": sequence.get("source_sha256")},
        "interpretation": (
            "Development-only paired fixed-prediction comparison. Exact input, "
            "split, event budget, training budget, optimizer and parameter count "
            "are required. A graph advantage is evidence for this graph "
            "parameterization only; it does not establish novel clinical facts, "
            "general graph superiority, causal event effects, or explanation "
            "faithfulness. Participant bootstrap conditions on these fitted models."
        ),
    })
    return paired


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graph_generic", type=Path)
    parser.add_argument("non_graph_sequence", type=Path)
    parser.add_argument("--draws", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20261003)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("comparison output already exists")
    result = compare_graph_sequence(args.graph_generic, args.non_graph_sequence,
                                   draws=args.draws, seed=args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
