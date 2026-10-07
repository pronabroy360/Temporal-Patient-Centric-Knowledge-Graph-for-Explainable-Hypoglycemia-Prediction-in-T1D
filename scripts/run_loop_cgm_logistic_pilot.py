#!/usr/bin/env python3
"""Run one patient-disjoint development-fold CGM logistic pilot, storage-bounded."""

from __future__ import annotations

import argparse
import json
import math
import shutil
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from t1d_tkg.features import cgm_recent_features
from t1d_tkg.feature_cache import iter_patients as iter_cached_patients, load_metadata as load_cache_metadata
from t1d_tkg.baselines import persistence_slope_score_from_current_and_slope
from t1d_tkg.logistic import fit_streaming_logistic
from t1d_tkg.manifest import load_manifest, manifest_checksum
from t1d_tkg.pilot_artifacts import PilotArtifacts, eligible_metadata, verify_windows
from t1d_tkg.metrics import METRIC_VERSION, average_precision
from t1d_tkg.temporal_eligibility import logical_grid_window_metadata

from audit_loop_partitioned_cgm import FIELDS, UTC_FORMAT, partition, sorted_rows


def iter_patient_readings(path: Path):
    """Yield canonical non-conflicting numeric mmol/L CGM readings by patient."""
    patient = None; readings = {}; exact_key = None; exact_rows = []; timestamp_key = None; timestamp_rows = []

    def close_timestamp():
        nonlocal timestamp_rows
        if not timestamp_rows or patient is None:
            return
        values = {(row[5], row[6]) for row in timestamp_rows if row[4] == b"CGM"}
        if len(values) != 1:
            return
        raw_value, unit = next(iter(values))
        if unit != b"mmol/L":
            return
        try:
            value = float(raw_value)
        except ValueError:
            return
        if math.isfinite(value):
            readings[datetime.strptime(timestamp_key[1].decode(), UTC_FORMAT).replace(tzinfo=timezone.utc)] = value * 18.0182

    def close_exact():
        nonlocal timestamp_key, timestamp_rows
        if not exact_rows:
            return
        representative = exact_rows[0]
        key = (representative[0], representative[3])
        if timestamp_key is not None and key != timestamp_key:
            close_timestamp(); timestamp_rows = []
        timestamp_key = key; timestamp_rows.append(representative)

    with path.open("rb") as handle:
        for raw in handle:
            row = raw.rstrip(b"\n").split(b"|")
            row_patient = row[0]
            if patient is not None and row_patient != patient:
                if exact_rows: close_exact()
                close_timestamp()
                yield patient.decode("ascii", "replace"), readings
                readings = {}; exact_key = None; exact_rows = []; timestamp_key = None; timestamp_rows = []
            patient = row_patient
            key = (row[0], row[3], row[4], row[5], row[6])
            if exact_key is not None and key != exact_key:
                close_exact(); exact_rows = []
            exact_key = key; exact_rows.append(row)
        if patient is not None:
            close_exact(); close_timestamp(); yield patient.decode("ascii", "replace"), readings


def samples(readings):
    for _, features, label in samples_with_times(readings):
        yield features, label


