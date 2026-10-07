import gzip
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_loop_window_event_alignment import SPECS
from build_loop_event_instance_cache import canonical_records
from t1d_tkg.event_cache import EVENT_CACHE_VERSION, iter_partition, load_metadata, write_partition
from t1d_tkg.manifest import build_hashed_kfold_manifest, manifest_checksum, save_manifest


class EventInstanceCacheTests(unittest.TestCase):
    def test_canonicalization_collapses_repeats_and_preserves_value_quality(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.sorted"
            fields = SPECS["bolus"][1]
            normal = {"BolusType": "normal", "Normal": "2", "Extended": "100"}
            alternate = {"BolusType": "normal", "Normal": "3", "Extended": "100"}
            rows = [
                ["p", "4", "2026-01-01 12:00:00", *[normal.get(field, "") for field in fields]],
                ["p", "9", "2026-01-01 12:00:00", *[normal.get(field, "") for field in fields]],
                ["p", "10", "2026-01-01 12:00:00", *[alternate.get(field, "") for field in fields]],
            ]
            path.write_text("\n".join("|".join(row) for row in rows) + "\n")
            records = list(canonical_records(path, "bolus"))

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["exact_duplicate_count"], 1)
        self.assertEqual(records[0]["same_time_variant_count"], 2)
        self.assertEqual(records[1]["same_time_variant_count"], 2)
        self.assertEqual(records[0]["model_value"], 2.0)
        self.assertNotEqual(records[0]["model_value"], 100.0)

    def test_non_gram_food_is_retained_as_an_unknown_model_value(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.sorted"
            path.write_text("p|1|2026-01-01 12:00:00|30|exchanges\n")
            record = next(canonical_records(path, "food"))
        self.assertIsNone(record["model_value"])
        self.assertFalse(record["model_value_known"])
        self.assertEqual(record["source_fields"]["CarbsNet"], "30")

    def test_partition_round_trip_and_metadata_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            path = directory / "events-bolus-00.jsonl.gz"
            summary = write_partition(path, "bolus", [{
                "event_id": "private", "patient_id": "p", "occurrence_time": "2026-01-01T12:00:00+00:00",
                "modality": "bolus", "subtype": "normal", "model_value": 2.0, "model_value_unit": "U",
                "model_value_known": True, "source_fields": {}, "exact_duplicate_count": 0,
                "same_time_variant_count": 1,
            }])
            (directory / "metadata.json").write_text(json.dumps({
                "cache_version": EVENT_CACHE_VERSION, "manifest_sha256": "manifest", "files": [path.name],
            }))
            self.assertEqual(summary["canonical_events"], 1)
            self.assertEqual(next(iter_partition(path))["event_id"], "private")
            self.assertEqual(load_metadata(directory, manifest_sha256="manifest")["files"], [path.name])
            with self.assertRaises(ValueError):
                load_metadata(directory, manifest_sha256="other")

    def test_builder_writes_only_development_event_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            tables = work / "release" / "Data Tables"
            tables.mkdir(parents=True)
            patients = [str(number) for number in range(30)]
            manifest = build_hashed_kfold_manifest(patients, folds=3)
            save_manifest(work / "manifest.json", manifest)
            cgm_cache = work / "cgm-cache"
            cgm_cache.mkdir()
            (cgm_cache / "metadata.json").write_text(json.dumps({
                "manifest_sha256": manifest_checksum(manifest), "partitions": 3,
                "window_verification": {"window_identity_sha256": "frozen-window-identity"},
            }))
            values = {
                "Rate": "1", "Normal": "2", "Extended": "99", "CarbsNet": "30", "CarbUnits": "grams",
            }
            for modality, (pattern, fields) in SPECS.items():
                name = pattern.replace("*", "1")
                lines = ["|".join(["PtID", "RecID", "UTCDtTm", *fields])]
                for patient in patients:
                    lines.append("|".join([patient, patient, "2026-01-01 02:00:00", *[values.get(field, "") for field in fields]]))
                (tables / name).write_text("\n".join(lines) + "\n")
            # A synthetic export has one basal table, declared explicitly rather
            # than pretending to be the complete three-table Loop release.
            inventory = {modality: [pattern.replace("*", "1")] for modality, (pattern, _) in SPECS.items()}
            (work / "inventory.json").write_text(json.dumps(inventory))
            command = [
                sys.executable, str(ROOT / "scripts" / "build_loop_event_instance_cache.py"), str(work / "release"),
                "--model-manifest", str(work / "manifest.json"), "--cgm-cache-directory", str(cgm_cache),
                "--output-directory", str(work / "event-cache"), "--summary-output", str(work / "summary.json"),
                "--partitions", "3", "--minimum-free-before-gib", "0", "--minimum-free-during-gib", "0",
                "--source-inventory", str(work / "inventory.json"),
            ]
            result = subprocess.run(command, cwd=work, env={**os.environ, "PYTHONPATH": str(ROOT / "src")}, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            summary = json.loads((work / "summary.json").read_text())
            self.assertEqual(summary["canonical_events"], 90)
            self.assertEqual(summary["development_participants"], 30)
            self.assertEqual(len(list((work / "event-cache").glob("events-*.jsonl.gz"))), 9)
            self.assertFalse(any("event_id" in line for line in (work / "summary.json").read_text().splitlines()))


if __name__ == "__main__":
    unittest.main()
