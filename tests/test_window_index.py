import tempfile
import unittest
import gzip
from datetime import datetime, timedelta, timezone
from pathlib import Path

from t1d_tkg.events import Event
from t1d_tkg.manifest import build_loso_manifest, fold_by_patient
from t1d_tkg.window_index import iter_window_index, validate_window_index, validate_window_index_directory, write_window_index
from t1d_tkg.windows import build_prediction_windows


class WindowIndexTests(unittest.TestCase):
    def test_round_trip_is_metadata_only_and_reconciles_counts(self):
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        events = [Event(f"e{i}", "p", "cgm", base + timedelta(minutes=5 * i), 100.0) for i in range(40)]
        samples = build_prediction_windows(events, patient_id="p", horizon_minutes=30)
        with tempfile.TemporaryDirectory() as directory:
            summary = write_window_index(Path(directory) / "index.jsonl", samples, fold_by_patient={"p": "test-p"})
            rows = list(iter_window_index(summary["path"]))
            validation = validate_window_index(summary["path"])
        self.assertEqual(summary["records"], len(samples))
        self.assertEqual(summary["known_labels"], len(samples) - 6)
        self.assertEqual(rows[0]["fold_id"], "test-p")
        self.assertNotIn("history", rows[0])
        self.assertEqual(validation["participants"], 1)
        self.assertEqual(len(validation["sha256"]), 64)

    def test_duplicate_sample_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.jsonl"
            path.write_text('{"record_type":"window_index"}\n{"sample_id":"x","patient_id":"p","index_time":"2026-01-01T00:00:00+00:00","horizon_minutes":30,"input_eligible":true,"label_status":"known","label":0}\n{"sample_id":"x","patient_id":"p","index_time":"2026-01-01T00:05:00+00:00","horizon_minutes":30,"input_eligible":true,"label_status":"known","label":0}\n')
            with self.assertRaises(ValueError):
                validate_window_index(path)

    def test_manifest_fold_mismatch_is_rejected(self):
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        sample = build_prediction_windows(
            [Event(f"e{i}", "p", "cgm", base + timedelta(minutes=5 * i), 100.0) for i in range(40)],
            patient_id="p", horizon_minutes=30,
        )[0]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "index.jsonl"
            write_window_index(path, [sample], fold_by_patient={"p": "wrong-fold"})
            manifest = build_loso_manifest(["p"])
            with self.assertRaises(ValueError):
                validate_window_index(path, expected_folds=fold_by_patient(manifest))

    def test_compressed_partition_is_readable(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "index.jsonl.gz"
            with gzip.open(path, "wt", encoding="utf-8") as handle:
                handle.write('{"record_type":"window_index","protocol_version":"test"}\n')
                handle.write('{"sample_id":"x","patient_id":"p","fold_id":null,"index_time":"2026-01-01T00:00:00+00:00","horizon_minutes":30,"input_eligible":true,"label_status":"known","label":0}\n')
            self.assertEqual(validate_window_index(path)["records"], 1)
            self.assertEqual(validate_window_index_directory(Path(directory))["partitions"], 1)


if __name__ == "__main__":
    unittest.main()
