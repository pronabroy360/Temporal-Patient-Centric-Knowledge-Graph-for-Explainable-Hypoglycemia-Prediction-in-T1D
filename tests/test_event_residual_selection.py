import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "summarize_loop_event_residual_candidates.py"
SPEC = importlib.util.spec_from_file_location("residual_selection", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class EventResidualSelectionTests(unittest.TestCase):
    def report(self, variant, l2, epochs, ap, brier):
        return {
            "model": "frozen_cgm_event_logit_residual", "metric_version": "threshold-grouped-ap-v2",
            "variant": variant, "l2": l2, "epochs": epochs, "fold": "outer-0", "manifest_sha256": "manifest",
            "window_verification": {"window_identity_sha256": "windows"},
            "groups": {"validation": {"participants": 2, "windows": 10, "positive_labels": 2,
                       "frozen_cgm": {"participant_macro_ap": 0.4, "brier_score": 0.1},
                       "event_residual": {"participant_macro_ap": ap, "brier_score": brier}}},
        }

    def test_selects_ap_then_brier_then_simpler_variant(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = []
            for variant in MODULE.EXPECTED_VARIANTS:
                for l2 in MODULE.EXPECTED_L2:
                    for epochs in MODULE.EXPECTED_EPOCHS:
                        path = Path(directory) / f"{variant}-{l2}-{epochs}.json"
                        ap = 0.45 if (variant, l2, epochs) == ("presence-quality", 0.001, 1) else 0.42
                        path.write_text(json.dumps(self.report(variant, l2, epochs, ap, 0.11)))
                        paths.append(path)
            result = MODULE.summarize(paths)
        self.assertEqual(result["selected_candidate"]["variant"], "presence-quality")
        self.assertEqual(result["selected_candidate"]["l2"], 0.001)

    def test_rejects_incomplete_grid(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "one.json"
            path.write_text(json.dumps(self.report("presence-quality", 0.0001, 1, 0.4, 0.1)))
            with self.assertRaisesRegex(ValueError, "twelve"):
                MODULE.summarize([path])


if __name__ == "__main__":
    unittest.main()
