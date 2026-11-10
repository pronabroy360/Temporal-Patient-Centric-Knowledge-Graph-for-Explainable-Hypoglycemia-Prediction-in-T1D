#!/usr/bin/env python3
"""Summarize the paired graph/control effect averaged within participant over two seeds."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from compare_loop_pilot_archives import interval, metadata, prediction_files, window_identity
from summarize_graph_aligned_nongraph_folds import load_pair


SEEDS = (20261029, 20261030)
FIRST_SEED_AUDITS = {
    0: "loop_graph_vs_aligned_nongraph_outer0_seed20261029.json",
    1: "loop_graph_vs_aligned_nongraph_outer1_seed20261029.json",
    2: "loop_graph_vs_aligned_nongraph_outer2_seed20261029_current_source_rerun.json",
    3: "loop_graph_vs_aligned_nongraph_outer3_seed20261029_current_source.json",
    4: "loop_graph_vs_aligned_nongraph_outer4_seed20261029_source_a4d.json",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-directory", type=Path, default=Path("audit"))
    parser.add_argument("--draws", type=int, default=10_000)
    parser.add_argument("--bootstrap-seed", type=int, default=20261031)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite {args.output}")

    participant_rows: dict[str, dict] = {}
    fold_summary = {}
    contracts = {}
    source_by_fold = {}
    total_windows = total_positives = 0

    for fold_number in range(5):
        fold = f"outer-{fold_number}"
        pairs = {}
        dirs_by_seed = {}
        for seed in SEEDS:
            if seed == 20261030:
                name = f"loop_graph_vs_aligned_nongraph_outer{fold_number}_seed20261030_source_a4d.json"
            else:
                name = FIRST_SEED_AUDITS[fold_number]
            audit_path = args.audit_directory / name
            audit = json.loads(audit_path.read_text(encoding="utf-8"))
            if (audit.get("comparison_contract") != "loop-graph-vs-time-aligned-nongraph-v1"
                    or audit.get("seed") != seed
                    or audit.get("identifiers_emitted") is not False
                    or audit.get("draws") != 10000
                    or audit.get("parameter_counts") !=
                       {"aligned_nongraph": 36883, "graph_generic": 36883}):
                raise ValueError(f"unexpected strict-pair audit contract: {audit_path}")
            graph_dir = Path(audit["first_archive"])
            control_dir = Path(audit["second_archive"])
            graph, rows = load_pair(graph_dir, control_dir, fold)
            if graph.get("seed") != seed:
                raise ValueError(f"{fold} audit/run training seed mismatch")
            contracts[(fold, seed)] = {
                "source_sha256": graph["source_sha256"],
                "input_content_sha256": graph["input_content_sha256"],
                "manifest_sha256": graph["manifest_sha256"],
                "window_identity_sha256": window_identity(graph),
                "participants": graph["groups"]["validation"]["participants"],
                "windows": graph["groups"]["validation"]["windows"],
                "positive_labels": graph["groups"]["validation"]["positive_labels"],
                "prediction_window_identity_sha256": graph["groups"]["validation"][
                    "prediction_window_identity_sha256"],
                "epochs": graph["epochs"],
                "parameters": graph["trainable_parameters"],
                "locked_holdout_used": graph["locked_holdout_used"],
            }
            dirs_by_seed[seed] = (graph_dir, control_dir)
            pairs[seed] = {
                row["participant_file"]: row for row in rows
            }

        contract_a, contract_b = (contracts[(fold, seed)] for seed in SEEDS)
        for key in ("input_content_sha256", "manifest_sha256", "window_identity_sha256",
                    "participants", "windows", "positive_labels", "epochs", "parameters",
                    "prediction_window_identity_sha256"):
            if contract_a[key] != contract_b[key]:
                raise ValueError(f"{fold} seed contracts differ in {key}")
        if contract_a["locked_holdout_used"] or contract_b["locked_holdout_used"]:
            raise ValueError(f"{fold} unexpectedly used the locked holdout")
        if set(pairs[SEEDS[0]]) != set(pairs[SEEDS[1]]):
            raise ValueError(f"{fold} participant sets differ across seeds")

        files = {}
        for seed in SEEDS:
            graph_dir, control_dir = dirs_by_seed[seed]
            left = prediction_files(graph_dir, "validation")
            right = prediction_files(control_dir, "validation")
            files[seed] = (left, right)
        fold_ap, fold_brier = [], []
        for participant_file in sorted(pairs[SEEDS[0]]):
            first = pairs[SEEDS[0]][participant_file]
            second = pairs[SEEDS[1]][participant_file]
            ap_values = [first["ap_difference"], second["ap_difference"]]
            if (ap_values[0] is None) != (ap_values[1] is None):
                raise ValueError(f"{fold} AP-defined status changes across seeds")
            ap_average = None if ap_values[0] is None else sum(ap_values) / 2
            brier_average = (first["brier_difference"] + second["brier_difference"]) / 2
            participant_rows[participant_file] = {
                "fold": fold,
                "ap_difference_averaged_over_seeds": ap_average,
                "macro_brier_difference_averaged_over_seeds": brier_average,
                "windows": first["windows"],
                "positives": first["positives"],
            }
            if ap_average is not None:
                fold_ap.append(ap_average)
            fold_brier.append(brier_average)
        fold_summary[fold] = {
            "participants": len(fold_brier),
            "ap_defined_participants": len(fold_ap),
            "mean_ap_difference_averaged_over_seeds": sum(fold_ap) / len(fold_ap),
            "mean_macro_brier_difference_averaged_over_seeds": sum(fold_brier) / len(fold_brier),
            "source_sha256": {str(seed): contracts[(fold, seed)]["source_sha256"] for seed in SEEDS},
        }
        total_windows += sum(row["windows"] for row in pairs[SEEDS[0]].values())
        total_positives += sum(row["positives"] for row in pairs[SEEDS[0]].values())
        source_by_fold[fold] = fold_summary[fold]["source_sha256"]

    ap_differences = [row["ap_difference_averaged_over_seeds"]
                      for row in participant_rows.values()
                      if row["ap_difference_averaged_over_seeds"] is not None]
    brier_differences = [row["macro_brier_difference_averaged_over_seeds"]
                         for row in participant_rows.values()]
    report = {
        "audit_type": "two-seed participant-level paired graph vs aligned-pooling summary",
        "difference_orientation": "graph-generic minus aligned-nongraph",
        "seeds": list(SEEDS),
        "folds": [f"outer-{i}" for i in range(5)],
        "fold_results": fold_summary,
        "participants": len(participant_rows),
        "ap_defined_participants": len(ap_differences),
        "windows": total_windows,
        "positive_labels": total_positives,
        "manifest_sha256": next(iter(contracts.values()))["manifest_sha256"],
        "input_content_sha256": next(iter(contracts.values()))["input_content_sha256"],
        "locked_holdout_used": False,
        "participant_macro_ap_difference": {
            "graph_minus_control_after_within_participant_seed_average":
                sum(ap_differences) / len(ap_differences),
            "fixed_prediction_participant_bootstrap_95_ci": interval(
                ap_differences, draws=args.draws, seed=args.bootstrap_seed),
            "control_ahead": sum(value < 0 for value in ap_differences),
            "graph_ahead": sum(value > 0 for value in ap_differences),
        },
        "participant_macro_brier_difference": {
            "graph_minus_control_after_within_participant_seed_average":
                sum(brier_differences) / len(brier_differences),
            "fixed_prediction_participant_bootstrap_95_ci": interval(
                brier_differences, draws=args.draws, seed=args.bootstrap_seed + 1),
            "control_lower_brier": sum(value > 0 for value in brier_differences),
            "graph_lower_brier": sum(value < 0 for value in brier_differences),
        },
        "source_sha256_by_fold_and_seed": source_by_fold,
        "policy": (
            "For each participant, average the paired fixed-model metric differences "
            "across two seeds before participant bootstrap. The same participants and "
            "fold assignments occur at each seed; folds are not independent cohorts."
        ),
        "interpretation": (
            "Development-only participant-level summary for the two fitted seeds. "
            "Intervals condition on these predictions and do not estimate training "
            "seed, refitting, or external-cohort uncertainty."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
