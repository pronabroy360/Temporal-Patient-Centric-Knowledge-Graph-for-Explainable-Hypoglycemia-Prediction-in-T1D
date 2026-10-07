#!/usr/bin/env python3
"""Run matched CGM and multimodal logistic smoke benchmarks."""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from t1d_tkg.evaluation import evaluate_loso_cgm, evaluate_loso_event_sequence, evaluate_loso_graph, evaluate_loso_multimodal
from t1d_tkg.synthetic import synthetic_events
from t1d_tkg.windows import build_prediction_windows


if __name__ == "__main__":
    events = synthetic_events()
    grouped = {patient: build_prediction_windows(events, patient_id=patient, horizon_minutes=30) for patient in sorted({event.patient_id for event in events})}
    result = evaluate_loso_cgm(grouped)
    result.update(evaluate_loso_multimodal(events, grouped))
    result.update(evaluate_loso_event_sequence(events, grouped))
    result.update(evaluate_loso_graph(events, grouped, relation_mode="typed"))
    result.update(evaluate_loso_graph(events, grouped, relation_mode="generic"))
    print(json.dumps(result, indent=2, sort_keys=True))
