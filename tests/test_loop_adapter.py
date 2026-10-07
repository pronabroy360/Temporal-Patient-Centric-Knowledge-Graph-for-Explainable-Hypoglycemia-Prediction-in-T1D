import unittest
import tempfile
from pathlib import Path

from t1d_tkg.loop_adapter import iter_loop_table, loop_event


BASE = {"PtID": "p", "RecID": "7", "ParentLOOPDeviceUploadsID": "u", "UTCDtTm": "2026-01-01 00:00:00"}


class LoopAdapterTests(unittest.TestCase):
    def test_cgm_preserves_raw_unit_and_requires_range_validation(self):
        event = loop_event({**BASE, "RecordType": "CGM", "CGMVal": "4.0", "Units": "mmol/L"}, modality="cgm")
        self.assertAlmostEqual(event.value, 72.0728)
        self.assertEqual(event.quality_status, "observed_pending_range_validation")

    def test_bolus_keeps_delivery_components(self):
        event = loop_event({**BASE, "BolusType": "dual", "Normal": "1", "Extended": "2", "Duration": "60000"}, modality="bolus")
        self.assertEqual(event.value, 3.0)
        self.assertEqual(event.attributes["extended_u"], 2.0)

    def test_streaming_reader_filters_participants_and_preserves_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "food.txt"
            path.write_text("PtID|RecID|ParentLOOPDeviceUploadsID|UTCDtTm|CarbsNet|CarbUnits\np|1|u|2026-01-01 00:00:00|20|grams\nq|2|v|2026-01-01 00:00:00|30|grams\n", encoding="utf-8")
            events = list(iter_loop_table(path, modality="food", patient_ids={"p"}))
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].source_record_id, "1")
        self.assertEqual(events[0].attributes["parent_upload_id"], "u")


if __name__ == "__main__":
    unittest.main()
