import tempfile
import unittest
from datetime import timezone
from pathlib import Path

from t1d_tkg.ohio import parse_ohio_xml


XML = """<patient id="559" weight="99" insulin_type="Novalog">
  <glucose_level>
    <event ts="01-01-2026 00:00:00" value="120" />
    <event ts="01-01-2026 00:05:00" value="119" />
  </glucose_level>
  <basal>
    <event ts="31-12-2025 23:55:00" value="0.6" />
    <event ts="01-01-2026 00:05:00" value="0.7" />
  </basal>
  <temp_basal><event ts_begin="01-01-2026 00:00:00" ts_end="01-01-2026 00:10:00" value="0" /></temp_basal>
  <bolus><event ts_begin="01-01-2026 00:00:00" ts_end="01-01-2026 00:00:00" dose="2.0" type="normal" /></bolus>
  <meal><event ts="01-01-2026 00:00:00" type="Breakfast" carbs="30" /></meal>
  <exercise><event ts="01-01-2026 00:05:00" duration="20" intensity="4" /></exercise>
  <basis_heart_rate><event ts="01-01-2026 00:00:00" value="70" /></basis_heart_rate>
  <hypo_event><event ts="01-01-2026 00:10:00" /></hypo_event>
</patient>"""


class OhioAdapterTests(unittest.TestCase):
    def test_documented_blocks_are_canonical_events(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "559-ws-training.xml"
            path.write_text(XML, encoding="utf-8")
            result = parse_ohio_xml(path, timezone=timezone.utc, source_split="training")
        self.assertEqual(result.patient_id, "559")
        self.assertEqual(result.metadata["weight"], "99")
        by_type = {}
        for event in result.events:
            by_type.setdefault(event.event_type, []).append(event)
        self.assertEqual(len(by_type["cgm"]), 2)
        self.assertEqual(by_type["meal"][0].value, 30.0)
        self.assertEqual(by_type["insulin"][0].unit, "U")
        self.assertEqual(by_type["exercise"][0].event_type, "exercise")
        self.assertEqual(by_type["exercise"][0].attributes["duration_minutes"], 20.0)
        self.assertEqual(by_type["cgm"][0].attributes["source_split"], "training")
        basal = [event for event in result.events if event.event_type == "basal"]
        self.assertEqual(len(basal), 2)
        self.assertIsNotNone(basal[0].end_time)
        self.assertEqual(basal[0].unit, "U/h")
        self.assertEqual(by_type["context"][-1].event_type, "context")

    def test_timezone_is_required_by_caller(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "559.xml"
            path.write_text(XML, encoding="utf-8")
            with self.assertRaises(TypeError):
                parse_ohio_xml(path)


if __name__ == "__main__":
    unittest.main()
