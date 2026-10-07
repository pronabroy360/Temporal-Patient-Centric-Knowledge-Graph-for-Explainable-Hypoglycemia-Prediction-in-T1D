#!/usr/bin/env python3
"""Compare the fixed CGM MLP and clean event GRU on paired validation windows.

This reads protected participant predictions locally. It emits aggregate metrics
only and refuses comparisons across different folds, seeds, inputs, or runs.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from compare_loop_pilot_archives import compare, metadata, window_identity
from t1d_tkg.neural_contract import CONTRACT_VERSION


MATCHED_FIELDS = (
    "contract_version", "fold", "seed", "hidden", "epochs", "batch_size",
    "workers", "max_events", "manifest_sha256", "window_identity_sha256",
    "input_content_sha256", "training_membership_sha256", "optimizer",
    "source_sha256", "event_input_policy", "evaluation_scope",
    "metric_version", "prediction_window_identity_sha256",
)


def _contract(report: dict, group: str) -> dict:
    values = {key: report.get(key) for key in MATCHED_FIELDS}
    values["window_identity_sha256"] = window_identity(report)
    values["prediction_window_identity_sha256"] = report["groups"][group].get(
        "prediction_window_identity_sha256"
    )
    if any(value is None for value in values.values()):
        raise ValueError("controlled-neural archive is missing a comparison contract field")
    return values


def _check_reported_metrics(report: dict, result: dict, side: str, group: str) -> None:
    reported = report["groups"][group]
    checks = (
        ("participant_macro_ap", "participant_macro_ap"),
        ("participant_macro_brier", "participant_macro_brier"),
        ("pooled_brier", "pooled_brier"),
    )
    for key, comparison_key in checks:
        actual = result[comparison_key][side]
        claimed = reported.get(key)
        if not isinstance(claimed, (int, float)) or not math.isclose(
            actual, claimed, rel_tol=1e-8, abs_tol=1e-10
        ):
            raise ValueError(f"{side} archive's reported {key} differs from its predictions")
    if result["participants"] != reported.get("participants"):
        raise ValueError(f"{side} archive participant count differs from predictions")
    if result["participant_macro_ap"]["participants"] != reported.get("ap_defined_participants"):
        raise ValueError(f"{side} archive AP denominator differs from predictions")


def compare_first_gate(
    cgm_mlp: Path, clean_gru: Path, *, draws: int = 2000, seed: int = 20261002
) -> dict:
    group = "validation"
    baseline = metadata(cgm_mlp, group)
    event = metadata(clean_gru, group)
    if baseline.get("contract_version") != CONTRACT_VERSION or event.get("contract_version") != CONTRACT_VERSION:
        raise ValueError("both archives must use the controlled-neural contract")
    if baseline.get("variant") != "cgm-mlp" or event.get("variant") != "clean-gru":
        raise ValueError("first archive must be cgm-mlp and second clean-gru")
    if not baseline.get("prediction_identity_verified") or not event.get("prediction_identity_verified"):
        raise ValueError("a model did not complete independent prediction-identity verification")
    if baseline.get("fixture_only") or event.get("fixture_only"):
        raise ValueError("software fixtures are not research-scale first-gate results")
    if baseline.get("mode") != "train" or event.get("mode") != "train":
        raise ValueError("first-gate comparison requires completed training runs")
    if _contract(baseline, group) != _contract(event, group):
        raise ValueError("controlled-neural archives differ in fold, seed, inputs, code, or configuration")

    result = compare(cgm_mlp, clean_gru, group=group, draws=draws, seed=seed)
    _check_reported_metrics(baseline, result, "first", group)
    _check_reported_metrics(event, result, "second", group)
    result["first_variant"] = "cgm-mlp"
    result["second_variant"] = "clean-gru"
    result["contract_version"] = CONTRACT_VERSION
    result["interpretation"] = "Development validation only; fixed-prediction paired intervals do not measure training variability or establish relation benefit."
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cgm_mlp", type=Path)
    parser.add_argument("clean_gru", type=Path)
    parser.add_argument("--draws", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20261002)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("comparison output already exists")
    result = compare_first_gate(args.cgm_mlp, args.clean_gru, draws=args.draws, seed=args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
