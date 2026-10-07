#!/usr/bin/env python3
"""Count Loop CGM values retained by each explicit range policy."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from t1d_tkg.range_policy import RANGE_POLICIES

def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("release", type=Path); parser.add_argument("--output", type=Path, required=True); args = parser.parse_args()
    counts = {name: 0 for name in RANGE_POLICIES}; numeric = raw = 0
    for path in sorted((args.release / "Data Tables").glob("LOOPDeviceCGM*.txt")):
        with path.open("rb") as handle:
            header = handle.readline().decode("utf-8-sig", "replace").rstrip("\r\n").split("|")
            value_i, type_i, unit_i = (header.index(name) for name in ("CGMVal", "RecordType", "Units"))
            for line in handle:
                raw += 1; parts = line.rstrip(b"\r\n").split(b"|")
                if len(parts) <= max(value_i, type_i, unit_i) or parts[type_i] != b"CGM" or parts[unit_i] != b"mmol/L": continue
                try: value = float(parts[value_i]) * 18.0182
                except (ValueError, TypeError): continue
                numeric += 1
                for name, policy in RANGE_POLICIES.items(): counts[name] += int(policy.accepts(value))
    summary = {"audit_type": "Loop CGM range-policy sensitivity", "raw_rows": raw, "numeric_cgm_rows": numeric, "retained_by_policy": counts, "identifiers_emitted": False}
    args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"); print(json.dumps(summary, indent=2, sort_keys=True))
if __name__ == "__main__": main()
