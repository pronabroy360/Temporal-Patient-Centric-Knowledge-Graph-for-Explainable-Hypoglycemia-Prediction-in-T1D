#!/usr/bin/env python3
"""Build a protected, verified development-only Loop CGM feature cache."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from audit_loop_partitioned_cgm import partition, sorted_rows
from run_loop_cgm_logistic_pilot import iter_patient_readings, samples_with_times
from t1d_tkg.feature_cache import CACHE_VERSION, FEATURE_NAMES, write_partition
from t1d_tkg.manifest import load_manifest, manifest_checksum
from t1d_tkg.pilot_artifacts import verify_windows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("release", type=Path)
    parser.add_argument("--model-manifest", type=Path, default=Path("private/loop_model_manifest.json"))
    parser.add_argument("--window-index-directory", type=Path, default=Path("private/loop_window_index"))
    parser.add_argument("--output-directory", type=Path, default=Path("private/loop_cgm_feature_cache"))
    parser.add_argument("--summary-output", type=Path, default=Path("audit/loop_cgm_feature_cache.json"))
    parser.add_argument("--partitions", type=int, default=64)
    parser.add_argument("--minimum-free-before-gib", type=float, default=20.0)
    parser.add_argument("--minimum-free-during-gib", type=float, default=10.0)
    args = parser.parse_args()
    if args.output_directory.exists() or args.summary_output.exists():
        raise FileExistsError("cache and summary outputs must be new paths")
    if args.partitions < 1:
        raise ValueError("partitions must be positive")
    paths = sorted((args.release / "Data Tables").glob("LOOPDeviceCGM*.txt"))
    if not paths:
        raise ValueError("required CGM source tables are missing")
    if shutil.disk_usage(args.output_directory.parent).free < args.minimum_free_before_gib * 1024**3:
        raise RuntimeError("insufficient free space before feature-cache build")
    manifest = load_manifest(args.model_manifest)
    patients = set(manifest["patients"])
    args.output_directory.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="loop-cgm-cache-build-", dir=args.output_directory.parent) as temporary:
        workspace = Path(temporary)
        raw_dir = workspace / "raw"
        raw_dir.mkdir()
        _, raw_paths = partition(
            paths, raw_dir, args.partitions, minimum_free_gib=args.minimum_free_during_gib
        )
        sorted_paths = []
        for raw_path in raw_paths:
            if shutil.disk_usage(workspace).free < args.minimum_free_during_gib * 1024**3:
                raise RuntimeError("free-space safety floor reached while sorting CGM partitions")
            sorted_paths.append(sorted_rows(raw_path))
        verification = verify_windows(
            args.window_index_directory, sorted_paths, iter_patient_readings, patients
        )
        destination = workspace / "cache"
        destination.mkdir()
        summaries = []
        for number, sorted_path in enumerate(sorted_paths):
            def rows():
                for patient, readings in iter_patient_readings(sorted_path):
                    if patient not in patients:
                        continue
                    for index_time, features, label in samples_with_times(readings):
                        yield patient, index_time.isoformat(), label, *features

            summaries.append(write_partition(destination / f"features-{number:02d}.tsv.gz", rows()))
        metadata = {
            "cache_version": CACHE_VERSION,
            "features": list(FEATURE_NAMES),
            "manifest_sha256": manifest_checksum(manifest),
            "development_participants": len(patients),
            "partitions": len(summaries),
            "records": sum(int(item["records"]) for item in summaries),
            "positive_labels": sum(int(item["positive_labels"]) for item in summaries),
            "window_verification": verification,
            "partition_summaries": summaries,
            "identifiers_emitted_publicly": False,
        }
        (destination / "metadata.json").write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        destination.rename(args.output_directory)
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    public = {key: value for key, value in metadata.items() if key != "partition_summaries"}
    args.summary_output.write_text(json.dumps(public, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(public, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
