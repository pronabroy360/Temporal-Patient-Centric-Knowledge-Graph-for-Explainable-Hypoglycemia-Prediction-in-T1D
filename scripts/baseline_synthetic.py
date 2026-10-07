#!/usr/bin/env python3
"""Run the CGM-only rule/logistic smoke benchmark on synthetic data."""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from t1d_tkg.evaluation import evaluate_loso_cgm
from t1d_tkg.synthetic import synthetic_events
from t1d_tkg.windows import build_prediction_windows


if __name__ == "__main__":
    events = synthetic_events()
    grouped = {
        patient: build_prediction_windows(events, patient_id=patient, horizon_minutes=30)
        for patient in sorted({event.patient_id for event in events})
    }
    print(json.dumps(evaluate_loso_cgm(grouped), indent=2, sort_keys=True))
