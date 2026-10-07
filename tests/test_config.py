import unittest

from t1d_tkg.config import BenchmarkConfig, DEFAULT_CONFIG


class ConfigTests(unittest.TestCase):
    def test_default_config_is_valid_and_serializable(self):
        config = DEFAULT_CONFIG.as_dict()
        self.assertEqual(config["primary_horizon_minutes"], 30)
        self.assertEqual(config["low_threshold_mg_dl"], 70.0)

    def test_invalid_config_is_rejected(self):
        with self.assertRaises(ValueError):
            BenchmarkConfig(step_minutes=7).validate()
        with self.assertRaises(ValueError):
            BenchmarkConfig(alert_budget_unmatched_per_day=-1).validate()


if __name__ == "__main__":
    unittest.main()

