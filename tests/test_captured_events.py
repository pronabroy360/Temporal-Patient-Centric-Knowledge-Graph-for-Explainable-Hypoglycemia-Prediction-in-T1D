import unittest
from datetime import datetime, timedelta, timezone

from t1d_tkg.captured_events import captured_event_features, iter_captured_event_features


class CapturedEventTests(unittest.TestCase):
    def test_uses_only_asof_120_minute_records(self):
        now = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
        rows = [
            (now - timedelta(minutes=10), "bolus", 2.0),
            (now - timedelta(minutes=20), "food", 30.0),
            (now + timedelta(minutes=1), "food", 99.0),
            (now - timedelta(minutes=121), "basal", 1.0),
        ]
        features = captured_event_features(now, rows)
        self.assertEqual(features, (0.0, 0.0, 1.0, 2.0, 10.0, 1.0, 30.0, 20.0, 0.0, 0.0, 0.0, 1.0))

    def test_boundary_missingness_and_basal_conflict(self):
        now = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
        rows = [(now-timedelta(minutes=120), 'bolus', 100.0),
                (now, 'bolus', None), (now, 'food', None),
                (now, 'basal', 1.0), (now, 'basal', 2.0)]
        result = captured_event_features(now, rows)
        self.assertEqual(result[1], 0.0)
        self.assertEqual(result[2:4], (1.0, 0.0))
        self.assertEqual(result[8:], (0.0, 1.0, 1.0, 1.0))
        self.assertEqual(result, captured_event_features(now, reversed(rows)))

    def test_rejects_reversed_index_times(self):
        now = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
        with self.assertRaises(ValueError):
            list(iter_captured_event_features([now, now-timedelta(minutes=1)], []))

    def test_rolling_features_match_each_window(self):
        base = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
        rows = [
            (base - timedelta(minutes=121), "basal", 0.7),
            (base, "bolus", 1.0),
            (base + timedelta(minutes=10), "food", 10.0),
            (base + timedelta(minutes=121), "bolus", 2.0),
        ]
        times = [base, base + timedelta(minutes=10), base + timedelta(minutes=121)]
        observed = list(iter_captured_event_features(times, rows))
        expected = [captured_event_features(time, rows) for time in times]
        self.assertEqual([features for _, features in observed], expected)
