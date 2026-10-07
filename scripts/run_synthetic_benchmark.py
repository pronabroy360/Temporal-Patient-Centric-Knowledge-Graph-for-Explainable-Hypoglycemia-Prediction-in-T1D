#!/usr/bin/env python3
"""Assemble the complete leakage checks into one synthetic artifact."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from t1d_tkg.audit import audit_dataset
from t1d_tkg.archive import validate_prediction_archive
from t1d_tkg.config import DEFAULT_CONFIG
from t1d_tkg.evaluation import (
    evaluate_loso_cgm,
    evaluate_loso_event_sequence,
    evaluate_loso_graph,
    evaluate_loso_multimodal,
)
from t1d_tkg.manifest import build_loso_manifest, manifest_checksum
from t1d_tkg.synthetic import synthetic_events
from t1d_tkg.uncertainty import paired_cluster_bootstrap
from t1d_tkg.windows import build_prediction_windows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=None, help="optional JSON artifact path")
    parser.add_argument("--bootstrap-draws", type=int, default=2000)
    args = parser.parse_args()
    config = DEFAULT_CONFIG

    events = synthetic_events()
    patients = sorted({event.patient_id for event in events})
    grouped = {
        patient: build_prediction_windows(
            events,
            patient_id=patient,
            horizon_minutes=config.primary_horizon_minutes,
            history_minutes=config.history_minutes,
            step_minutes=config.step_minutes,
            max_consecutive_missing=config.max_consecutive_missing,
        )
        for patient in patients
    }
    manifest = build_loso_manifest(patients)
    cgm = evaluate_loso_cgm(grouped, include_predictions=True, manifest=manifest)
    multimodal = evaluate_loso_multimodal(events, grouped, include_predictions=True, manifest=manifest)
    sequence = evaluate_loso_event_sequence(events, grouped, include_predictions=True, manifest=manifest)
    graph_typed = evaluate_loso_graph(events, grouped, relation_mode="typed", include_predictions=True, manifest=manifest)
    graph_generic = evaluate_loso_graph(events, grouped, relation_mode="generic", include_predictions=True, manifest=manifest)
    model_runs = [cgm, multimodal, sequence, graph_typed, graph_generic]
    predictions = {}
    metrics = {}
    for run in model_runs:
        predictions.update(run.pop("predictions"))
        metrics.update({key: value for key, value in run.items() if key != "fold_counts"})
    bootstrap_input = {
        model: {patient: (values["labels"], values["scores"]) for patient, values in patient_values.items()}
        for model, patient_values in predictions.items()
    }
    validate_prediction_archive(predictions, manifest)
    bootstrap = paired_cluster_bootstrap(
        bootstrap_input,
        model_a="logistic_graph_typed",
        model_b="logistic_multimodal",
        draws=args.bootstrap_draws,
        seed=0,
    )
    artifact = {
        "artifact_type": "synthetic_software_fixture",
        "warning": "Synthetic metrics are implementation checks and are not study results.",
        "protocol_config": config.as_dict(),
        "audit": audit_dataset(events),
        "fold_manifest": manifest,
        "fold_manifest_checksum": manifest_checksum(manifest),
        "fold_counts": cgm["fold_counts"],
        "metrics": metrics,
        "predictions": predictions,
        "bootstrap_graph_typed_minus_multimodal": bootstrap,
    }
    payload = json.dumps(artifact, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
