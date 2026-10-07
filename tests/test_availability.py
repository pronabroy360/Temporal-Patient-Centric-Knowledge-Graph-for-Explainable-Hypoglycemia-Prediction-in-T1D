import unittest
from datetime import datetime, timedelta, timezone

from t1d_tkg.events import Event
from t1d_tkg.graph import build_asof_graph


class AvailabilityTests(unittest.TestCase):
    def test_unknown_availability_is_excluded(self):
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        events = [
            Event("cgm", "p", "cgm", base, 100, "mg/dL", availability_assumption="assumed_immediate", source_type="cgm"),
            Event("late", "p", "meal", base - timedelta(minutes=5), 40, "g", available_time=base + timedelta(minutes=5), source_type="self_report"),
        ]
        graph = build_asof_graph(events, patient_id="p", index_time=base)
        self.assertNotIn("late", graph.node_ids())

    def test_unknown_assumption_does_not_become_immediate(self):
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        event = Event("unknown", "p", "meal", base, 40, "g", source_type="self_report")
        self.assertFalse(event.available_by(base))

    def test_delayed_future_observation_can_label_but_not_input(self):
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        events = []
        for i in range(31):
            timestamp = base - timedelta(minutes=120) + timedelta(minutes=5 * i)
            available = timestamp if i <= 24 else base + timedelta(minutes=60)
            value = 60.0 if i == 25 else 120.0
            events.append(Event(f"cgm-{i}", "p", "cgm", timestamp, value, "mg/dL", available_time=available, source_type="cgm"))
        from t1d_tkg.windows import build_prediction_windows
        samples = build_prediction_windows(events, patient_id="p", horizon_minutes=30)
        sample = next(s for s in samples if s.index_time == base)
        self.assertTrue(sample.input_eligible)
        self.assertEqual(sample.label, 1)
        self.assertEqual(sample.history[-1].value, 120.0)


if __name__ == "__main__":
    unittest.main()
