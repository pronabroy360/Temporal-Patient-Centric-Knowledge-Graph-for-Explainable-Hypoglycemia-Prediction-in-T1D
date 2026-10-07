#!/usr/bin/env python3
"""Validate a compact prediction-window JSONL index."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from t1d_tkg.window_index import validate_window_index, validate_window_index_directory
from t1d_tkg.manifest import fold_by_patient, load_manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("index", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--manifest", type=Path, help="validated LOSO manifest used for fold checks")
    parser.add_argument("--sha256", help="expected exact-file SHA-256 digest")
    args = parser.parse_args()
    expected = fold_by_patient(load_manifest(args.manifest)) if args.manifest else None
    summary = validate_window_index_directory(args.index, expected_folds=expected) if args.index.is_dir() else validate_window_index(args.index, expected_folds=expected)
    if args.sha256 and summary["sha256"] != args.sha256:
        raise SystemExit(f"SHA-256 mismatch: expected {args.sha256}, got {summary['sha256']}")
    payload = json.dumps(summary, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
