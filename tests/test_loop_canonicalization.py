import unittest
from datetime import datetime, timezone

from t1d_tkg.loop import LoopRecord, canonicalize_records, exact_repeat_key


TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)


def record(modality, source_id, fields, *, timestamp=TIME):
    return LoopRecord(modality, "participant", timestamp, source_id, fields)


class LoopCanonicalizationTests(unittest.TestCase):
    def test_cgm_exact_repeats_use_lowest_source_id_and_keep_provenance(self):
        rows = [
            record("cgm", 9, {"RecordType": "CGM", "CGMVal": "6.1", "Units": "mmol/L"}),
            record("cgm", 4, {"RecordType": "CGM", "CGMVal": "6.1", "Units": "mmol/L"}),
        ]
        result = canonicalize_records(rows)
        self.assertEqual(result.exact_duplicates_removed, 1)
        self.assertEqual(result.records[0].record.source_record_id, 4)
        self.assertEqual(result.records[0].duplicate_source_record_ids, (9,))
        self.assertFalse(result.ambiguous_cgm_times)

    def test_conflicting_cgm_values_are_retained_and_marked_ambiguous(self):
        rows = [
            record("cgm", 1, {"RecordType": "CGM", "CGMVal": "4.0", "Units": "mmol/L"}),
            record("cgm", 2, {"RecordType": "CGM", "CGMVal": "4.3", "Units": "mmol/L"}),
        ]
        result = canonicalize_records(rows)
        self.assertEqual(len(result.records), 2)
        self.assertEqual(result.ambiguous_cgm_times, frozenset({("participant", TIME)}))

    def test_non_cgm_same_time_records_are_not_merged_by_time(self):
        rows = [
            record("bolus", 1, {"BolusType": "normal", "Normal": "1", "Extended": "", "ExpectedNormal": "1", "ExpectedExtended": "", "Duration": "0", "ExpectedDuration": "0"}),
            record("bolus", 2, {"BolusType": "normal", "Normal": "2", "Extended": "", "ExpectedNormal": "2", "ExpectedExtended": "", "Duration": "0", "ExpectedDuration": "0"}),
        ]
        result = canonicalize_records(rows)
        self.assertEqual(len(result.records), 2)
        self.assertFalse(result.ambiguous_cgm_times)

    def test_key_preserves_raw_values_and_units(self):
        grams = record("food", 1, {"CarbsNet": "15", "CarbUnits": "grams"})
        exchange = record("food", 2, {"CarbsNet": "15", "CarbUnits": "exchanges"})
        self.assertNotEqual(exact_repeat_key(grams), exact_repeat_key(exchange))

    def test_rejects_unsorted_or_mixed_modalities(self):
        later = record("food", 1, {"CarbsNet": "1", "CarbUnits": "grams"}, timestamp=datetime(2026, 1, 2, tzinfo=timezone.utc))
        earlier = record("food", 2, {"CarbsNet": "1", "CarbUnits": "grams"})
        with self.assertRaisesRegex(ValueError, "sorted"):
            canonicalize_records([later, earlier])
        with self.assertRaisesRegex(ValueError, "one Loop modality"):
            canonicalize_records([record("food", 1, {"CarbsNet": "1", "CarbUnits": "grams"}), record("exercise", 2, {"ExerciseName": "run", "DistanceValue": "", "DistanceUnits": "", "DurationValue": "", "DurationUnits": "", "EnergyValue": "", "EnergyUnits": "", "ReportedIntensity": ""})])


if __name__ == "__main__":
    unittest.main()
