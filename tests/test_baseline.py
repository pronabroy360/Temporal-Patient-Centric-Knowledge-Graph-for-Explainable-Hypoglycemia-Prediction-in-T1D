import unittest
from datetime import datetime, timedelta, timezone

from t1d_tkg.evaluation import evaluate_loso_cgm
from t1d_tkg.features import cgm_summary
from t1d_tkg.events import Event
from t1d_tkg.synthetic import synthetic_events
from t1d_tkg.windows import build_prediction_windows
from t1d_tkg.manifest import build_loso_manifest
from t1d_tkg.baselines import persistence_slope_score_from_current_and_slope, persistence_slope_score_from_values
from t1d_tkg.logistic import fit_streaming_logistic
from t1d_tkg.features import cgm_recent_features


class BaselineTests(unittest.TestCase):
    def test_raw_value_rule_detects_downward_crossing(self):
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(persistence_slope_score_from_values(base, 100, base + timedelta(minutes=5), 90, horizon_minutes=30), 1.0)
        self.assertEqual(persistence_slope_score_from_current_and_slope(90, -10, horizon_minutes=30), 1.0)

    def test_streaming_logistic_learns_from_repeatable_rows(self):
        rows = [((0.0,), 0), ((0.1,), 0), ((0.9,), 1), ((1.0,), 1)]
        model = fit_streaming_logistic(lambda: iter(rows), epochs=40, learning_rate=0.05)
        self.assertGreater(model.predict_proba([(1.0,)])[0], model.predict_proba([(0.0,)])[0])

    def test_recent_features_use_elapsed_time(self):
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(cgm_recent_features(base, 110, base + timedelta(minutes=10), 100), (100, -5.0))
    def test_loso_runner_returns_fold_isolated_results(self):
        events = synthetic_events()
        grouped = {
            patient: build_prediction_windows(events, patient_id=patient, horizon_minutes=30)
            for patient in sorted({event.patient_id for event in events})
        }
        result = evaluate_loso_cgm(grouped, include_predictions=True, manifest=build_loso_manifest(grouped))
        self.assertEqual(set(result["fold_counts"]), {"p1", "p2"})
        self.assertEqual(result["fold_counts"]["p1"]["train"], result["fold_counts"]["p2"]["test"])
        self.assertEqual(result["fold_counts"]["p2"]["train"], result["fold_counts"]["p1"]["test"])
        self.assertIsNotNone(result["rule"]["participant_macro_ap"])
        self.assertIsNotNone(result["logistic_cgm"]["macro_brier"])
        self.assertEqual(set(result["predictions"]["logistic_cgm"]), {"p1", "p2"})

    def test_cgm_slope_uses_elapsed_time_across_a_gap(self):
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        events = []
        for i in range(31):
            if i == 23:
                continue
            value = 110.0 if i == 22 else (100.0 if i == 24 else 120.0)
            events.append(Event(f"cgm-{i}", "p", "cgm", base + timedelta(minutes=5 * i), value, "mg/dL", availability_assumption="assumed_immediate", source_type="cgm"))
        sample = next(s for s in __import__("t1d_tkg.windows", fromlist=["build_prediction_windows"]).build_prediction_windows(events, patient_id="p", horizon_minutes=30) if s.index_time == base + timedelta(minutes=120))
        self.assertAlmostEqual(cgm_summary(sample)[1], -5.0)


if __name__ == "__main__":
    unittest.main()
