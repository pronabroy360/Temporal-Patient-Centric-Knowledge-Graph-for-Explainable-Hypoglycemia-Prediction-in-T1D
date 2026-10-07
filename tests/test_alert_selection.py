import unittest
from datetime import datetime, timedelta, timezone

from t1d_tkg.episodes import select_alert_threshold, simulate_alerts


class AlertSelectionTests(unittest.TestCase):
    def test_simulator_applies_refractory_to_thresholded_scores(self):
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        times = [base + timedelta(minutes=5 * i) for i in range(10)]
        scores = [0.1, 0.8, 0.9, 0.2, 0.7, 0.1, 0.8, 0.8, 0.1, 0.1]
        alerts = simulate_alerts(times, scores, threshold=0.7, refractory_minutes=30)
        self.assertEqual(alerts, [times[1], times[7]])

    def test_threshold_selector_enforces_alert_budget(self):
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        times = [base + timedelta(minutes=5 * i) for i in range(12)]
        predictions = {"p": (times, [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.1, 0.1, 0.1])}
        episodes = {"p": [times[4], times[10]]}
        result = select_alert_threshold(predictions, episodes, {"p": 1440.0}, [0.2, 0.6, 0.85], horizon_minutes=30)
        self.assertIsNotNone(result["selected"])
        self.assertEqual(result["selected"]["threshold"], 0.2)
        self.assertTrue(all("feasible" in candidate for candidate in result["candidates"]))


if __name__ == "__main__":
    unittest.main()
