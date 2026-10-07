import unittest

from t1d_tkg.uncertainty import paired_cluster_bootstrap


class UncertaintyTests(unittest.TestCase):
    def test_paired_bootstrap_is_deterministic_and_clustered(self):
        predictions = {
            "a": {
                "p1": ([1, 0], [0.9, 0.1]),
                "p2": ([1, 0], [0.6, 0.4]),
            },
            "b": {
                "p1": ([1, 0], [0.8, 0.2]),
                "p2": ([1, 0], [0.4, 0.6]),
            },
        }
        first = paired_cluster_bootstrap(predictions, model_a="a", model_b="b", draws=100, seed=7)
        second = paired_cluster_bootstrap(predictions, model_a="a", model_b="b", draws=100, seed=7)
        self.assertEqual(first, second)
        self.assertEqual(first["participants"], ["p1", "p2"])
        self.assertEqual(first["valid_replicates"], 100)
        self.assertAlmostEqual(first["observed"]["difference"], 0.25)

    def test_ap_no_positive_replicate_is_reported_undefined(self):
        predictions = {
            "a": {"positive": ([1, 0], [0.9, 0.1]), "negative": ([0], [0.2])},
            "b": {"positive": ([1, 0], [0.8, 0.2]), "negative": ([0], [0.1])},
        }
        result = paired_cluster_bootstrap(predictions, model_a="a", model_b="b", draws=50, seed=1)
        self.assertGreater(result["undefined_replicates"], 0)
        self.assertEqual(result["valid_replicates"] + result["undefined_replicates"], 50)


if __name__ == "__main__":
    unittest.main()
