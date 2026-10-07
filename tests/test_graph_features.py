import unittest
from datetime import datetime, timedelta, timezone

from t1d_tkg.evaluation import evaluate_loso_graph
from t1d_tkg.graph import build_asof_graph
from t1d_tkg.graph_features import graph_summary, graph_summary_for_sample
from t1d_tkg.synthetic import synthetic_events
from t1d_tkg.windows import build_prediction_windows


class GraphFeatureTests(unittest.TestCase):
    def test_relation_controls_have_fixed_width_and_future_invariance(self):
        events = synthetic_events()
        index = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=225)
        graph = build_asof_graph(events, patient_id="p1", index_time=index)
        typed = graph_summary(graph, relation_mode="typed")
        generic = graph_summary(graph, relation_mode="generic")
        none = graph_summary(graph, relation_mode="none")
        self.assertEqual(len(typed), len(generic))
        self.assertEqual(len(typed), len(none))
        self.assertNotEqual(typed, generic)
        self.assertNotEqual(typed, none)
        self.assertNotIn("p1-future-meal", graph.node_ids())

    def test_graph_loso_smoke_runner(self):
        events = synthetic_events()
        grouped = {
            patient: build_prediction_windows(events, patient_id=patient, horizon_minutes=30)
            for patient in sorted({event.patient_id for event in events})
        }
        result = evaluate_loso_graph(events, grouped, relation_mode="typed", include_predictions=True)
        self.assertIn("logistic_graph_typed", result)
        self.assertEqual(set(result["predictions"]["logistic_graph_typed"]), {"p1", "p2"})

    def test_sample_graph_uses_history_support(self):
        events = synthetic_events()
        sample = next(s for s in build_prediction_windows(events, patient_id="p1", horizon_minutes=30) if s.index_time.minute == 45)
        features = graph_summary_for_sample(sample, events)
        self.assertTrue(any(value > 0 for value in features))


if __name__ == "__main__":
    unittest.main()

