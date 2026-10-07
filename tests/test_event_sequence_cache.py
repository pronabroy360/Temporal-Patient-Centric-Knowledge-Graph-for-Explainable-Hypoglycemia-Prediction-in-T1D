import unittest
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from t1d_tkg.event_sequence_cache import EVENT_FEATURE_WIDTH, iter_sequence_features
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_loop_event_sequence_linear_pilot import sequence_partition


def record(time, modality, value, known=True):
    return {"occurrence_time": time.isoformat(), "modality": modality, "subtype": "normal", "model_value": value if known else None,
            "model_value_known": known, "same_time_variant_count": 1, "exact_duplicate_count": 0}


class CachedSequenceTests(unittest.TestCase):
    def test_newest_events_and_unknown_values_are_masked(self):
        now = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
        rows = [record(now-timedelta(minutes=30), "food", 10), record(now-timedelta(minutes=5), "bolus", None, False)]
        _, features, active, dropped = next(iter_sequence_features([now], rows, max_events=1))
        self.assertEqual(len(features), EVENT_FEATURE_WIDTH)
        self.assertEqual((active, dropped), (2, 1))
        self.assertEqual(features[0], 1.0)
        self.assertEqual(features[-3], 0.0)  # unknown value is masked, not a clinical zero

    def test_left_history_boundary_is_excluded(self):
        now = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
        rows = [record(now-timedelta(minutes=120), "food", 10), record(now, "food", 20)]
        _, _, active, _ = next(iter_sequence_features([now], rows, max_events=2))
        self.assertEqual(active, 1)
