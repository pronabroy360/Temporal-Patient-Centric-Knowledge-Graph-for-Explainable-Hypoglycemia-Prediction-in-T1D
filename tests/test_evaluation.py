import unittest
from datetime import datetime, timedelta, timezone

from t1d_tkg.episodes import confirmed_episode_onsets, match_alerts_to_episodes, suppress_alerts
from t1d_tkg.events import Event
from t1d_tkg.metrics import average_precision, brier_score, participant_macro_ap


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.base = datetime(2026, 1, 1, tzinfo=timezone.utc)

    def test_average_precision_and_participant_macro(self):
        self.assertAlmostEqual(average_precision([1, 0, 1], [0.9, 0.8, 0.7]), 5 / 6)
        self.assertIsNone(average_precision([0, 0], [0.9, 0.1]))
        self.assertAlmostEqual(brier_score([1, 0], [0.8, 0.2]), 0.04)
        value = participant_macro_ap({"a": ([1, 0], [0.9, 0.2]), "b": ([0, 0], [0.8, 0.1])})
        self.assertAlmostEqual(value, 1.0)

    def test_confirmed_runs_break_on_missing_and_emit_once(self):
        events = []
        for i, value in enumerate([80, 65, 60, 55, 80, 60, 55, 50]):
            if i == 5:  # leave a gap at 25 minutes
                continue
            events.append(Event(str(i), "p", "cgm", self.base + timedelta(minutes=5 * i), value, "mg/dL", availability_assumption="assumed_immediate", source_type="cgm"))
        self.assertEqual(confirmed_episode_onsets(events), [self.base + timedelta(minutes=5)])

    def test_alert_suppression_and_matching(self):
        alerts = [self.base, self.base + timedelta(minutes=10), self.base + timedelta(minutes=35)]
        self.assertEqual(suppress_alerts(alerts), [self.base, self.base + timedelta(minutes=35)])
        result = match_alerts_to_episodes([self.base, self.base + timedelta(minutes=35)], [self.base + timedelta(minutes=20), self.base + timedelta(minutes=100)], horizon_minutes=30)
        self.assertEqual(result["matched"], 1)
        self.assertEqual(result["missed_episodes"], 1)
        self.assertEqual(result["lead_times_minutes"], [20.0])


if __name__ == "__main__":
    unittest.main()