def samples_with_times(readings):
    ordered = sorted(readings); position = {time: index for index, time in enumerate(ordered)}
    for row in logical_grid_window_metadata(readings, threshold=70.0, tolerance_seconds=1):
        if not row["input_eligible"] or row["label_status"] != "known":
            continue
        current = datetime.fromisoformat(str(row["index_time"])); previous = ordered[position[current] - 1]
        yield current, cgm_recent_features(previous, readings[previous], current, readings[current]), int(row["label"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("release", type=Path, nargs="?")
    parser.add_argument("--model-manifest", type=Path, default=Path("private/loop_model_manifest.json"))
    parser.add_argument("--fold", default="outer-0")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--learning-rate", type=float, default=0.002)
    parser.add_argument("--partitions", type=int, default=64)
    parser.add_argument("--minimum-free-before-gib", type=float, default=20.0)
    parser.add_argument("--minimum-free-during-gib", type=float, default=10.0)
    parser.add_argument("--evaluate-development-test", action="store_true", help="evaluate the fold's internal test group after configuration is frozen")
    parser.add_argument(
        "--evaluation-scope", choices=("validation", "development-test", "both"),
        default="validation", help="prediction group; use development-test only after configuration freeze",
    )
    parser.add_argument("--window-index-directory", type=Path, default=Path("private/loop_window_index"))
    parser.add_argument("--feature-cache-directory", type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Choose a new output path; historical reports must be preserved")
    if args.epochs < 1 or args.learning_rate <= 0 or args.partitions < 1:
        raise ValueError("epochs, learning rate and partitions must be positive")
    if args.evaluate_development_test and args.evaluation_scope != "validation":
        raise ValueError("use either legacy --evaluate-development-test or --evaluation-scope")
    evaluation_scope = "both" if args.evaluate_development_test else args.evaluation_scope
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(args.output.parent).free < args.minimum_free_before_gib * 1024**3:
        raise RuntimeError("insufficient free space before CGM logistic pilot")
    manifest = load_manifest(args.model_manifest)
    fold = next((item for item in manifest["folds"] if item["fold_id"] == args.fold), None)
    if fold is None:
        raise ValueError("requested fold is not in model manifest")
    groups = {"train": set(fold["train_patients"]), "validation": set(fold["validation_patients"]), "development_test": set(fold["test_patients"])}
    if set().union(*groups.values()) != set(manifest["patients"]):
        raise ValueError("fold does not cover the development manifest")
    if args.feature_cache_directory is None and args.release is None:
        raise ValueError("release is required unless --feature-cache-directory is supplied")
    paths = [] if args.release is None else sorted((args.release / "Data Tables").glob("LOOPDeviceCGM*.txt"))
    if args.feature_cache_directory is None and not paths:
        raise ValueError("required source tables are missing")
    artifacts = PilotArtifacts(Path("private/pilot_runs") / args.output.stem, {
        "manifest_sha256": manifest_checksum(manifest), "arguments": {key: str(value) for key, value in vars(args).items()}})
    if args.feature_cache_directory is not None:
        cache_metadata = load_cache_metadata(
            args.feature_cache_directory, manifest_sha256=manifest_checksum(manifest)
        )
        window_verification = cache_metadata["window_verification"]

        def cached_training_rows():
            for patient, rows in iter_cached_patients(args.feature_cache_directory):
                if patient in groups["train"]:
                    for _, label, features in rows:
                        yield features, label

        model = fit_streaming_logistic(cached_training_rows, epochs=args.epochs, learning_rate=args.learning_rate)
        artifacts.model(model)
        evaluation_groups = {
            "validation": ("validation",), "development-test": ("development_test",),
            "both": ("validation", "development_test"),
        }[evaluation_scope]
        outcomes = {name: Counter() for name in evaluation_groups}
        for patient, rows in iter_cached_patients(args.feature_cache_directory):
            group = next((name for name in evaluation_groups if patient in groups[name]), None)
            if group is None:
                continue
            times = [row[0] for row in rows]
            labels = [row[1] for row in rows]
            features = [row[2] for row in rows]
            scores = model.predict_proba(features)
            rule_scores = [persistence_slope_score_from_current_and_slope(row[0], row[1], horizon_minutes=30) for row in features]
            artifacts.predictions(group, patient, times, labels, scores, rule_scores)
            outcomes[group]["participants"] += 1
            outcomes[group]["windows"] += len(labels)
            outcomes[group]["positive_labels"] += sum(labels)
            for name, values in (("logistic", scores), ("rule", rule_scores)):
                outcomes[group][f"{name}_squared_error_sum"] += sum((score-label)**2 for label, score in zip(labels, values, strict=True))
                ap = average_precision(labels, values)
                if ap is not None:
                    outcomes[group][f"{name}_ap_sum"] += ap
                    outcomes[group][f"{name}_ap_count"] += 1
    else:
      with tempfile.TemporaryDirectory(prefix="loop-cgm-logistic-", dir=args.output.parent) as temporary:
        directory = Path(temporary)
        _, raw_partitions = partition(paths, directory, args.partitions, minimum_free_gib=args.minimum_free_during_gib)
        sorted_partitions = []
        for raw in raw_partitions:
            if shutil.disk_usage(directory).free < args.minimum_free_during_gib * 1024**3:
                raise RuntimeError("free-space safety floor reached while sorting CGM partitions")
            sorted_partitions.append(sorted_rows(raw))

        window_verification = verify_windows(args.window_index_directory, sorted_partitions, iter_patient_readings, set(manifest["patients"]))

        def training_rows():
            for path in sorted_partitions:
                for patient, readings in iter_patient_readings(path):
                    if patient in groups["train"]:
                        yield from samples(readings)

        model = fit_streaming_logistic(training_rows, epochs=args.epochs, learning_rate=args.learning_rate)
        artifacts.model(model)
        evaluation_groups = {
            "validation": ("validation",), "development-test": ("development_test",),
            "both": ("validation", "development_test"),
        }[evaluation_scope]
        outcomes = {name: Counter() for name in evaluation_groups}
        for path in sorted_partitions:
            for patient, readings in iter_patient_readings(path):
                group = next((name for name in evaluation_groups if patient in groups[name]), None)
                if group is None:
                    continue
                labels: list[int] = []; scores: list[float] = []; rule_scores: list[float] = []
                for feature, label in samples(readings):
                    labels.append(label); scores.append(model.predict_proba([feature])[0])
                    rule_scores.append(persistence_slope_score_from_current_and_slope(feature[0], feature[1], horizon_minutes=30))
                if labels:
                    artifacts.predictions(group, patient, (row["index_time"] for row in eligible_metadata(readings)), labels, scores, rule_scores)
                    outcomes[group]["participants"] += 1
                    outcomes[group]["windows"] += len(labels)
                    outcomes[group]["positive_labels"] += sum(labels)
                    for name, values in (("logistic", scores), ("rule", rule_scores)):
                        outcomes[group][f"{name}_squared_error_sum"] += sum((score - label) ** 2 for label, score in zip(labels, values))
                        ap = average_precision(labels, values)
                        if ap is not None:
                            outcomes[group][f"{name}_ap_sum"] += ap; outcomes[group][f"{name}_ap_count"] += 1
            path.unlink()
    report_groups = {}
    for group, counts in outcomes.items():
        report_groups[group] = {
            "participants": counts["participants"], "windows": counts["windows"], "positive_labels": counts["positive_labels"],
            "streaming_logistic": {"ap_defined_participants": counts["logistic_ap_count"], "participant_macro_ap": counts["logistic_ap_sum"] / counts["logistic_ap_count"] if counts["logistic_ap_count"] else None, "brier_score": counts["logistic_squared_error_sum"] / counts["windows"] if counts["windows"] else None},
            "persistence_slope_rule": {"ap_defined_participants": counts["rule_ap_count"], "participant_macro_ap": counts["rule_ap_sum"] / counts["rule_ap_count"] if counts["rule_ap_count"] else None, "brier_score": counts["rule_squared_error_sum"] / counts["windows"] if counts["windows"] else None},
        }
    report = {"model": "streaming_logistic_current_glucose_and_slope", "fold": args.fold, "epochs": args.epochs, "learning_rate": args.learning_rate, "features": ["current_glucose_mg_dl", "recent_slope_mg_dl_per_5m"], "metric_version": METRIC_VERSION, "manifest_sha256": manifest_checksum(manifest), "identifiers_emitted": False, "evaluation_scope": evaluation_scope, "groups": report_groups, "policy": "Development-only pilot. Training excludes validation, internal development-test, and locked holdout participants. Development-test evaluation is permitted only after configuration selection."}
    report["optimizer"] = {"l2": 1e-4, "positive_weight": 1.0, "order": "deterministic participant partitions", "learning_rate_schedule": "initial/sqrt(epoch+1)"}
    for group in report["groups"].values():
        prevalence = model.training_prevalence
        group["training_prevalence_reference"] = {
            "probability": prevalence,
            "brier_score": ((group["windows"]-group["positive_labels"])*prevalence**2 + group["positive_labels"]*(1-prevalence)**2)/group["windows"] if group["windows"] else None}
    report["window_verification"] = window_verification
    report["input_source"] = "protected_feature_cache" if args.feature_cache_directory is not None else "canonicalized_raw_cgm"
    report["artifacts"] = str(artifacts.path)
    artifacts.complete(report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
