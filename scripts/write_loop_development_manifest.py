#!/usr/bin/env python3
"""Create a protected development/holdout split for the Loop candidate pool."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def participant_ids(paths: list[Path], *, required_field: str | None = None) -> set[str]:
    result: set[str] = set()
    for path in paths:
        with path.open("rb") as handle:
            header = handle.readline().decode("utf-8-sig", "replace").rstrip("\r\n").split("|")
            patient_index = header.index("PtID")
            field_index = header.index(required_field) if required_field else None
            for line in handle:
                parts = line.rstrip(b"\r\n").split(b"|")
                if field_index is not None and not parts[field_index].strip():
                    continue
                patient = parts[patient_index].strip().decode("ascii", "replace")
                if patient:
                    result.add(patient)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("release", type=Path)
    parser.add_argument("--private-output", type=Path, default=Path("private/loop_development_manifest.json"))
    parser.add_argument("--summary-output", type=Path, required=True)
    args = parser.parse_args()
    tables = args.release / "Data Tables"
    candidates = set.intersection(
        participant_ids(sorted(tables.glob("LOOPDeviceCGM*.txt"))),
        participant_ids(sorted(tables.glob("LOOPDeviceBasal*.txt"))),
        participant_ids([tables / "LOOPDeviceBolus.txt"]),
        participant_ids([tables / "LOOPDeviceFood.txt"], required_field="CarbsNet"),
    )
    development = sorted(patient for patient in candidates if int(hashlib.sha256(f"loop-tolerance-v1:{patient}".encode()).hexdigest(), 16) % 10 < 8)
    holdout = sorted(candidates - set(development))
    manifest = {"version": "loop-tolerance-v1", "purpose": "select grid tolerance only", "development_patients": development, "holdout_patients": holdout}
    payload = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    args.private_output.parent.mkdir(parents=True, exist_ok=True)
    args.private_output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = {"version": manifest["version"], "candidate_patients": len(candidates), "development_patients": len(development), "holdout_patients": len(holdout), "manifest_sha256": hashlib.sha256(payload).hexdigest(), "identifiers_emitted": False}
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
