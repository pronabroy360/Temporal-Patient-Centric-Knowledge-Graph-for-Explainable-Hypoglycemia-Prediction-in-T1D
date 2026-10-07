#!/usr/bin/env python3
"""Validate aggregate invariants from the completed Loop canonical audits."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("audit_directory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    checks: dict[str, bool] = {}
    details: dict[str, object] = {}
    for modality in ("basal", "bolus", "food", "exercise"):
        report = load(args.audit_directory / f"loop_{modality}_canonical_audit.json")
        counts = report["counts"]
        checks[f"{modality}_row_reconciliation"] = counts["raw_rows"] == counts["canonical_rows"] + counts["exact_duplicates_removed"]
        checks[f"{modality}_temporary_cleanup"] = report["temporary_partitions_removed"] is True
        details[modality] = counts
    cgm = load(args.audit_directory / "loop_cgm_canonical_audit.json")
    cgm_counts = cgm["counts"]
    checks["cgm_row_reconciliation"] = cgm_counts["raw_rows"] == cgm_counts["canonical_rows"] + cgm_counts["exact_duplicates_removed"]
    checks["cgm_has_one_or_more_conflicting_records_per_ambiguous_timestamp"] = (
        cgm_counts["canonical_rows"] - cgm_counts["calibration_canonical_rows"] - cgm_counts["usable_canonical_cgm_timestamps"]
        >= cgm_counts["ambiguous_cgm_timestamps"]
    )
    checks["cgm_temporary_cleanup"] = cgm["temporary_partitions_removed"] is True
    details["cgm"] = cgm_counts
    report = {"audit_type": "Loop canonical-audit aggregate validation", "passed": all(checks.values()), "checks": checks, "counts": details}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
