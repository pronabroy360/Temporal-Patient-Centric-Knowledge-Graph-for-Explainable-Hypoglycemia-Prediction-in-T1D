import unittest
from datetime import datetime, timedelta, timezone

from t1d_tkg.graph import build_asof_graph
from t1d_tkg.synthetic import synthetic_events
from t1d_tkg.windows import build_prediction_windows


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.events = synthetic_events()
        self.base = datetime(2026, 1, 1, tzinfo=timezone.utc)

    def test_incomplete_future_is_unknown(self):
        samples = build_prediction_windows(self.events, patient_id="p1", horizon_minutes=30)
        sample = next(s for s in samples if s.index_time == self.base + timedelta(minutes=345))
        self.assertTrue(sample.input_eligible)
        self.assertEqual(sample.label_status, "unknown")
        self.assertIsNone(sample.label)

    def test_future_low_is_positive_and_current_low_is_ineligible(self):
        samples = build_prediction_windows(self.events, patient_id="p1", horizon_minutes=30)
        pre_low = next(s for s in samples if s.index_time == self.base + timedelta(minutes=230))
        self.assertEqual(pre_low.label, 1)
        current_low = next(s for s in samples if s.index_time == self.base + timedelta(minutes=250))
        self.assertFalse(current_low.input_eligible)
        self.assertIn("current_glucose_below_70", current_low.eligibility_reason)

    def test_graph_is_as_of_and_patient_scoped(self):
        index = self.base + timedelta(minutes=225)
        graph = build_asof_graph(self.events, patient_id="p1", index_time=index)
        self.assertNotIn("p1-future-meal", graph.node_ids())
        self.assertTrue(all(node.get("patient_id") in {None, "p1"} for node in graph.nodes))
        self.assertTrue(all(edge["source"] in graph.node_ids() and edge["target"] in graph.node_ids() for edge in graph.edges))

    def test_threshold_70_is_not_low(self):
        events = []
        from t1d_tkg.events import Event
        for event in self.events:
            if event.patient_id == "p2" and event.event_type == "cgm" and event.value is not None and event.value < 70:
                event = Event(event.event_id, event.patient_id, event.event_type, event.event_time, 70.0, "mg/dL", availability_assumption="assumed_immediate", source_type="cgm")
            events.append(event)
        samples = build_prediction_windows(events, patient_id="p2", horizon_minutes=30)
        after = next(s for s in samples if s.index_time == self.base + timedelta(days=1000, minutes=240))
        self.assertEqual(after.label, 0)


if __name__ == "__main__":
    unittest.main()
