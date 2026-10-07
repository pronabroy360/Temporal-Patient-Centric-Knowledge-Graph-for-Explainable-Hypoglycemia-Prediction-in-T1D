#!/usr/bin/env python3
"""Aggregate frozen development-test results from the five CGM logistic folds."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from t1d_tkg.metrics import METRIC_VERSION


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-directory", type=Path, default=Path("audit"))
    parser.add_argument(
        "--filename-template", default="loop_cgm_logistic_outer{fold}_development_test.json",
        help="input filename pattern containing {fold}",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if "{fold}" not in args.filename_template:
        raise ValueError("--filename-template must contain {fold}")
    if args.output.exists():
        raise FileExistsError("summary output already exists")
    rows = []
    for number in range(5):
        path = args.input_directory / args.filename_template.format(fold=number)
        report = json.loads(path.read_text(encoding="utf-8"))
        if report.get("fold") != f"outer-{number}" or "development_test" not in report.get("groups", {}):
            raise ValueError(f"invalid development-test artifact: {path}")
        if set(report["groups"]) != {"development_test"}:
            raise ValueError(f"artifact must contain development-test predictions only: {path}")
        if report.get("metric_version") != METRIC_VERSION:
            raise ValueError("legacy AP artifact: corrected predictions must be rescored first")
        rows.append(report)
    checksums = {str(row["manifest_sha256"]) for row in rows}
    configurations = {(row["epochs"], row["learning_rate"], tuple(row["features"])) for row in rows}
    if len(checksums) != 1 or len(configurations) != 1:
        raise ValueError("fold artifacts do not share one manifest and frozen configuration")
    models = ("persistence_slope_rule", "streaming_logistic")
    total_participants = sum(row["groups"]["development_test"]["participants"] for row in rows)
    total_windows = sum(row["groups"]["development_test"]["windows"] for row in rows)
    summary_models = {}
    for model in models:
        denominator = sum(row["groups"]["development_test"][model]["ap_defined_participants"] for row in rows)
        macro_ap = sum(row["groups"]["development_test"][model]["ap_defined_participants"] * (row["groups"]["development_test"][model]["participant_macro_ap"] or 0.0) for row in rows) / denominator if denominator else None
        brier = sum(row["groups"]["development_test"]["windows"] * row["groups"]["development_test"][model]["brier_score"] for row in rows) / total_windows
        summary_models[model] = {"ap_defined_participants": denominator, "participant_macro_ap": macro_ap, "pooled_brier_score": brier}
    report = {
        "metric_version": METRIC_VERSION,
        "evaluation": "five-fold patient-disjoint development-test aggregation",
        "identifiers_emitted": False,
        "manifest_sha256": checksums.pop(),
        "configuration": {"epochs": rows[0]["epochs"], "learning_rate": rows[0]["learning_rate"], "features": rows[0]["features"]},
        "participants": total_participants, "windows": total_windows,
        "positive_labels": sum(row["groups"]["development_test"]["positive_labels"] for row in rows),
        "models": summary_models,
        "folds": [{"fold": row["fold"], **row["groups"]["development_test"]} for row in rows],
        "policy": "Development-only out-of-fold summary. The locked holdout is not included.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
