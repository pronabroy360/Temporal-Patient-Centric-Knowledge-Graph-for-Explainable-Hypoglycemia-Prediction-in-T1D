import unittest
import tempfile
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from t1d_tkg.event_residual import (
    PRESENCE_QUALITY_FEATURE_NAMES, VALUE_TIMING_FEATURE_NAMES, fit_streaming_event_residual,
    residual_features,
)
from t1d_tkg.logistic import LogisticModel
from t1d_tkg.feature_cache import write_partition as write_cgm_partition
from t1d_tkg.event_cache import write_partition as write_event_partition
from run_loop_event_residual_pilot import join_partition


class EventResidualTests(unittest.TestCase):
    def test_feature_variants_are_prespecified_subsets(self):
        summary = tuple(float(value) for value in range(12))
        self.assertEqual(len(residual_features(summary, "presence-quality")), len(PRESENCE_QUALITY_FEATURE_NAMES))
        self.assertEqual(residual_features(summary, "value-timing"), summary)
        self.assertEqual(len(VALUE_TIMING_FEATURE_NAMES), 12)

    def test_zero_initialized_residual_reproduces_frozen_base_before_fitting(self):
        base = LogisticModel((100.0,), (10.0,), (-1.0,), 0.0)
        rows = lambda: iter([((100.0,), (0.0, 1.0), 0), ((90.0,), (1.0, 0.0), 1)])
        model = fit_streaming_event_residual(rows, base, epochs=0, learning_rate=0.1, l2=0.01)
        self.assertEqual(model.intercept, 0.0)
        self.assertEqual(model.weights, (0.0, 0.0))
        self.assertEqual(model.predict_proba(base, (90.0,), (1.0, 0.0)), base.predict_proba([(90.0,)])[0])

    def test_linear_predictor_rejects_wrong_width(self):
        with self.assertRaises(ValueError):
            LogisticModel((0.0,), (1.0,), (1.0,), 0.0).linear_predictor((1.0, 2.0))

    def test_cached_partition_join_is_asof_and_preserves_unknownness(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            base = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
            cgm_path = directory / "features-00.tsv.gz"
            write_cgm_partition(cgm_path, [
                ("p", base.isoformat(), 0, 100.0, -1.0),
                ("p", (base + timedelta(minutes=10)).isoformat(), 1, 90.0, -2.0),
            ])
            event_paths = []
            for modality in ("basal", "bolus", "food"):
                path = directory / f"events-{modality}-00.jsonl.gz"
                records = []
                if modality == "bolus":
                    records.append({"event_id": "x", "patient_id": "p", "occurrence_time": base.isoformat(),
                                    "modality": modality, "subtype": "normal", "model_value": 2.0,
                                    "model_value_unit": "U", "model_value_known": True, "source_fields": {},
                                    "exact_duplicate_count": 0, "same_time_variant_count": 1})
                if modality == "food":
                    records.append({"event_id": "y", "patient_id": "p", "occurrence_time": base.isoformat(),
                                    "modality": modality, "subtype": "reported_meal", "model_value": None,
                                    "model_value_unit": "exchanges", "model_value_known": False, "source_fields": {},
                                    "exact_duplicate_count": 0, "same_time_variant_count": 1})
                write_event_partition(path, modality, records)
                event_paths.append(path)
            rows = list(join_partition(cgm_path, event_paths, "value-timing"))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][3][2:5], (1.0, 2.0, 0.0))
        self.assertEqual(rows[0][3][5:8], (1.0, 0.0, 0.0))


if __name__ == "__main__":
    unittest.main()
