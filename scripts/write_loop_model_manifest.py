#!/usr/bin/env python3
"""Freeze patient-disjoint model folds for the selected Loop candidate pool."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from t1d_tkg.manifest import build_hashed_kfold_manifest, manifest_checksum, save_manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-manifest", type=Path, default=Path("private/loop_development_manifest.json"))
    parser.add_argument("--private-output", type=Path, default=Path("private/loop_model_manifest.json"))
    parser.add_argument("--summary-output", type=Path, required=True)
    parser.add_argument("--folds", type=int, default=5)
    args = parser.parse_args()
    candidate = json.loads(args.candidate_manifest.read_text(encoding="utf-8"))
    development = sorted(set(candidate["development_patients"]))
    holdout = sorted(set(candidate["holdout_patients"]))
    manifest = build_hashed_kfold_manifest(development, folds=args.folds, version="loop-development-model-folds-v1")
    manifest["locked_holdout_patients"] = holdout
    args.private_output.parent.mkdir(parents=True, exist_ok=True)
    checksum = save_manifest(args.private_output, manifest)
    summary = {
        "version": manifest["version"], "strategy": manifest["strategy"],
        "development_participants": len(development), "locked_holdout_participants": len(holdout), "outer_folds": args.folds,
        "fold_sizes": [{"train": len(fold["train_patients"]), "validation": len(fold["validation_patients"]), "test": len(fold["test_patients"])} for fold in manifest["folds"]],
        "manifest_sha256": checksum, "identifiers_emitted": False,
    }
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
