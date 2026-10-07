#!/usr/bin/env python3
"""Stream Jaeb public tables to measure participant-level modality overlap.

This is an intake audit. It counts records and pseudonymous participants but
does not emit identifiers, construct labels, resolve duplicates, or infer
event availability. Large Loop tables are read line by line.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from statistics import median


def encoding_for(path: Path) -> str:
    sample = path.open("rb").read(4096)
    return "utf-16" if sample.count(b"\x00") > 100 else "utf-8-sig"


def summarize(counter: Counter[str]) -> dict[str, float | int | None]:
    values = list(counter.values())
    return {
        "min": min(values) if values else None,
        "median": median(values) if values else None,
        "max": max(values) if values else None,
    }


def scan(path: Path, *, nonempty_field: str | None = None) -> tuple[dict[str, object], set[str], Counter[str]]:
    encoding = encoding_for(path)
    counts: Counter[str] = Counter()
    selected_rows = 0
    total_rows = 0
    if encoding == "utf-16":
        with path.open(encoding=encoding, errors="replace") as handle:
            header = handle.readline().rstrip("\r\n").split("|")
            patient_index = header.index("PtID")
            filter_index = header.index(nonempty_field) if nonempty_field else None
            for line in handle:
                total_rows += 1
                parts = line.rstrip("\r\n").split("|")
                if filter_index is not None and (filter_index >= len(parts) or not parts[filter_index].strip()):
                    continue
                if patient_index < len(parts) and parts[patient_index].strip():
                    counts[parts[patient_index].strip()] += 1
                    selected_rows += 1
    else:
        with path.open("rb") as handle:
            header = handle.readline().decode("utf-8-sig", "replace").rstrip("\r\n").split("|")
            patient_index = header.index("PtID")
            filter_index = header.index(nonempty_field) if nonempty_field else None
            for raw in handle:
                total_rows += 1
                if filter_index is None and patient_index == 0:
                    stop = raw.find(b"|")
                    patient = raw[:stop if stop >= 0 else None].strip().decode("ascii", "replace")
                else:
                    parts = raw.rstrip(b"\r\n").split(b"|")
                    if filter_index is not None and (filter_index >= len(parts) or not parts[filter_index].strip()):
                        continue
                    patient = parts[patient_index].strip().decode("ascii", "replace") if patient_index < len(parts) else ""
                if patient:
                    counts[patient] += 1
                    selected_rows += 1
    result = {
        "files": [str(path)],
        "rows": total_rows,
        "selected_rows": selected_rows,
        "participants": len(counts),
        "rows_per_participant": summarize(counts),
        "selection": f"{nonempty_field} nonempty" if nonempty_field else "all rows",
    }
    return result, set(counts), counts


def scan_group(paths: list[Path], *, nonempty_field: str | None = None) -> tuple[dict[str, object], set[str]]:
    combined: Counter[str] = Counter()
    rows = selected = 0
    files = []
    for path in paths:
        report, _, counts = scan(path, nonempty_field=nonempty_field)
        combined.update(counts)
        rows += int(report["rows"])
        selected += int(report["selected_rows"])
        files.extend(report["files"])
        print(f"scanned {path}: {report['rows']} rows, {report['participants']} participants", flush=True)
    return ({
        "files": files,
        "rows": rows,
        "selected_rows": selected,
        "participants": len(combined),
        "rows_per_participant": summarize(combined),
        "selection": f"{nonempty_field} nonempty" if nonempty_field else "all rows",
    }, set(combined))


def dataset_report(name: str, roster: Path, groups: dict[str, tuple[list[Path], str | None]]) -> dict[str, object]:
    roster_report, roster_ids, _ = scan(roster)
    modalities: dict[str, object] = {}
    participant_sets: dict[str, set[str]] = {}
    for modality, (paths, nonempty) in groups.items():
        report, ids = scan_group(paths, nonempty_field=nonempty)
        modalities[modality] = report
        participant_sets[modality] = ids
    overlaps = {}
    core = [key for key in ("cgm", "basal", "bolus", "carbohydrate") if key in participant_sets]
    if core:
        intersection = set.intersection(*(participant_sets[key] for key in core))
        overlaps["cgm_basal_bolus_carbohydrate"] = len(intersection) if len(core) == 4 else None
    if "cgm" in participant_sets:
        overlaps["cgm_in_roster"] = len(participant_sets["cgm"] & roster_ids)
    for modality, ids in participant_sets.items():
        overlaps[f"cgm_and_{modality}"] = len(participant_sets.get("cgm", set()) & ids)
    return {"dataset": name, "roster": roster_report, "modalities": modalities, "participant_overlaps": overlaps}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("data_root", type=Path, nargs="?", default=Path("data"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.data_root
    loop = root / "Loop study public dataset 2023-01-31" / "Data Tables"
    d3 = root / "DCLP3 Public Dataset - Release 3 - 2022-08-04" / "Data Files"
    d5 = root / "DCLP5_Dataset_2022-01-20-5e0f3b16-c890-4ace-9e3b-531f3687cf53"
    flair = root / "FLAIRPublicDataSet" / "Data Tables"
    reports = [
        dataset_report("Loop", loop / "PtRoster.txt", {
            "cgm": (sorted(loop.glob("LOOPDeviceCGM*.txt")), None),
            "basal": (sorted(loop.glob("LOOPDeviceBasal*.txt")), None),
            "bolus": ([loop / "LOOPDeviceBolus.txt"], None),
            "carbohydrate": ([loop / "LOOPDeviceFood.txt"], "CarbsNet"),
            "exercise": ([loop / "LOOPDeviceExercise.txt"], None),
            "wizard": ([loop / "LOOPDeviceWizard.txt"], None),
        }),
        dataset_report("DCLP3", d3 / "PtRoster_a.txt", {
            "cgm": ([d3 / "cgm.txt"], None),
            "basal": ([d3 / "Pump_BasalRateChange.txt"], None),
            "bolus": ([d3 / "Pump_BolusDelivered.txt"], None),
            "carbohydrate": ([d3 / "RocheMeter_a.txt"], "Carbs"),
        }),
        dataset_report("DCLP5", d5 / "PtRoster.txt", {
            "cgm": ([d5 / "DCLP5TandemCGMDATAGXB_b.txt"], None),
            "basal": ([d5 / "DCLP5TandemBASALRATECHG_b.txt"], None),
            "bolus": ([d5 / "DCLP5TandemBolus_Completed_Combined_b.txt"], None),
            "carbohydrate": ([d5 / "RocheMeter.txt"], "Carbs"),
        }),
        dataset_report("FLAIR", flair / "PtRoster.txt", {
            "cgm": ([flair / "FLAIRDeviceCGM.txt"], None),
            "daily_insulin_summary": ([flair / "FLAIRInsulinDelivery.txt"], None),
        }),
    ]
    payload = {
        "audit_type": "participant modality coverage intake",
        "identifiers_emitted": False,
        "limitations": [
            "Counts do not establish timestamp alignment, record validity, capture completeness, or prediction-time availability.",
            "Carbohydrate coverage counts only rows whose carbohydrate field is nonempty.",
            "Loop shards are combined by participant ID; cross-shard duplicate records are not resolved here.",
        ],
        "datasets": reports,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
