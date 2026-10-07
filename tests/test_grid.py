import unittest
from datetime import datetime, timedelta, timezone

from t1d_tkg.grid import assign_to_grid


class GridAssignmentTests(unittest.TestCase):
    def test_assigns_nearby_observation_and_retains_offset(self):
        origin = datetime(2026, 1, 1, tzinfo=timezone.utc)
        result = assign_to_grid([origin + timedelta(seconds=301)], origin=origin, tolerance_seconds=2)
        self.assertEqual(result[0].grid_time, origin + timedelta(minutes=5))
        self.assertEqual(result[0].offset_seconds, 1)

    def test_does_not_interpolate_or_assign_outside_tolerance(self):
        origin = datetime(2026, 1, 1, tzinfo=timezone.utc)
        result = assign_to_grid([origin + timedelta(seconds=303)], origin=origin, tolerance_seconds=2)
        self.assertEqual(result, ())

    def test_rejects_nearest_time_tie(self):
        origin = datetime(2026, 1, 1, tzinfo=timezone.utc)
        result = assign_to_grid([origin + timedelta(seconds=299), origin + timedelta(seconds=301)], origin=origin + timedelta(minutes=5), tolerance_seconds=2)
        self.assertEqual(result, ())


if __name__ == "__main__":
    unittest.main()
