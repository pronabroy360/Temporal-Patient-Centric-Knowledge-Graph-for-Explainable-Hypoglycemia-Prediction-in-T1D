#!/usr/bin/env python3
"""Aggregate paired graph vs aligned-pooling predictions across outer folds.

This computes participant-level differences over the disjoint validation
participants. Its bootstrap conditions on the saved predictions and does not
estimate refit, seed, or cohort uncertainty.
"""

from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path

from compare_loop_pilot_archives import (
    interval,
    metadata,
    prediction_files,
    window_identity,
)
from t1d_tkg.metrics import METRIC_VERSION, average_precision


COMMON_FIELDS = (
    "seed", "epochs", "batch_size", "workers", "history_steps",
    "max_events", "hidden", "trainable_parameters", "manifest_sha256",
    "input_content_sha256", "source_sha256", "optimizer",
    "availability_policy", "evaluation_scope", "metric_version",
)


def load_pair(graph_dir: Path, control_dir: Path, fold: str) -> tuple[dict, list[dict]]:
    graph = metadata(graph_dir, "validation")
    control = metadata(control_dir, "validation")
    expected = {"complete": True, "prediction_identity_verified": True,
                "locked_holdout_used": False, "mode": "train",
                "fixture_only": False}
    for report, variant in ((graph, "graph-generic"),
                            (control, "aligned-nongraph")):
        if any(report.get(key) != value for key, value in expected.items()):
            raise ValueError(f"{fold} {variant} is incomplete, unverified, or uses holdout data")
        if report.get("variant") != variant or report.get("fold") != fold:
            raise ValueError(f"unexpected run identity for {fold} {variant}")
        if report.get("trainable_parameters") != 36_883:
            raise ValueError(f"{fold} {variant} is not the declared capacity match")
    for key in COMMON_FIELDS:
        if graph.get(key) != control.get(key):
            raise ValueError(f"{fold} pair differs in shared field {key}")
    for report in (graph, control):
        group = report["groups"]["validation"]
        if report.get("metric_version") != METRIC_VERSION:
            raise ValueError(f"{fold} has an unexpected metric version")
        if group.get("prediction_window_identity_sha256") is None:
            raise ValueError(f"{fold} lacks prediction identity")
    if window_identity(graph) != window_identity(control):
        raise ValueError(f"{fold} uses different frozen-window identity")

    graph_files = prediction_files(graph_dir, "validation")
    control_files = prediction_files(control_dir, "validation")
    if not graph_files or set(graph_files) != set(control_files):
        raise ValueError(f"{fold} prediction participant sets differ")

    rows: list[dict] = []
    total_windows = total_positive = 0
    for name in sorted(graph_files):
        labels: list[int] = []
        left_scores: list[float] = []
        right_scores: list[float] = []
        with gzip.open(graph_files[name], "rt", encoding="utf-8") as left, \
                gzip.open(control_files[name], "rt", encoding="utf-8") as right:
            for left_line, right_line in zip(left, right, strict=True):
                a, b = json.loads(left_line), json.loads(right_line)
                if (a["patient_id"], a["index_time"], a["label"]) != (
                        b["patient_id"], b["index_time"], b["label"]):
                    raise ValueError(f"{fold} prediction rows do not align")
                labels.append(int(a["label"]))
                left_scores.append(float(a["score"]))
                right_scores.append(float(b["score"]))
        if not labels:
            raise ValueError(f"{fold} contains an empty participant prediction file")
        ap_graph = average_precision(labels, left_scores)
        ap_control = average_precision(labels, right_scores)
        if (ap_graph is None) != (ap_control is None):
            raise ValueError(f"{fold} participant AP-defined status differs between arms")
        brier_graph = sum((p - y) ** 2 for p, y in zip(left_scores, labels, strict=True)) / len(labels)
        brier_control = sum((p - y) ** 2 for p, y in zip(right_scores, labels, strict=True)) / len(labels)
        rows.append({"participant_file": name,
                     "ap_difference": (None if ap_graph is None else
                                       ap_graph - ap_control),
                     "brier_difference": brier_graph - brier_control,
                     "windows": len(labels),
                     "positives": sum(labels),
                     "squared_error_graph": brier_graph * len(labels),
                     "squared_error_control": brier_control * len(labels)})
        total_windows += len(labels)
        total_positive += sum(labels)

    group = graph["groups"]["validation"]
    if (total_windows != group.get("windows") or
            total_positive != group.get("positive_labels") or
            len(rows) != group.get("participants")):
        raise ValueError(f"{fold} prediction totals do not match run metadata")
    return graph, rows


