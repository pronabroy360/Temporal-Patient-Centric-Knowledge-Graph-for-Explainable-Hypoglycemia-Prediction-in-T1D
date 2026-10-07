#!/usr/bin/env python3
"""Verify frozen Loop window-index coverage under the protected model split."""

from __future__ import annotations

import argparse
import gzip
import json
from collections import Counter, defaultdict
from pathlib import Path

from t1d_tkg.manifest import fold_by_patient, load_manifest, manifest_checksum


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--window-index-directory", type=Path, required=True)
    parser.add_argument("--model-manifest", type=Path, default=Path("private/loop_model_manifest.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = load_manifest(args.model_manifest)
    development_fold = fold_by_patient(manifest)
    locked = set(str(patient) for patient in manifest.get("locked_holdout_patients", []))
    if locked & set(development_fold):
        raise ValueError("locked holdout overlaps development participants")
    totals: Counter[str] = Counter()
    per_group: dict[str, Counter[str]] = defaultdict(Counter)
    participants: dict[str, set[str]] = defaultdict(set)
    for path in sorted(args.window_index_directory.glob("*.jsonl.gz")):
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            next(handle)
            for line in handle:
                row = json.loads(line)
                patient = str(row["patient_id"])
                if patient in development_fold:
                    group = development_fold[patient]
                elif patient in locked:
                    group = "locked_holdout"
                else:
                    raise ValueError("window index includes a patient outside model split")
                totals["windows"] += 1
                totals["positive_labels"] += int(row["label"] == 1)
                per_group[group]["windows"] += 1
                per_group[group]["positive_labels"] += int(row["label"] == 1)
                participants[group].add(patient)
    missing_development = sorted(set(development_fold) - set().union(*(members for members in participants.values())))
    missing_locked = sorted(locked - participants.get("locked_holdout", set()))
    if missing_development or missing_locked:
        raise ValueError("one or more split participants have no indexed windows")
    groups = {
        group: {
            "participants": len(participants[group]),
            "windows": counts["windows"],
            "positive_labels": counts["positive_labels"],
            "positive_prevalence": counts["positive_labels"] / counts["windows"] if counts["windows"] else None,
        }
        for group, counts in sorted(per_group.items())
    }
    report = {
        "audit_type": "frozen window-index coverage under protected model split",
        "identifiers_emitted": False,
        "model_manifest_sha256": manifest_checksum(manifest),
        "windows": totals["windows"], "positive_labels": totals["positive_labels"],
        "positive_prevalence": totals["positive_labels"] / totals["windows"] if totals["windows"] else None,
        "groups": groups,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
