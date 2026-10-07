import unittest
from datetime import datetime, timedelta, timezone

from t1d_tkg.events import Event
from t1d_tkg.validation import validate_event_collection


class ValidationTests(unittest.TestCase):
    def test_collection_validation_reports_anomalies_without_dropping_events(self):
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        events = [
            Event("same", "p", "cgm", base + timedelta(minutes=5), 100, "mg/dL", availability_assumption="assumed_immediate"),
            Event("same", "p", "cgm", base, 101, "mg/dL", availability_assumption="assumed_immediate"),
            Event("unknown", "p", "new_source_block", base + timedelta(minutes=10), source_type="x"),
            Event("unknown-availability", "p", "meal", base + timedelta(minutes=15), source_type="x"),
        ]
        report = validate_event_collection(events)
        self.assertFalse(report["valid"])
        codes = {item["code"] for item in report["errors"] + report["warnings"]}
        self.assertIn("duplicate_event_id", codes)
        self.assertIn("unknown_event_type", codes)
        self.assertIn("unknown_availability", codes)
        self.assertEqual(report["events"], 4)


if __name__ == "__main__":
    unittest.main()
