import unittest
from datetime import datetime, timezone

from t1d_tkg.events import Event
from t1d_tkg.range_policy import filter_cgm_events, get_range_policy


class RangePolicyTests(unittest.TestCase):
    def test_primary_retains_all_numeric_values(self):
        policy = get_range_policy("observed_numeric")
        self.assertTrue(policy.accepts(1.0))
        self.assertTrue(policy.accepts(592.0))
        self.assertFalse(policy.accepts(None))

    def test_sensitivity_bounds_are_explicit(self):
        policy = get_range_policy("sensitivity_40_400")
        self.assertTrue(policy.accepts(40.0))
        self.assertFalse(policy.accepts(39.99))
        self.assertFalse(policy.accepts(400.01))

    def test_filter_stream_keeps_auxiliary_events(self):
        now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        events = [Event("low", "p", "cgm", now, 10), Event("meal", "p", "meal", now, 20)]
        kept = list(filter_cgm_events(events, get_range_policy("sensitivity_40_400")))
        self.assertEqual([event.event_id for event in kept], ["meal"])


if __name__ == "__main__":
    unittest.main()