def mean(items: list[float]) -> float:
    return sum(items) / len(items)


def summarize(folds: dict[str, tuple[Path, Path]], *, draws: int,
              bootstrap_seed: int) -> dict:
    all_rows: list[dict] = []
    fold_results: dict[str, dict] = {}
    run_contract: dict | None = None
    fold_differences: dict[str, dict[str, float]] = {}
    for fold in sorted(folds):
        graph_dir, control_dir = folds[fold]
        graph, rows = load_pair(graph_dir, control_dir, fold)
        contract = {key: graph.get(key) for key in COMMON_FIELDS}
        if run_contract is None:
            run_contract = contract
        elif contract != run_contract:
            raise ValueError(f"training contracts differ across folds at {fold}")
        if any(row["participant_file"] == prior["participant_file"]
               for row in rows for prior in all_rows):
            raise ValueError("a validation participant appears in multiple folds")
        all_rows.extend(rows)
        fold_differences[fold] = {
            "participants": len(rows),
            "ap_defined_participants": sum(r["ap_difference"] is not None for r in rows),
            "ap_graph_minus_control": mean([r["ap_difference"] for r in rows
                                             if r["ap_difference"] is not None]),
            "macro_brier_graph_minus_control": mean([r["brier_difference"] for r in rows]),
        }

    ap_deltas = [row["ap_difference"] for row in all_rows
                 if row["ap_difference"] is not None]
    brier_deltas = [row["brier_difference"] for row in all_rows]
    windows = sum(row["windows"] for row in all_rows)
    positives = sum(row["positives"] for row in all_rows)
    squared_graph = sum(row["squared_error_graph"] for row in all_rows)
    squared_control = sum(row["squared_error_control"] for row in all_rows)
    return {
        "audit_type": "two-epoch paired graph vs time-aligned non-graph pooling across outer folds",
        "comparison": "all disjoint validation participants, paired fixed predictions",
        "difference_orientation": "graph-generic minus aligned-nongraph",
        "folds": list(sorted(folds)),
        "fold_results": fold_differences,
        "participants": len(all_rows),
        "ap_defined_participants": len(ap_deltas),
        "windows": windows,
        "positive_labels": positives,
        "manifest_sha256": run_contract["manifest_sha256"],
        "input_content_sha256": run_contract["input_content_sha256"],
        "source_sha256": run_contract["source_sha256"],
        "seed": run_contract["seed"],
        "epochs": run_contract["epochs"],
        "parameters_per_arm": run_contract["trainable_parameters"],
        "locked_holdout_used": False,
        "participant_macro_ap_difference": {
            "graph_minus_control": mean(ap_deltas),
            "fixed_prediction_participant_bootstrap_95_ci": interval(
                ap_deltas, draws=draws, seed=bootstrap_seed),
            "participants_graph_ahead": sum(value > 0 for value in ap_deltas),
            "participants_control_ahead": sum(value < 0 for value in ap_deltas),
        },
        "participant_macro_brier_difference": {
            "graph_minus_control": mean(brier_deltas),
            "fixed_prediction_participant_bootstrap_95_ci": interval(
                brier_deltas, draws=draws, seed=bootstrap_seed + 1),
            "participants_graph_lower_brier": sum(value < 0 for value in brier_deltas),
            "participants_control_lower_brier": sum(value > 0 for value in brier_deltas),
        },
        "pooled_brier_difference_graph_minus_control":
            (squared_graph - squared_control) / windows,
        "policy": (
            "Participants are resampled from the union of five disjoint outer-fold "
            "validation sets. Intervals condition on fixed fitted predictions; "
            "they do not represent seed, refitting, or external-cohort uncertainty."
        ),
        "interpretation": (
            "Development-only comparison of the tested graph message-passing "
            "architecture against same-input, same-timing, exactly parameter-matched "
            "time-bin pooling. It does not establish clinical relation validity, "
            "causal benefit, clinical utility, or general graph ineffectiveness."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--folds", nargs="+", default=["outer-0", "outer-1", "outer-2", "outer-3", "outer-4"])
    parser.add_argument("--draws", type=int, default=10_000)
    parser.add_argument("--bootstrap-seed", type=int, default=20261030)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite {args.output}")
    folds = {
        fold: (args.run_root /
               f"loop_aligned_control_{fold.replace('-', '')}_seed20261030_source_a4d" /
               "graph-generic",
               args.run_root /
               f"loop_aligned_control_{fold.replace('-', '')}_seed20261030_source_a4d" /
               "aligned-nongraph")
        for fold in args.folds
    }
    report = summarize(folds, draws=args.draws,
                       bootstrap_seed=args.bootstrap_seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
