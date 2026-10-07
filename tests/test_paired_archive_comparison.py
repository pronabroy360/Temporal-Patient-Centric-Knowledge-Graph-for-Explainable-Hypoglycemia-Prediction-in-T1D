import gzip
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from compare_loop_pilot_archives import compare
from t1d_tkg.metrics import METRIC_VERSION


class PairedArchiveComparisonTests(unittest.TestCase):
    def write_archive(self, directory, scores, rule_scores=None, recovered_layout=False):
        directory.mkdir()
        report = {
            "metric_version": METRIC_VERSION,
            "manifest_sha256": "manifest", "window_verification": {"window_identity_sha256": "windows"},
            "groups": {"validation": {"windows": 4, "positive_labels": 2}},
        }
        record = {"complete": True, **report} if recovered_layout else {
            "complete": True, "metric_version": METRIC_VERSION, "report": report,
        }
        (directory / "run.json").write_text(json.dumps(record))
        prediction_directory = directory / "predictions" if recovered_layout else directory
        prediction_directory.mkdir(exist_ok=True)
        for patient, values in scores.items():
            with gzip.open(prediction_directory / f"validation-{patient}.jsonl.gz", "wt") as handle:
                for number, (label, score) in enumerate(values):
                    row = {"patient_id": patient, "index_time": str(number), "label": label, "score": score}
                    if rule_scores is not None:
                        row["rule_score"] = rule_scores[patient][number]
                    handle.write(json.dumps(row) + "\n")

    def test_paired_comparison_reconciles_and_preserves_orientation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            labels = {"a": [(0, .1), (1, .9)], "b": [(0, .2), (1, .8)]}
            weaker = {"a": [(0, .8), (1, .2)], "b": [(0, .7), (1, .3)]}
            self.write_archive(root / "first", labels)
            self.write_archive(root / "second", weaker)
            result = compare(root / "first", root / "second", group="validation", draws=50, seed=7)
            self.assertEqual(result["windows"], 4)
            self.assertGreater(result["participant_macro_ap"]["difference_first_minus_second"], 0)
            self.assertLess(result["pooled_brier"]["difference_first_minus_second"], 0)
            self.assertEqual(result["participant_macro_ap"]["positive_difference_participants"], 2)

    def test_can_compare_two_score_fields_in_one_aligned_archive(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            scores = {"a": [(0, .1), (1, .9)], "b": [(0, .2), (1, .8)]}
            rules = {"a": [.8, .2], "b": [.7, .3]}
            self.write_archive(root / "both", scores, rules)
            result = compare(root / "both", root / "both", group="validation", draws=50, seed=7,
                             first_score_field="score", second_score_field="rule_score")
            self.assertGreater(result["participant_macro_ap"]["difference_first_minus_second"], 0)
            self.assertEqual(result["second_score_field"], "rule_score")

    def test_accepts_recovered_flat_metadata_and_nested_predictions(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = {"a": [(0, .1), (1, .9)], "b": [(0, .2), (1, .8)]}
            second = {"a": [(0, .8), (1, .2)], "b": [(0, .7), (1, .3)]}
            self.write_archive(root / "first", first, recovered_layout=True)
            self.write_archive(root / "second", second)
            result = compare(root / "first", root / "second", group="validation", draws=10, seed=7)
            self.assertEqual(result["participants"], 2)
            self.assertGreater(result["participant_macro_ap"]["difference_first_minus_second"], 0)

    def test_rejects_mismatched_row_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_archive(root / "first", {"a": [(0, .1), (1, .9)], "b": []})
            self.write_archive(root / "second", {"a": [(1, .1), (0, .9)], "b": []})
            with self.assertRaisesRegex(ValueError, "differ"):
                compare(root / "first", root / "second", group="validation", draws=10, seed=1)
