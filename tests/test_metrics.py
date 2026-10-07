import unittest

from t1d_tkg.metrics import average_precision


class AveragePrecisionTests(unittest.TestCase):
    def test_equal_scores_have_prevalence_ap_independent_of_order(self):
        self.assertEqual(average_precision([1, 0], [0.5, 0.5]), 0.5)
        self.assertEqual(average_precision([0, 1], [0.5, 0.5]), 0.5)

    def test_multiple_thresholds(self):
        # First threshold: recall 1/2, precision 1/2. Second: 1, 2/3.
        self.assertAlmostEqual(average_precision([1, 0, 1], [1, 1, 0]), 7 / 12)

    def test_no_positives_is_undefined(self):
        self.assertIsNone(average_precision([0, 0], [1, 0]))

    def test_length_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            average_precision([1, 0], [0.5])
