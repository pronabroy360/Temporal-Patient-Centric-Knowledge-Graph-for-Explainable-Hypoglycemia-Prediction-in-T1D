import unittest
from datetime import datetime, timedelta, timezone

from t1d_tkg.event_alignment import aligned_event_counts


class EventAlignmentTests(unittest.TestCase):
    def test_asof_history_includes_current_and_excludes_future(self):
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        windows = [base + timedelta(minutes=minute) for minute in (60, 120)]
        events = [base, base + timedelta(minutes=60), base + timedelta(minutes=121)]
        self.assertEqual(list(aligned_event_counts(windows, events, lookback_minutes=60)), [(windows[0], 2), (windows[1], 1)])

    def test_rejects_unordered_windows(self):
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        with self.assertRaises(ValueError):
            list(aligned_event_counts([base + timedelta(minutes=5), base], [], lookback_minutes=30))
