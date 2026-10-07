#!/usr/bin/env python3
"""Stream the Loop public release for chronology and field-quality checks.

The audit uses source row order only to detect that sorting is needed. It does
not resolve duplicate timestamps, infer event availability, or create labels.
No participant identifiers are written to the report.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


ISO_SECOND = re.compile(rb"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")


def number(raw: bytes) -> float | None:
    raw = raw.strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def scan_group(paths: list[Path], *, values: list[str], categories: list[str]) -> dict[str, object]:
    participants: set[bytes] = set()
    rows = 0
    missing_patient = missing_utc = malformed_utc = 0
    backwards = adjacent_duplicates = 0
    last_utc: dict[bytes, bytes] = {}
    value_stats = {field: {"present": 0, "missing_or_nonnumeric": 0, "min": None, "max": None} for field in values}
    category_counts = {field: Counter() for field in categories}
    recid_first: list[int | None] = []
    recid_last: list[int | None] = []
    recid_non_increasing = 0

    for path in paths:
        first_rec = last_rec = previous_rec = None
        with path.open("rb") as handle:
            header = handle.readline().decode("utf-8-sig", "replace").rstrip("\r\n").split("|")
            index = {name: header.index(name) for name in ["PtID", "RecID", "UTCDtTm", *values, *categories]}
            for raw in handle:
                rows += 1
                parts = raw.rstrip(b"\r\n").split(b"|")
                patient = parts[index["PtID"]].strip()
                utc = parts[index["UTCDtTm"]].strip()
                if not patient:
                    missing_patient += 1
                else:
                    participants.add(patient)
                if not utc:
                    missing_utc += 1
                elif not ISO_SECOND.match(utc):
                    malformed_utc += 1
                elif patient:
                    previous = last_utc.get(patient)
                    if previous is not None:
                        if utc < previous:
                            backwards += 1
                        elif utc == previous:
                            adjacent_duplicates += 1
                    last_utc[patient] = utc
                try:
                    rec = int(parts[index["RecID"]])
                except ValueError:
                    rec = None
                if rec is not None:
                    first_rec = rec if first_rec is None else first_rec
                    if previous_rec is not None and rec <= previous_rec:
                        recid_non_increasing += 1
                    previous_rec = rec
                    last_rec = rec
                for field in values:
                    parsed = number(parts[index[field]])
                    stats = value_stats[field]
                    if parsed is None:
                        stats["missing_or_nonnumeric"] += 1
                    else:
                        stats["present"] += 1
                        stats["min"] = parsed if stats["min"] is None else min(stats["min"], parsed)
                        stats["max"] = parsed if stats["max"] is None else max(stats["max"], parsed)
                for field in categories:
                    category_counts[field][parts[index[field]].decode("utf-8", "replace").strip()] += 1
        recid_first.append(first_rec)
        recid_last.append(last_rec)
        print(f"scanned {path}: {rows} cumulative rows", flush=True)

    return {
        "files": [str(path) for path in paths],
        "rows": rows,
        "participants": len(participants),
        "missing_patient": missing_patient,
        "missing_utc_timestamp": missing_utc,
        "malformed_utc_timestamp": malformed_utc,
        "source_order_backward_timestamps": backwards,
        "source_order_adjacent_duplicate_timestamps": adjacent_duplicates,
        "recid_first_by_shard": recid_first,
        "recid_last_by_shard": recid_last,
        "recid_non_increasing_within_shards": recid_non_increasing,
        "value_fields": value_stats,
        "categories": {field: dict(counts.most_common()) for field, counts in category_counts.items()},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("release", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    tables = args.release / "Data Tables"
    report = {
        "release": str(args.release),
        "audit_type": "Loop chronology and field-quality intake",
        "identifiers_emitted": False,
        "modalities": {
            "cgm": scan_group(sorted(tables.glob("LOOPDeviceCGM*.txt")), values=["CGMVal"], categories=["RecordType", "Units"]),
            "basal": scan_group(sorted(tables.glob("LOOPDeviceBasal*.txt")), values=["Duration", "ExpectedDuration", "Percnt", "Rate", "SuprDuration", "SuprRate"], categories=["BasalType", "SuprBasalType"]),
            "bolus": scan_group([tables / "LOOPDeviceBolus.txt"], values=["Normal", "ExpectedNormal", "Extended", "ExpectedExtended", "Duration", "ExpectedDuration"], categories=["BolusType"]),
            "food": scan_group([tables / "LOOPDeviceFood.txt"], values=["CarbsNet"], categories=["CarbUnits"]),
            "exercise": scan_group([tables / "LOOPDeviceExercise.txt"], values=["DistanceValue", "DurationValue", "EnergyValue", "ReportedIntensity"], categories=["DistanceUnits", "DurationUnits", "EnergyUnits"]),
            "wizard": scan_group([tables / "LOOPDeviceWizard.txt"], values=["RecommendedCarb", "RecommendedCorrection", "RecommendedNet", "BgInput", "CarbInput", "InsulinOnBoard"], categories=[]),
        },
        "limitations": [
            "Backward and adjacent-duplicate counts use RecID source order and demonstrate the need to sort; they are not final duplicate counts.",
            "Exact duplicates across nonadjacent rows require a sorted or partitioned patient-level audit.",
            "Presence and numeric ranges do not establish clinical validity or prediction-time availability.",
            "The release readme states that participant treatment dates are shifted by a participant-specific random offset.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
