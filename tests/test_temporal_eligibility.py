import unittest
from datetime import datetime, timedelta, timezone

from t1d_tkg.temporal_eligibility import audit_cadence_tolerant, audit_exact_grid, audit_logical_grid, logical_grid_episode_counts, logical_grid_window_metadata


class TemporalEligibilityTests(unittest.TestCase):
    def test_logical_grid_metadata_matches_window_counts(self):
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        readings = {base + timedelta(minutes=5 * i): 100.0 for i in range(40)}
        rows = list(logical_grid_window_metadata(readings, threshold=70, tolerance_seconds=1))
        self.assertEqual(len(rows), 40)
        self.assertEqual(sum(row["input_eligible"] for row in rows), 17)
    def test_complete_exact_grid_produces_eligible_known_positive_index(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        readings = {start + timedelta(minutes=5 * index): 100.0 for index in range(40)}
        readings[start + timedelta(minutes=5 * 30)] = 60.0
        result = audit_exact_grid(readings, threshold=70.0)
        self.assertGreater(result["input_eligible"], 0)
        self.assertGreater(result["positive_labels"], 0)

    def test_irregular_future_is_unknown_not_filled(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        readings = {start + timedelta(minutes=5 * index): 100.0 for index in range(31)}
        del readings[start + timedelta(minutes=5 * 30)]
        readings[start + timedelta(minutes=151)] = 60.0
        result = audit_exact_grid(readings, threshold=70.0)
        self.assertEqual(result["positive_labels"], 0)

    def test_input_eligibility_does_not_require_future_label(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        readings = {start + timedelta(minutes=5 * index): 100.0 for index in range(25)}
        result = audit_exact_grid(readings, threshold=70.0)
        self.assertGreater(result["input_eligible"], 0)
        self.assertLess(result["known_labels"], result["timestamps"])

    def test_cadence_tolerance_uses_relative_intervals_not_epoch_phase(self):
        start = datetime(2026, 1, 1, 0, 0, 17, tzinfo=timezone.utc)
        readings = {start + timedelta(seconds=299 * index): 100.0 for index in range(32)}
        self.assertEqual(audit_cadence_tolerant(readings, threshold=70.0, tolerance_seconds=0)["input_eligible"], 0)
        self.assertGreater(audit_cadence_tolerant(readings, threshold=70.0, tolerance_seconds=1)["input_eligible"], 0)

    def test_logical_grid_allows_one_genuine_missing_slot_in_history(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        readings = {start + timedelta(minutes=5 * index): 100.0 for index in range(33) if index != 10}
        result = audit_logical_grid(readings, threshold=70.0, tolerance_seconds=1)
        self.assertGreater(result["input_eligible"], 0)

    def test_logical_episode_requires_observed_boundaries_and_recovery(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        values = [100, 100, 60, 60, 60, 100, 100, 100]
        readings = {start + timedelta(minutes=5 * index): value for index, value in enumerate(values)}
        result = logical_grid_episode_counts(readings, threshold=70.0, tolerance_seconds=1)
        self.assertEqual(result["confirmed_episode_onsets"], 1)
        self.assertEqual(result["censored_boundary_low_runs"], 0)
        self.assertEqual(result["unconfirmed_short_low_runs"], 0)


if __name__ == "__main__":
    unittest.main()
