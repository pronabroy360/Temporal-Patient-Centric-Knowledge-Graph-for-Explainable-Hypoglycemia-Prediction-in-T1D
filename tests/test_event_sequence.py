import unittest
from datetime import datetime, timedelta, timezone

from t1d_tkg.event_sequence import event_sequence_summary
from t1d_tkg.events import Event
from t1d_tkg.windows import build_prediction_windows


class EventSequenceTests(unittest.TestCase):
    def test_recent_events_are_ordered_and_as_of_filtered(self):
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        events = [
            Event(f"cgm-{i}", "p", "cgm", base - timedelta(minutes=120) + timedelta(minutes=5 * i), 120, "mg/dL", availability_assumption="assumed_immediate", source_type="cgm")
            for i in range(31)
        ]
        events += [
            Event("meal-old", "p", "meal", base - timedelta(minutes=30), 20, "g", availability_assumption="assumed_immediate", source_type="self_report"),
            Event("exercise-new", "p", "exercise", base - timedelta(minutes=5), attributes={"duration_minutes": 10}, availability_assumption="assumed_immediate", source_type="self_report"),
            Event("meal-late", "p", "meal", base - timedelta(minutes=10), 99, "g", available_time=base + timedelta(minutes=1), source_type="self_report"),
        ]
        sample = next(s for s in build_prediction_windows(events, patient_id="p", horizon_minutes=30) if s.index_time == base)
        features = event_sequence_summary(sample, events, max_events=2)
        width = 11  # seven type indicators plus age, value flag, value, duration
        self.assertEqual(len(features), 9 + 2 * width)
        # The most recent admissible event is exercise; late data is absent.
        second = 9 + width
        self.assertAlmostEqual(features[second + 7], 5 / 120)
        self.assertEqual(features[second + 3], 1.0)  # exercise type indicator

    def test_interval_duration_is_capped_at_index_time(self):
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        events = [
            Event(f"cgm-{i}", "p", "cgm", base - timedelta(minutes=120) + timedelta(minutes=5 * i), 120, "mg/dL", availability_assumption="assumed_immediate", source_type="cgm")
            for i in range(31)
        ]
        events.append(Event("exercise", "p", "exercise", base - timedelta(minutes=10), end_time=base + timedelta(minutes=90), availability_assumption="assumed_immediate", source_type="self_report"))
        sample = next(s for s in build_prediction_windows(events, patient_id="p", horizon_minutes=30) if s.index_time == base)
        features = event_sequence_summary(sample, events, max_events=1)
        self.assertAlmostEqual(features[9 + 7 + 3], 10 / 120)


if __name__ == "__main__":
    unittest.main()
