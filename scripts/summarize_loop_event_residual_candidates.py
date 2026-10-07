#!/usr/bin/env python3
"""Validate and select among the prespecified outer-0 residual candidates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from t1d_tkg.metrics import METRIC_VERSION


EXPECTED_VARIANTS = ("presence-quality", "value-timing")
EXPECTED_L2 = (0.0001, 0.001, 0.01)
EXPECTED_EPOCHS = (1, 2)


def candidate_key(report: dict[str, object]) -> tuple[str, float, int]:
    return str(report["variant"]), float(report["l2"]), int(report["epochs"])


def summarize(paths: list[Path]) -> dict[str, object]:
    expected = {(variant, l2, epochs) for variant in EXPECTED_VARIANTS for l2 in EXPECTED_L2 for epochs in EXPECTED_EPOCHS}
    reports = [(path, json.loads(path.read_text(encoding="utf-8"))) for path in paths]
    observed = {candidate_key(report) for _, report in reports}
    if len(reports) != len(observed) or observed != expected:
        raise ValueError("reports must contain each of the twelve prespecified residual candidates exactly once")
    reference = None
    rows = []
    for path, report in reports:
        if report.get("model") != "frozen_cgm_event_logit_residual" or report.get("metric_version") != METRIC_VERSION:
            raise ValueError("report is not a corrected frozen-CGM residual result")
        group = report.get("groups", {}).get("validation")
        if not isinstance(group, dict):
            raise ValueError("residual reports must contain validation results")
        frozen = group.get("frozen_cgm")
        residual = group.get("event_residual")
        if not isinstance(frozen, dict) or not isinstance(residual, dict):
            raise ValueError("residual report lacks paired metrics")
        current = (
            report.get("fold"), report.get("manifest_sha256"), report.get("window_verification", {}).get("window_identity_sha256"),
            group.get("participants"), group.get("windows"), group.get("positive_labels"),
            frozen.get("participant_macro_ap"), frozen.get("brier_score"),
        )
        if reference is None:
            reference = current
        elif current != reference:
            raise ValueError("candidate reports do not share an identical frozen-CGM validation contract")
        rows.append({
            "file": str(path),
            "variant": report["variant"], "l2": report["l2"], "epochs": report["epochs"],
            "participant_macro_ap": residual["participant_macro_ap"], "brier_score": residual["brier_score"],
            "ap_difference_from_frozen_cgm": residual["participant_macro_ap"] - frozen["participant_macro_ap"],
            "brier_difference_from_frozen_cgm": residual["brier_score"] - frozen["brier_score"],
        })
    rows.sort(key=lambda row: (-float(row["participant_macro_ap"]), float(row["brier_score"]), 0 if row["variant"] == "presence-quality" else 1, float(row["l2"]), int(row["epochs"])))
    return {
        "selection_policy": "higher participant-macro AP, then lower Brier, then presence-quality, lower L2, fewer epochs",
        "metric_version": METRIC_VERSION,
        "frozen_cgm_validation_contract": {"fold": reference[0], "manifest_sha256": reference[1], "window_identity_sha256": reference[2], "participants": reference[3], "windows": reference[4], "positive_labels": reference[5], "participant_macro_ap": reference[6], "brier_score": reference[7]},
        "candidates": rows,
        "selected_candidate": rows[0],
        "policy": "Development-only selection. No development-test or locked-holdout metric is read or emitted.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=Path("audit"))
    parser.add_argument("--pattern", default="loop_event_residual_outer0_*.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("choose a new summary output path")
    result = summarize(sorted(args.directory.glob(args.pattern)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
