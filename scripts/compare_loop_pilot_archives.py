#!/usr/bin/env python3
"""Paired participant comparison of two protected pilot prediction archives."""

from __future__ import annotations

import argparse
import gzip
import json
import random
from pathlib import Path

from t1d_tkg.metrics import METRIC_VERSION, average_precision


def percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] + fraction * (ordered[upper] - ordered[lower])


def interval(differences: list[float], *, draws: int, seed: int) -> list[float]:
    rng = random.Random(seed)
    replicates = []
    for _ in range(draws):
        sample = [differences[rng.randrange(len(differences))] for _ in differences]
        replicates.append(sum(sample) / len(sample))
    return [percentile(replicates, 0.025), percentile(replicates, 0.975)]


def metadata(directory: Path, group: str) -> dict[str, object]:
    record = json.loads((directory / "run.json").read_text(encoding="utf-8"))
    report = record.get("report", record)
    if not record.get("complete") or report.get("metric_version") != METRIC_VERSION:
        raise ValueError(f"archive is incomplete or uses a legacy metric: {directory}")
    if set(report.get("groups", {})) != {group}:
        raise ValueError(f"archive does not contain only {group}: {directory}")
    return report


def prediction_files(directory: Path, group: str) -> dict[str, Path]:
    paths = list(directory.rglob(f"{group}-*.jsonl.gz"))
    files = {path.name: path for path in paths}
    if len(files) != len(paths):
        raise ValueError(f"archive contains duplicate participant filenames: {directory}")
    return files


def window_identity(report: dict[str, object]) -> str:
    """Accept the historical nested and controlled-neural flat layouts."""
    nested = report.get("window_verification", {}).get("window_identity_sha256")
    flat = report.get("window_identity_sha256")
    if nested is not None and flat is not None and nested != flat:
        raise ValueError("archive has conflicting window identity digests")
    value = flat if flat is not None else nested
    if not isinstance(value, str) or not value:
        raise ValueError("archive is missing a window identity digest")
    return value


def compare(first: Path, second: Path, *, group: str, draws: int, seed: int, first_score_field: str = "score", second_score_field: str = "score") -> dict[str, object]:
    if draws < 1:
        raise ValueError("draws must be positive")
    first_report = metadata(first, group)
    second_report = metadata(second, group)
    contract = (
        first_report["manifest_sha256"], window_identity(first_report),
        first_report["groups"][group]["windows"], first_report["groups"][group]["positive_labels"],
    )
    other_contract = (
        second_report["manifest_sha256"], window_identity(second_report),
        second_report["groups"][group]["windows"], second_report["groups"][group]["positive_labels"],
    )
    if contract != other_contract:
        raise ValueError("archives do not share manifest, windows, and labels")
    first_files = prediction_files(first, group)
    second_files = prediction_files(second, group)
    if not first_files or set(first_files) != set(second_files):
        raise ValueError("archives do not contain the same participant files")

    ap_first: list[float] = []
    ap_second: list[float] = []
    brier_first: list[float] = []
    brier_second: list[float] = []
    total_squared_first = total_squared_second = 0.0
    total_rows = total_positives = 0
    for name in sorted(first_files):
        labels: list[int] = []
        scores_first: list[float] = []
        scores_second: list[float] = []
        with gzip.open(first_files[name], "rt", encoding="utf-8") as left, gzip.open(second_files[name], "rt", encoding="utf-8") as right:
            for line_first, line_second in zip(left, right, strict=True):
                row_first = json.loads(line_first)
                row_second = json.loads(line_second)
                identity_first = (row_first["patient_id"], row_first["index_time"], row_first["label"])
                identity_second = (row_second["patient_id"], row_second["index_time"], row_second["label"])
                if identity_first != identity_second:
                    raise ValueError("prediction archives differ in participant, time, or label")
                labels.append(int(row_first["label"]))
                try:
                    scores_first.append(float(row_first[first_score_field]))
                    scores_second.append(float(row_second[second_score_field]))
                except (KeyError, TypeError, ValueError) as error:
                    raise ValueError("requested prediction score field is absent or invalid") from error
        if not labels:
            raise ValueError("empty participant prediction file")
        first_ap = average_precision(labels, scores_first)
        second_ap = average_precision(labels, scores_second)
        if (first_ap is None) != (second_ap is None):
            raise ValueError("AP defined status differs despite matched labels")
        if first_ap is not None:
            ap_first.append(first_ap)
            ap_second.append(second_ap)
        first_error = sum((score - label) ** 2 for label, score in zip(labels, scores_first, strict=True))
        second_error = sum((score - label) ** 2 for label, score in zip(labels, scores_second, strict=True))
        brier_first.append(first_error / len(labels))
        brier_second.append(second_error / len(labels))
        total_squared_first += first_error
        total_squared_second += second_error
        total_rows += len(labels)
        total_positives += sum(labels)
    if total_rows != contract[2] or total_positives != contract[3]:
        raise ValueError("paired archive rows do not reconcile with reports")

    def comparison(values_first, values_second):
        differences = [left - right for left, right in zip(values_first, values_second, strict=True)]
        return {
            "first": sum(values_first) / len(values_first),
            "second": sum(values_second) / len(values_second),
            "difference_first_minus_second": sum(differences) / len(differences),
            "difference_ci95": interval(differences, draws=draws, seed=seed),
            "positive_difference_participants": sum(value > 0 for value in differences),
            "negative_difference_participants": sum(value < 0 for value in differences),
            "tied_participants": sum(value == 0 for value in differences),
            "participants": len(differences),
        }

    return {
        "comparison": "paired fixed predictions by participant",
        "first_archive": str(first), "second_archive": str(second),
        "first_score_field": first_score_field, "second_score_field": second_score_field,
        "difference_orientation": "first minus second", "group": group,
        "metric_version": METRIC_VERSION, "draws": draws, "seed": seed,
        "identifiers_emitted": False, "participants": len(first_files),
        "windows": total_rows, "positive_labels": total_positives,
        "participant_macro_ap": comparison(ap_first, ap_second),
        "participant_macro_brier": comparison(brier_first, brier_second),
        "pooled_brier": {
            "first": total_squared_first / total_rows,
            "second": total_squared_second / total_rows,
            "difference_first_minus_second": (total_squared_first - total_squared_second) / total_rows,
        },
        "manifest_sha256": contract[0], "window_identity_sha256": contract[1],
        "policy": "Percentile interval from paired participant resampling of fixed predictions; no model refitting.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("first_archive", type=Path)
    parser.add_argument("second_archive", type=Path)
    parser.add_argument("--group", choices=("validation", "development_test"), default="validation")
    parser.add_argument("--draws", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260915)
    parser.add_argument("--first-score-field", choices=("score", "rule_score"), default="score")
    parser.add_argument("--second-score-field", choices=("score", "rule_score"), default="score")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("comparison output already exists")
    report = compare(args.first_archive, args.second_archive, group=args.group, draws=args.draws, seed=args.seed,
                     first_score_field=args.first_score_field, second_score_field=args.second_score_field)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
