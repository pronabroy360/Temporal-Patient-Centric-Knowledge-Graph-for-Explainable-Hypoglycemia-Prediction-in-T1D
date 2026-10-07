#!/usr/bin/env python3
"""Test whether cached Loop events improve a frozen CGM predictor."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from t1d_tkg.captured_events import iter_captured_event_features
from t1d_tkg.event_cache import iter_partition_patients as iter_event_partition_patients, load_metadata as load_event_metadata
from t1d_tkg.event_residual import (
    PRESENCE_QUALITY_FEATURE_NAMES, VALUE_TIMING_FEATURE_NAMES, fit_streaming_event_residual, residual_features,
)
from t1d_tkg.feature_cache import iter_partition_patients as iter_cgm_partition_patients, load_metadata as load_cgm_metadata
from t1d_tkg.logistic import LogisticModel
from t1d_tkg.manifest import load_manifest, manifest_checksum
from t1d_tkg.metrics import METRIC_VERSION, average_precision
from t1d_tkg.pilot_artifacts import PilotArtifacts


def load_frozen_cgm(path: Path, manifest_sha256: str, fold_id: str) -> LogisticModel:
    """Load a completed CGM archive only when it belongs to this exact fold."""
    metadata = json.loads((path / "run.json").read_text(encoding="utf-8"))
    report = metadata.get("report", {})
    if not metadata.get("complete") or metadata.get("manifest_sha256") != manifest_sha256:
        raise ValueError("CGM baseline archive is incomplete or uses a different manifest")
    if report.get("fold") != fold_id or report.get("model") != "streaming_logistic_current_glucose_and_slope":
        raise ValueError("CGM baseline archive does not match the requested fold")
    raw = json.loads((path / "model.json").read_text(encoding="utf-8"))
    return LogisticModel(tuple(raw["means"]), tuple(raw["scales"]), tuple(raw["weights"]), float(raw["intercept"]), raw.get("training_prevalence"))


def merged_event_patients(paths: list[Path]):
    """Merge the three modality streams without retaining a full partition."""
    streams = [iter_event_partition_patients(path) for path in paths]
    current = [next(stream, None) for stream in streams]
    while any(item is not None for item in current):
        patient = min(str(item[0]) for item in current if item is not None)
        records = []
        for index, item in enumerate(current):
            if item is not None and str(item[0]) == patient:
                records.extend(item[1])
                current[index] = next(streams[index], None)
        records.sort(key=lambda record: str(record["occurrence_time"]))
        yield patient, records


def join_partition(cgm_path: Path, event_paths: list[Path], variant: str):
    events = merged_event_patients(event_paths)
    event_item = next(events, None)
    for patient, cgm_rows in iter_cgm_partition_patients(cgm_path):
        while event_item is not None and event_item[0] < patient:
            event_item = next(events, None)
        records = [] if event_item is None or event_item[0] != patient else event_item[1]
        if event_item is not None and event_item[0] == patient:
            event_item = next(events, None)
        replay = [
            (datetime.fromisoformat(str(record["occurrence_time"])), str(record["modality"]),
             float(record["model_value"]) if record["model_value_known"] else None)
            for record in records
        ]
        windows = [(datetime.fromisoformat(time), label, features) for time, label, features in cgm_rows]
        summaries = iter_captured_event_features((row[0] for row in windows), replay)
        for (time, label, cgm), (event_time, summary) in zip(windows, summaries, strict=True):
            if time != event_time:
                raise RuntimeError("event replay lost frozen CGM window order")
            yield patient, time.isoformat(), cgm, residual_features(summary, variant), label


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--feature-cache-directory", type=Path, required=True)
    parser.add_argument("--event-cache-directory", type=Path, required=True)
    parser.add_argument("--model-manifest", type=Path, default=Path("private/loop_model_manifest.json"))
    parser.add_argument("--cgm-baseline-artifacts", type=Path, required=True)
    parser.add_argument("--fold", default="outer-0")
    parser.add_argument("--variant", choices=("presence-quality", "value-timing"), required=True)
    parser.add_argument("--epochs", type=int, required=True)
    parser.add_argument("--learning-rate", type=float, default=0.002)
    parser.add_argument("--l2", type=float, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("choose a new output path; pilot reports must be preserved")
    if args.epochs < 1 or args.learning_rate <= 0 or args.l2 < 0:
        raise ValueError("epochs and learning rate must be positive; l2 must be nonnegative")
    manifest = load_manifest(args.model_manifest)
    checksum = manifest_checksum(manifest)
    fold = next((item for item in manifest["folds"] if item["fold_id"] == args.fold), None)
    if fold is None:
        raise ValueError("requested fold is not in model manifest")
    groups = {"train": set(fold["train_patients"]), "validation": set(fold["validation_patients"])}
    cgm_metadata = load_cgm_metadata(args.feature_cache_directory, manifest_sha256=checksum)
    event_metadata = load_event_metadata(args.event_cache_directory, manifest_sha256=checksum)
    if event_metadata.get("cgm_window_identity_sha256") != cgm_metadata["window_verification"]["window_identity_sha256"]:
        raise ValueError("event cache was not built for the frozen CGM window identity")
    partitions = int(cgm_metadata["partitions"])
    if int(event_metadata.get("partitions", 0)) != partitions:
        raise ValueError("event and CGM cache partition counts differ")
    cgm_paths = sorted(args.feature_cache_directory.glob("features-*.tsv.gz"))
    event_paths = {modality: sorted(args.event_cache_directory.glob(f"events-{modality}-*.jsonl.gz")) for modality in ("basal", "bolus", "food")}
    if len(cgm_paths) != partitions or any(len(paths) != partitions for paths in event_paths.values()):
        raise ValueError("cache files do not match metadata partition counts")
    base = load_frozen_cgm(args.cgm_baseline_artifacts, checksum, args.fold)

    def rows(patients):
        for number in range(partitions):
            paths = [event_paths[modality][number] for modality in ("basal", "bolus", "food")]
            for patient, _, cgm, events, label in join_partition(cgm_paths[number], paths, args.variant):
                if patient in patients:
                    yield cgm, events, label

    model = fit_streaming_event_residual(lambda: rows(groups["train"]), base, epochs=args.epochs, learning_rate=args.learning_rate, l2=args.l2)
    artifacts = PilotArtifacts(Path("private/pilot_runs") / args.output.stem, {
        "manifest_sha256": checksum, "arguments": {key: str(value) for key, value in vars(args).items()},
        "frozen_cgm_artifacts": str(args.cgm_baseline_artifacts),
    })
    artifacts.model(model)
    counts = Counter()
    for number in range(partitions):
        paths = [event_paths[modality][number] for modality in ("basal", "bolus", "food")]
        by_patient = {}
        for patient, time, cgm, events, label in join_partition(cgm_paths[number], paths, args.variant):
            if patient not in groups["validation"]:
                continue
            entry = by_patient.setdefault(patient, ([], [], [], []))
            entry[0].append(time); entry[1].append(label)
            entry[2].append(model.predict_proba(base, cgm, events)); entry[3].append(base.predict_proba([cgm])[0])
        for patient, (times, labels, scores, base_scores) in by_patient.items():
            artifacts.predictions("validation", patient, times, labels, scores, base_scores)
            counts["participants"] += 1; counts["windows"] += len(labels); counts["positive_labels"] += sum(labels)
            for name, values in (("residual", scores), ("frozen_cgm", base_scores)):
                counts[f"{name}_squared_error_sum"] += sum((score-label)**2 for label, score in zip(labels, values, strict=True))
                ap = average_precision(labels, values)
                if ap is not None:
                    counts[f"{name}_ap_sum"] += ap; counts[f"{name}_ap_count"] += 1
    def metrics(name):
        return {"ap_defined_participants": counts[f"{name}_ap_count"], "participant_macro_ap": counts[f"{name}_ap_sum"] / counts[f"{name}_ap_count"] if counts[f"{name}_ap_count"] else None, "brier_score": counts[f"{name}_squared_error_sum"] / counts["windows"] if counts["windows"] else None}
    names = PRESENCE_QUALITY_FEATURE_NAMES if args.variant == "presence-quality" else VALUE_TIMING_FEATURE_NAMES
    report = {
        "model": "frozen_cgm_event_logit_residual", "variant": args.variant, "features": list(names),
        "fold": args.fold, "epochs": args.epochs, "learning_rate": args.learning_rate, "l2": args.l2,
        "metric_version": METRIC_VERSION, "manifest_sha256": checksum, "identifiers_emitted": False,
        "groups": {"validation": {"participants": counts["participants"], "windows": counts["windows"], "positive_labels": counts["positive_labels"], "event_residual": metrics("residual"), "frozen_cgm": metrics("frozen_cgm")}},
        "window_verification": cgm_metadata["window_verification"], "event_cache_version": event_metadata["cache_version"],
        "availability_policy": "retrospective occurrence-time replay; immediate availability assumed, not measured",
        "policy": "Development-only frozen-CGM residual diagnostic. The CGM predictor is loaded from a completed matching archive and remains immutable. Training excludes validation, development-test, and locked-holdout participants.",
        "artifacts": str(artifacts.path),
    }
    artifacts.complete(report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
