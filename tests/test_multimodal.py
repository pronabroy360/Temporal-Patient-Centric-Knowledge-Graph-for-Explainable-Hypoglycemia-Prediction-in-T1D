import unittest
from datetime import datetime, timedelta, timezone

from t1d_tkg.events import Event
from t1d_tkg.multimodal import multimodal_summary
from t1d_tkg.windows import WindowSample, build_prediction_windows


class MultimodalTests(unittest.TestCase):
    def test_future_and_late_events_are_not_features(self):
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        events = []
        for i in range(31):
            timestamp = base - timedelta(minutes=120) + timedelta(minutes=5 * i)
            events.append(Event(f"cgm-{i}", "p", "cgm", timestamp, 120, "mg/dL", availability_assumption="assumed_immediate", source_type="cgm"))
        events += [
            Event("past-meal", "p", "meal", base - timedelta(minutes=10), 30, "g", availability_assumption="assumed_immediate", source_type="self_report"),
            Event("late-past-meal", "p", "meal", base - timedelta(minutes=20), 99, "g", available_time=base + timedelta(minutes=5), source_type="self_report"),
            Event("future-meal", "p", "meal", base + timedelta(minutes=5), 88, "g", availability_assumption="assumed_immediate", source_type="self_report"),
        ]
        sample = next(s for s in build_prediction_windows(events, patient_id="p", horizon_minutes=30) if s.index_time == base)
        features = multimodal_summary(sample, events)
        self.assertEqual(features[13], 30.0)  # carbohydrate sum, after 9 CGM features + 3 insulin + basal
        self.assertEqual(features[14], 1.0)


if __name__ == "__main__":
    unittest.main()
