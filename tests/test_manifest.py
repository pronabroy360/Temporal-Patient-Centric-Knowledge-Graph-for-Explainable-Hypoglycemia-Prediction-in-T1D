import tempfile
import unittest
from pathlib import Path

from t1d_tkg.manifest import build_hashed_kfold_manifest, build_loso_manifest, fold_by_patient, load_manifest, manifest_checksum, save_manifest, validate_manifest


class ManifestTests(unittest.TestCase):
    def test_rejects_holdout_overlap_and_incomplete_fold(self):
        manifest = build_loso_manifest(['a', 'b', 'c'])
        manifest['locked_holdout_patients'] = ['a']
        with self.assertRaisesRegex(ValueError, 'holdout'):
            validate_manifest(manifest)
        manifest['locked_holdout_patients'] = ['d']
        manifest['folds'][0]['train_patients'] = []
        with self.assertRaisesRegex(ValueError, 'cover'):
            validate_manifest(manifest)
    def test_fold_by_patient_is_complete_and_deterministic(self):
        manifest = build_loso_manifest(["b", "a"])
        self.assertEqual(fold_by_patient(manifest), {"a": "test-a", "b": "test-b"})

    def test_hashed_kfold_has_disjoint_validation_and_complete_test_coverage(self):
        manifest = build_hashed_kfold_manifest([str(number) for number in range(20)], folds=5)
        validate_manifest(manifest)
        self.assertEqual(len(fold_by_patient(manifest)), 20)
        for fold in manifest["folds"]:
            self.assertFalse(set(fold["train_patients"]) & set(fold["validation_patients"]))
    def test_loso_manifest_is_deterministic_and_round_trips(self):
        manifest = build_loso_manifest(["p2", "p1", "p2"])
        validate_manifest(manifest, expected_patients=["p1", "p2"])
        self.assertEqual(manifest["folds"][0]["test_patients"], ["p1"])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "folds.json"
            checksum = save_manifest(path, manifest)
            self.assertEqual(load_manifest(path), manifest)
            self.assertEqual(checksum, manifest_checksum(manifest))

    def test_manifest_rejects_cross_patient_fold_overlap_and_duplicate_test(self):
        manifest = build_loso_manifest(["p1", "p2"])
        manifest["folds"][0]["train_patients"] = ["p1"]
        with self.assertRaises(ValueError):
            validate_manifest(manifest)
        manifest = build_loso_manifest(["p1", "p2"])
        manifest["folds"][1]["test_patients"] = ["p1"]
        with self.assertRaises(ValueError):
            validate_manifest(manifest)


if __name__ == "__main__":
    unittest.main()
