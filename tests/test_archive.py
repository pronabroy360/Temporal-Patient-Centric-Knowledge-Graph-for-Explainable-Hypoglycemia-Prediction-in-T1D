import unittest

from t1d_tkg.archive import validate_prediction_archive
from t1d_tkg.manifest import build_loso_manifest


class ArchiveTests(unittest.TestCase):
    def test_prediction_archive_matches_manifest(self):
        manifest = build_loso_manifest(["p1", "p2"])
        predictions = {
            "model": {
                "p1": {"labels": [0, 1], "scores": [0.1, 0.9]},
                "p2": {"labels": [1], "scores": [0.8]},
            }
        }
        validate_prediction_archive(predictions, manifest)

    def test_prediction_archive_rejects_unknown_participant_and_bad_probability(self):
        manifest = build_loso_manifest(["p1", "p2"])
        predictions = {
            "model": {
                "p1": {"labels": [0], "scores": [1.2]},
                "p2": {"labels": [1], "scores": [0.8]},
                "p3": {"labels": [0], "scores": [0.1]},
            }
        }
        with self.assertRaises(ValueError):
            validate_prediction_archive(predictions, manifest)


if __name__ == "__main__":
    unittest.main()

