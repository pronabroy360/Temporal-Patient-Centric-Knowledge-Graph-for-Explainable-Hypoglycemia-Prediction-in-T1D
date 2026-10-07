import unittest
from datetime import datetime, timedelta, timezone

from t1d_tkg.audit import audit_patient
from t1d_tkg.events import Event


class AuditTests(unittest.TestCase):
    def test_audit_reports_coverage_gaps_duplicates_and_arrival_metadata(self):
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        events = [
            Event("cgm-0", "p", "cgm", base, 120, "mg/dL", availability_assumption="assumed_immediate", source_type="cgm"),
            Event("cgm-1", "p", "cgm", base + timedelta(minutes=5), 120, "mg/dL", availability_assumption="assumed_immediate", source_type="cgm"),
            Event("cgm-dup", "p", "cgm", base + timedelta(minutes=5), 119, "mg/dL", availability_assumption="assumed_immediate", source_type="cgm"),
            Event("cgm-2", "p", "cgm", base + timedelta(minutes=40), 60, "mg/dL", availability_assumption="assumed_immediate", source_type="cgm"),
            Event("meal", "p", "meal", base + timedelta(minutes=4), 20, "g", available_time=base + timedelta(minutes=6), source_type="self_report"),
        ]
        result = audit_patient(events, "p")
        self.assertEqual(result["duplicate_cgm_timestamp_groups"], 1)
        self.assertEqual(result["duplicate_cgm_records"], 1)
        self.assertEqual(result["longest_cgm_gap_minutes"], 35.0)
        self.assertEqual(result["availability_time_metadata"]["assumed_immediate"], 4)
        self.assertEqual(result["availability_time_metadata"]["known_arrival_time"], 1)
        self.assertTrue(result["window_build_status"].startswith("blocked:"))


if __name__ == "__main__":
    unittest.main()
