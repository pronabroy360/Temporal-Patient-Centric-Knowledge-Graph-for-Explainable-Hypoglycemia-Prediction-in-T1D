import unittest

from t1d_tkg.calibration import expected_calibration_error, fit_platt_scaler, reliability_bins


class CalibrationTests(unittest.TestCase):
    def test_platt_scaler_is_bounded_and_deterministic(self):
        scores = [0.05, 0.1, 0.8, 0.95]
        labels = [0, 0, 1, 1]
        first = fit_platt_scaler(scores, labels, iterations=500)
        second = fit_platt_scaler(scores, labels, iterations=500)
        self.assertEqual(first, second)
        calibrated = first.predict(scores)
        self.assertTrue(all(0.0 < value < 1.0 for value in calibrated))
        self.assertLess(calibrated[0], calibrated[-1])

    def test_reliability_bins_include_endpoint_and_ece(self):
        labels = [0, 1, 1, 0]
        probabilities = [0.0, 0.49, 0.5, 1.0]
        bins = reliability_bins(labels, probabilities, n_bins=2)
        self.assertEqual([item["count"] for item in bins], [2, 2])
        self.assertAlmostEqual(expected_calibration_error(labels, probabilities, n_bins=2), 0.2525)


if __name__ == "__main__":
    unittest.main()
