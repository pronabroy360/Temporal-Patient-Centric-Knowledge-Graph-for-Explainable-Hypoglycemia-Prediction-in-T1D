import gzip
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from compare_controlled_neural_archives import compare_first_gate
from t1d_tkg.metrics import METRIC_VERSION, average_precision
from t1d_tkg.neural_contract import CONTRACT_VERSION


class ControlledNeuralArchiveComparisonTests(unittest.TestCase):
    def write_archive(self, directory, variant, scores, **changes):
        directory.mkdir()
        predictions = directory / "predictions"
        predictions.mkdir()
        aps = []
        briers = []
        total_squared = 0.0
        for patient, values in scores.items():
            labels = [label for label, _ in values]
            probabilities = [score for _, score in values]
            aps.append(average_precision(labels, probabilities))
            squared = sum((score - label) ** 2 for label, score in values)
            briers.append(squared / len(values))
            total_squared += squared
            with gzip.open(predictions / f"validation-{patient}.jsonl.gz", "wt") as handle:
                for number, (label, score) in enumerate(values):
                    handle.write(json.dumps({
                        "patient_id": patient,
                        "index_time": f"2026-01-01T00:{number:02d}:00+00:00",
                        "label": label,
                        "score": score,
                    }) + "\n")
        windows = sum(len(values) for values in scores.values())
        report = {
            "complete": True, "contract_version": CONTRACT_VERSION,
            "variant": variant, "fold": "outer-0", "seed": 20261002,
            "hidden": 64, "epochs": 2, "batch_size": 4096, "workers": 3,
            "max_events": 64, "manifest_sha256": "manifest",
            "window_identity_sha256": "windows", "input_content_sha256": "content",
            "training_membership_sha256": "train", "optimizer": {"name": "AdamW"},
            "source_sha256": "source", "event_input_policy": "occurrence-replay-v1",
            "evaluation_scope": "validation", "metric_version": METRIC_VERSION,
            "prediction_identity_verified": True, "fixture_only": False, "mode": "train",
            "groups": {"validation": {
                "participants": len(scores), "windows": windows,
                "positive_labels": sum(label for values in scores.values() for label, _ in values),
                "ap_defined_participants": len(aps),
                "participant_macro_ap": sum(aps) / len(aps),
                "participant_macro_brier": sum(briers) / len(briers),
                "pooled_brier": total_squared / windows,
                "prediction_window_identity_sha256": "paired-validation-windows",
            }},
        }
        report.update(changes)
        (directory / "run.json").write_text(json.dumps(report))

    def test_compares_exactly_paired_controlled_runs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            labels = {"a": [(0, .1), (1, .9)], "b": [(0, .2), (1, .8)]}
            weaker = {"a": [(0, .8), (1, .2)], "b": [(0, .7), (1, .3)]}
            self.write_archive(root / "cgm", "cgm-mlp", labels)
            self.write_archive(root / "event", "clean-gru", weaker)
            result = compare_first_gate(root / "cgm", root / "event", draws=50, seed=7)
            self.assertEqual(result["windows"], 4)
            self.assertEqual(result["first_variant"], "cgm-mlp")
            self.assertGreater(result["participant_macro_ap"]["difference_first_minus_second"], 0)

    def test_rejects_different_training_seed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            rows = {"a": [(0, .1), (1, .9)], "b": [(0, .2), (1, .8)]}
            self.write_archive(root / "cgm", "cgm-mlp", rows)
            self.write_archive(root / "event", "clean-gru", rows, seed=20261003)
            with self.assertRaisesRegex(ValueError, "differ"):
                compare_first_gate(root / "cgm", root / "event", draws=10)

    def test_rejects_report_that_disagrees_with_predictions(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            rows = {"a": [(0, .1), (1, .9)], "b": [(0, .2), (1, .8)]}
            self.write_archive(root / "cgm", "cgm-mlp", rows)
            self.write_archive(root / "event", "clean-gru", rows)
            record = json.loads((root / "event" / "run.json").read_text())
            record["groups"]["validation"]["participant_macro_ap"] = 0.01
            (root / "event" / "run.json").write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError, "reported participant_macro_ap"):
                compare_first_gate(root / "cgm", root / "event", draws=10)


if __name__ == "__main__":
    unittest.main()
