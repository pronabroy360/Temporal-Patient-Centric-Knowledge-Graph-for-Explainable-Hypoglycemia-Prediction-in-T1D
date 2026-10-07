#!/usr/bin/env python3
"""Measure recorded basal/bolus/food overlap in frozen Loop windows."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from collections import Counter
from pathlib import Path

from audit_loop_window_event_alignment import (
    SPECS, aligned_event_counts, canonical_event_times, index_windows,
    partition_events, sorted_events,
)


MODALITIES = ("basal", "bolus", "food")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("release", type=Path)
    parser.add_argument("--window-index-directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--partitions", type=int, default=64)
    parser.add_argument("--lookback-minutes", type=int, default=120)
    parser.add_argument("--minimum-free-gib", type=float, default=15.0)
    args = parser.parse_args()
    if shutil.disk_usage(args.output.parent).free < args.minimum_free_gib * 1024**3:
        raise RuntimeError("insufficient free space before overlap audit")
    index_paths = sorted(args.window_index_directory.glob("*.jsonl.gz"))
    if len(index_paths) != args.partitions:
        raise ValueError("window-index partition count does not match --partitions")
    tables = args.release / "Data Tables"
    sources = {modality: sorted(tables.glob(SPECS[modality][0])) for modality in MODALITIES}
    if any(not paths for paths in sources.values()):
        raise ValueError("missing required Loop auxiliary table")
    totals: Counter[str] = Counter()
    with tempfile.TemporaryDirectory(prefix="loop-window-overlap-", dir=args.output.parent) as temporary:
        temporary_path = Path(temporary)
        partitions = {}
        for modality in MODALITIES:
            directory = temporary_path / modality
            directory.mkdir()
            partitions[modality] = partition_events(sources[modality], SPECS[modality][1], directory, args.partitions)
        for number in range(args.partitions):
            if shutil.disk_usage(args.output.parent).free < args.minimum_free_gib * 1024**3:
                raise RuntimeError("free-space safety floor reached during overlap audit")
            windows = index_windows(index_paths[number])
            event_times = {
                modality: canonical_event_times(sorted_events(partitions[modality][number], len(SPECS[modality][1])), len(SPECS[modality][1]))
                for modality in MODALITIES
            }
            for patient, times in windows.items():
                streams = [aligned_event_counts(times, event_times[modality].get(patient, []), lookback_minutes=args.lookback_minutes) for modality in MODALITIES]
                for records in zip(*streams):
                    present = tuple(int(record[1] > 0) for record in records)
                    totals["windows"] += 1
                    totals[f"basal_{present[0]}_bolus_{present[1]}_food_{present[2]}"] += 1
            print(f"overlap partition {number + 1}/{args.partitions}", flush=True)
    patterns = {key.removeprefix("basal_"): value for key, value in totals.items() if key.startswith("basal_")}
    report = {
        "audit_type": "canonical basal-bolus-food overlap in frozen eligible CGM windows",
        "release": str(args.release), "partitions": args.partitions,
        "lookback_minutes": args.lookback_minutes, "identifiers_emitted": False,
        "windows": totals["windows"], "presence_patterns": patterns,
        "all_three_present": totals["basal_1_bolus_1_food_1"],
        "none_present": totals["basal_0_bolus_0_food_0"],
        "temporary_partitions_removed": True,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
