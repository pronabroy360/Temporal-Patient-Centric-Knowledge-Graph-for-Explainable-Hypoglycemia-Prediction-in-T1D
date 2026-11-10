#!/usr/bin/env python3
"""No-refit transfer pilot of a frozen Loop CGM logistic model to Jaeb DCLP.

This evaluates CGM-only predictions. It is not a graph/event model transfer,
does not tune or recalibrate on the external cohort, and writes aggregate-only
metrics without participant identifiers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

import numpy as np

from audit_jaeb_eligible_windows import (
    FUTURE_STEPS, GRID_SEC, GRID_TOLERANCE_SEC, HISTORY_STEPS,
    canonical_patient_rows, parse_cgm,
)
from t1d_tkg.baselines import persistence_slope_score_from_current_and_slope
from t1d_tkg.features import cgm_recent_features
from t1d_tkg.logistic import LogisticModel
from t1d_tkg.metrics import average_precision


def eligible_positions(tt: np.ndarray) -> np.ndarray:
    if len(tt) < HISTORY_STEPS + FUTURE_STEPS + 1:
        return np.asarray([], dtype=np.int64)
    gaps = np.diff(tt)
    regular = (gaps >= GRID_SEC - GRID_TOLERANCE_SEC) & (gaps <= GRID_SEC + GRID_TOLERANCE_SEC)
    bad_prefix = np.r_[0, np.cumsum(~regular, dtype=np.int32)]
    anchors = np.arange(HISTORY_STEPS, len(tt) - FUTURE_STEPS, dtype=np.int64)
    left = anchors - HISTORY_STEPS
    right_interval = anchors + FUTURE_STEPS - 1
    continuous = bad_prefix[right_interval + 1] - bad_prefix[left] == 0
    continuous &= np.abs((tt[anchors] - tt[left]) - 7200) <= GRID_TOLERANCE_SEC
    continuous &= np.abs((tt[anchors + FUTURE_STEPS] - tt[anchors]) - 1800) <= GRID_TOLERANCE_SEC
    return anchors[continuous]


def mean_and_fixed_prediction_ci(values: list[float], seed: int = 20261031,
                                 draws: int = 2000) -> dict:
    if not values:
        return {"mean": None, "bootstrap_95_ci": [None, None], "participants": 0}
    rng = random.Random(seed)
    n = len(values)
    means = [sum(values[rng.randrange(n)] for _ in range(n)) / n for _ in range(draws)]
    return {
        "mean": sum(values) / n,
        "bootstrap_95_ci": [float(np.quantile(means, .025)), float(np.quantile(means, .975))],
        "participants": n,
    }


def evaluate_dataset(data_root: Path, dataset: str, timestamp_policy: str,
                     models: dict[str, tuple[LogisticModel, float]]) -> dict:
    cgm_report, people, codes, stamps, values, statuses = parse_cgm(
        data_root, dataset, timestamp_policy
    )
    participants = len(people)
    rows_by_person = np.bincount(codes, minlength=participants)
    starts = np.r_[0, np.cumsum(rows_by_person[:-1])]
    totals = {name: {"windows": 0, "positives": 0, "brier_sum": 0.0,
                     "ap_sum": 0.0, "ap_defined": 0,
                     "participant_briers": [], "participant_aps": []}
              for name in [*models, "persistence_slope"]}
    participant_diffs = {name: {"macro_ap": [], "macro_brier": [],
                                "prevalence_brier": []} for name in models}
    eligible_participants = positive_participants = 0
    for code in range(participants):
        begin = int(starts[code]); end = begin + int(rows_by_person[code])
        pt, pv, ps, _, _ = canonical_patient_rows(stamps, values, statuses, begin, end)
        usable = (ps == 0) & (pv >= 20.0) & (pv <= 600.0)
        tt = pt[usable]; vv = pv[usable]
        anchors = eligible_positions(tt)
        if not len(anchors):
            continue
        labels = (np.lib.stride_tricks.sliding_window_view(vv, FUTURE_STEPS + 1)[:, 1:] < 70.0).any(axis=1)[anchors].astype(np.int8)
        current = vv[anchors]
        previous = vv[anchors - 1]
        elapsed_steps = np.maximum(1e-6, (tt[anchors] - tt[anchors - 1]) / 300.0)
        slopes = (current - previous) / elapsed_steps
        features = list(zip(current.tolist(), slopes.tolist(), strict=True))
        rule_scores = [persistence_slope_score_from_current_and_slope(
            row[0], row[1], horizon_minutes=30
        ) for row in features]
        logistic_scores = {name: model.predict_proba(features)
                           for name, (model, _) in models.items()}
        eligible_participants += 1
        positive_participants += bool(labels.sum())
        person_briers = {}
        person_aps = {}
        all_scores = {**logistic_scores, "persistence_slope": rule_scores}
        for name, scores in all_scores.items():
            state = totals[name]
            state["windows"] += int(len(labels))
            state["positives"] += int(labels.sum())
            errors = [(float(score) - int(label)) ** 2
                      for label, score in zip(labels, scores, strict=True)]
            person_briers[name] = sum(errors) / len(errors)
            state["brier_sum"] += sum(errors)
            state["participant_briers"].append(person_briers[name])
            ap = average_precision(labels.tolist(), scores)
            person_aps[name] = ap
            if ap is not None:
                state["ap_sum"] += ap
                state["ap_defined"] += 1
                state["participant_aps"].append(ap)
        for name, (_, training_prevalence) in models.items():
            prevalence_errors = [(training_prevalence - int(label)) ** 2 for label in labels]
            participant_diffs[name]["macro_brier"].append(
                person_briers[name] - person_briers["persistence_slope"])
            participant_diffs[name]["prevalence_brier"].append(
                person_briers[name] - sum(prevalence_errors) / len(prevalence_errors))
            if person_aps[name] is not None and person_aps["persistence_slope"] is not None:
                participant_diffs[name]["macro_ap"].append(
                    person_aps[name] - person_aps["persistence_slope"])
    if not any(totals[name]["windows"] for name in totals):
        raise RuntimeError("no eligible external windows were generated")
    groups = {}
    for name, state in totals.items():
        windows = state["windows"]
        groups[name] = {
            "participants": eligible_participants,
            "participants_with_positive_label": positive_participants,
            "ap_defined_participants": state["ap_defined"],
            "participant_macro_ap": state["ap_sum"] / state["ap_defined"] if state["ap_defined"] else None,
            "participant_macro_ap_fixed_prediction_bootstrap_95_ci": mean_and_fixed_prediction_ci(
                state["participant_aps"]),
            "participant_macro_brier_score": sum(state["participant_briers"]) / len(state["participant_briers"]),
            "participant_macro_brier_fixed_prediction_bootstrap_95_ci": mean_and_fixed_prediction_ci(
                state["participant_briers"], seed=20261032),
            "global_brier_score": state["brier_sum"] / windows if windows else None,
            "windows": windows, "positive_labels": state["positives"],
            "positive_prevalence": state["positives"] / windows if windows else None,
        }
    references = {}
    for name, (_, training_prevalence) in models.items():
        logistic = groups[name]
        reference_brier = None
        if logistic["windows"]:
            reference_brier = (((logistic["windows"] - logistic["positive_labels"]) * training_prevalence ** 2)
                               + logistic["positive_labels"] * (1 - training_prevalence) ** 2) / logistic["windows"]
        references[name] = {"probability": training_prevalence,
                            "global_brier_score": reference_brier}
    paired = {}
    for name, deltas in participant_diffs.items():
        paired[name] = {
            "loop_logistic_minus_persistence_slope": {
                "participant_macro_ap": mean_and_fixed_prediction_ci(deltas["macro_ap"], seed=20261033),
                "participant_macro_brier": mean_and_fixed_prediction_ci(deltas["macro_brier"], seed=20261034),
            },
            "loop_logistic_minus_training_prevalence_brier": mean_and_fixed_prediction_ci(
                deltas["prevalence_brier"], seed=20261035),
        }
    return {
        "dataset": dataset, "timestamp_policy": timestamp_policy,
        "cgm_audit": {k: cgm_report[k] for k in (
            "participants_selected", "rows_selected_for_primary_screen",
            "invalid_timestamp_rows_selected", "rows_with_adjusted_timestamp",
            "rows_using_adjusted_timestamp")},
        "groups": groups,
        "paired_differences_by_model": paired,
        "training_prevalence_reference_by_model": references,
        "interval_note": "Participant bootstrap intervals condition on each frozen model and fixed external predictions; they do not include refit, cohort, or timestamp-policy uncertainty.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_root", nargs="?", type=Path, default=Path("data"))
    parser.add_argument("--dataset", choices=("dclp3", "dclp5"), required=True)
    parser.add_argument("--timestamp-policy", choices=("raw", "adjusted-preferred"), required=True)
    parser.add_argument("--model-artifacts", type=Path, nargs="+",
                        default=[Path(f"private/pilot_runs/loop_cgm_logistic_outer{i}_development_test_v2")
                                 for i in range(5)],
                        help="One or more completed, frozen Loop logistic model archives (default: all five outer folds).")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    models: dict[str, tuple[LogisticModel, float]] = {}
    model_reports = []
    source_signatures = set()
    for artifacts in args.model_artifacts:
        model_path = artifacts / "model.json"
        run_path = artifacts / "run.json"
        if not model_path.is_file() or not run_path.is_file():
            raise FileNotFoundError(f"frozen Loop model archive is incomplete: {artifacts}")
        run = json.loads(run_path.read_text())
        model_json = json.loads(model_path.read_text())
        if run.get("complete") is not True:
            raise ValueError(f"refusing to use incomplete Loop model archive: {artifacts}")
        report = run.get("report", {})
        if report.get("model") != "streaming_logistic_current_glucose_and_slope":
            raise ValueError(f"unexpected source model: {artifacts}")
        if report.get("evaluation_scope") != "development-test":
            raise ValueError(f"expected configuration-frozen development-test archive: {artifacts}")
        if report.get("identifiers_emitted") is not False:
            raise ValueError(f"source model report has unexpected identifier policy: {artifacts}")
        source_cache = str(run.get("arguments", {}).get("feature_cache_directory", ""))
        if Path(source_cache).name != "loop_cgm_feature_cache":
            raise ValueError(f"expected Loop-only CGM training cache: {artifacts}")
        model = LogisticModel(tuple(model_json["means"]), tuple(model_json["scales"]),
                              tuple(model_json["weights"]), float(model_json["intercept"]),
                              float(model_json["training_prevalence"]))
        if len(model.weights) != 2 or model.training_prevalence is None:
            raise ValueError(f"frozen model feature contract mismatch: {artifacts}")
        fold = str(report.get("fold", ""))
        if not fold.startswith("outer-") or fold in models:
            raise ValueError(f"missing or duplicate outer-fold label in archive: {artifacts}")
        if run.get("arguments", {}).get("fold") != fold:
            raise ValueError(f"run arguments and report disagree on fold: {artifacts}")
        if run.get("arguments", {}).get("evaluation_scope") != "development-test":
            raise ValueError(f"run arguments do not confirm development-test scope: {artifacts}")
        if run.get("arguments", {}).get("evaluate_development_test") != "False":
            raise ValueError(f"unexpected development-test selection setting: {artifacts}")
        if tuple(report.get("features", ())) != (
                "current_glucose_mg_dl", "recent_slope_mg_dl_per_5m"):
            raise ValueError(f"unexpected feature definition: {artifacts}")
        if report.get("metric_version") != "threshold-grouped-ap-v2":
            raise ValueError(f"unexpected metric version: {artifacts}")
        policy = str(report.get("policy", "")).lower()
        if not all(term in policy for term in ("excludes validation", "development-test", "locked holdout")):
            raise ValueError(f"training exclusion policy is not explicit: {artifacts}")
        if run.get("manifest_sha256") != report.get("manifest_sha256"):
            raise ValueError(f"run/report manifest digests disagree: {artifacts}")
        if report.get("window_verification", {}).get("window_identity_sha256") != (
                "26036d7d3d27c21a4407d15aacd916b98ba598dfded5da319288a74b54a592aa"):
            raise ValueError(f"Loop window identity does not match frozen cache contract: {artifacts}")
        signature = (report.get("model"), tuple(report.get("features", ())),
                     report.get("epochs"), report.get("learning_rate"),
                     report.get("manifest_sha256"), run.get("source_sha256"))
        source_signatures.add(signature)
        models[fold] = (model, model.training_prevalence)
        model_reports.append({
            "fold": fold, "model_artifacts": str(artifacts),
            "model_source_sha256": run.get("source_sha256"),
            "model_manifest_sha256": report.get("manifest_sha256"),
            "epochs": report.get("epochs"), "features": report.get("features"),
            "source_training_cache": source_cache,
        })
    if len(source_signatures) != 1:
        raise ValueError("model archives do not share the same feature/training configuration and source")
    if set(models) != {f"outer-{fold}" for fold in range(5)}:
        raise ValueError("expected exactly the five outer-fold models, outer-0 through outer-4")
    result = {
        "audit_type": "frozen Loop CGM logistic no-refit transfer pilot",
        "evaluator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "model": "streaming_logistic_current_glucose_and_slope",
        "models": model_reports,
        "external_dataset_not_in_fit": True,
        "external_label_use_for_fit_or_recalibration": False,
        "evaluation": evaluate_dataset(args.data_root, args.dataset,
                                        args.timestamp_policy, models),
        "identifiers_emitted": False,
        "limits": [
            "This is a CGM-only pilot; it does not transfer or validate graph/event relations.",
            "The listed frozen Loop outer-fold models are evaluated without external fitting, tuning, or recalibration; these shared-cohort model replays are not independent cohort replications.",
            "The timestamp-policy result is a sensitivity analysis, not evidence that either clock is correct.",
            "CGM endpoints remain release-local and are not harmonized clinical-event outcomes.",
            "External results must not be used to choose timestamp policy or model configuration.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
