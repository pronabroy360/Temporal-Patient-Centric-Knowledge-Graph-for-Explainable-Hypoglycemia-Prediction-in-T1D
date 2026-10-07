#!/usr/bin/env python3
"""Outer-fold position-aware cached-event sequence residual diagnostic."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from run_loop_event_residual_pilot import load_frozen_cgm, merged_event_patients
from t1d_tkg.event_cache import iter_partition_patients as iter_event_partition_patients, load_metadata as load_event_metadata
from t1d_tkg.event_residual import fit_streaming_event_residual
from t1d_tkg.event_sequence_cache import EVENT_FEATURE_WIDTH, iter_sequence_features
from t1d_tkg.feature_cache import iter_partition_patients as iter_cgm_partition_patients, load_metadata as load_cgm_metadata
from t1d_tkg.manifest import load_manifest, manifest_checksum
from t1d_tkg.metrics import METRIC_VERSION, average_precision
from t1d_tkg.pilot_artifacts import PilotArtifacts


def sequence_partition(cgm_path, event_paths, max_events, *, include_modality_counts=False, eligible_patients=None):
    events = merged_event_patients(event_paths)
    event_item = next(events, None)
    for patient, rows in iter_cgm_partition_patients(cgm_path):
        while event_item is not None and event_item[0] < patient:
            event_item = next(events, None)
        records = [] if event_item is None or event_item[0] != patient else event_item[1]
        if event_item is not None and event_item[0] == patient:
            event_item = next(events, None)
        if eligible_patients is not None and patient not in eligible_patients:
            continue
        windows = [(datetime.fromisoformat(time), label, features) for time, label, features in rows]
        sequences = iter_sequence_features((row[0] for row in windows), records, max_events=max_events, include_modality_counts=include_modality_counts)
        for (time, label, cgm), result in zip(windows, sequences, strict=True):
            sequence_time, sequence, active, dropped = result[:4]
            if time != sequence_time:
                raise RuntimeError("sequence iterator lost frozen window order")
            if include_modality_counts:
                yield patient, time.isoformat(), cgm, sequence, label, active, dropped, result[4], result[5]
            else:
                yield patient, time.isoformat(), cgm, sequence, label, active, dropped


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--feature-cache-directory", type=Path, required=True)
    parser.add_argument("--event-cache-directory", type=Path, required=True)
    parser.add_argument("--model-manifest", type=Path, default=Path("private/loop_model_manifest.json"))
    parser.add_argument("--cgm-baseline-artifacts", type=Path, required=True)
    parser.add_argument("--fold", default="outer-0")
    parser.add_argument("--max-events", type=int, default=16)
    parser.add_argument("--epochs", type=int, required=True)
    parser.add_argument("--learning-rate", type=float, default=0.002)
    parser.add_argument("--l2", type=float, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists(): raise FileExistsError("choose a new output path")
    if args.max_events < 1 or args.epochs < 1 or args.learning_rate <= 0 or args.l2 < 0: raise ValueError("invalid sequence hyperparameters")
    manifest = load_manifest(args.model_manifest); checksum = manifest_checksum(manifest)
    fold = next((item for item in manifest["folds"] if item["fold_id"] == args.fold), None)
    if fold is None: raise ValueError("requested fold is not in model manifest")
    groups = {"train": set(fold["train_patients"]), "validation": set(fold["validation_patients"])}
    cgm_meta = load_cgm_metadata(args.feature_cache_directory, manifest_sha256=checksum)
    event_meta = load_event_metadata(args.event_cache_directory, manifest_sha256=checksum)
    if event_meta.get("cgm_window_identity_sha256") != cgm_meta["window_verification"]["window_identity_sha256"]: raise ValueError("event and CGM caches have different window identities")
    partitions = int(cgm_meta["partitions"])
    cgm_paths = sorted(args.feature_cache_directory.glob("features-*.tsv.gz"))
    event_paths = {m: sorted(args.event_cache_directory.glob(f"events-{m}-*.jsonl.gz")) for m in ("basal", "bolus", "food")}
    if len(cgm_paths) != partitions or any(len(paths) != partitions for paths in event_paths.values()): raise ValueError("cache files do not match partition metadata")
    base = load_frozen_cgm(args.cgm_baseline_artifacts, checksum, args.fold)
    def rows(patients):
        for number in range(partitions):
            paths = [event_paths[m][number] for m in ("basal", "bolus", "food")]
            for patient, _, cgm, sequence, label, _, _ in sequence_partition(cgm_paths[number], paths, args.max_events):
                if patient in patients: yield cgm, sequence, label
    model = fit_streaming_event_residual(lambda: rows(groups["train"]), base, epochs=args.epochs, learning_rate=args.learning_rate, l2=args.l2)
    artifacts = PilotArtifacts(Path("private/pilot_runs") / args.output.stem, {"manifest_sha256": checksum, "arguments": {k: str(v) for k,v in vars(args).items()}, "frozen_cgm_artifacts": str(args.cgm_baseline_artifacts)})
    artifacts.model(model); counts = Counter()
    for number in range(partitions):
        paths = [event_paths[m][number] for m in ("basal", "bolus", "food")]; patients = {}
        for patient, time, cgm, sequence, label, active, dropped in sequence_partition(cgm_paths[number], paths, args.max_events):
            if patient not in groups["validation"]: continue
            item = patients.setdefault(patient, ([], [], [], [])); item[0].append(time); item[1].append(label); item[2].append(model.predict_proba(base,cgm,sequence)); item[3].append(base.predict_proba([cgm])[0])
            counts["active_events"] += active; counts["dropped_events"] += dropped; counts["windows_with_truncation"] += int(dropped > 0); counts["max_active_events"] = max(counts["max_active_events"], active)
        for patient,(times,labels,scores,base_scores) in patients.items():
            artifacts.predictions("validation",patient,times,labels,scores,base_scores); counts["participants"] += 1; counts["windows"] += len(labels); counts["positive_labels"] += sum(labels)
            for name, values in (("sequence",scores),("frozen_cgm",base_scores)):
                counts[f"{name}_squared_error_sum"] += sum((score-label)**2 for label,score in zip(labels,values,strict=True)); ap=average_precision(labels,values)
                if ap is not None: counts[f"{name}_ap_sum"] += ap; counts[f"{name}_ap_count"] += 1
    def metrics(name): return {"ap_defined_participants":counts[f"{name}_ap_count"],"participant_macro_ap":counts[f"{name}_ap_sum"]/counts[f"{name}_ap_count"],"brier_score":counts[f"{name}_squared_error_sum"]/counts["windows"]}
    report={"model":"frozen_cgm_position_aware_event_sequence_residual","fold":args.fold,"max_events":args.max_events,"event_feature_width":EVENT_FEATURE_WIDTH,"sequence_feature_width":EVENT_FEATURE_WIDTH*args.max_events,"epochs":args.epochs,"learning_rate":args.learning_rate,"l2":args.l2,"metric_version":METRIC_VERSION,"manifest_sha256":checksum,"identifiers_emitted":False,"groups":{"validation":{"participants":counts["participants"],"windows":counts["windows"],"positive_labels":counts["positive_labels"],"event_sequence_residual":metrics("sequence"),"frozen_cgm":metrics("frozen_cgm")}},"truncation":{"windows_with_truncation":counts["windows_with_truncation"],"fraction_windows_truncated":counts["windows_with_truncation"]/counts["windows"],"events_dropped":counts["dropped_events"],"max_active_events":counts["max_active_events"]},"window_verification":cgm_meta["window_verification"],"event_cache_version":event_meta["cache_version"],"availability_policy":"retrospective occurrence-time replay; immediate availability assumed, not measured","policy":"Development-only position-aware individual-event sequence diagnostic. Frozen CGM model remains immutable; training excludes validation, development-test, and locked holdout participants.","artifacts":str(artifacts.path)}
    artifacts.complete(report); args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n"); print(json.dumps(report,indent=2,sort_keys=True))

if __name__ == "__main__": main()
