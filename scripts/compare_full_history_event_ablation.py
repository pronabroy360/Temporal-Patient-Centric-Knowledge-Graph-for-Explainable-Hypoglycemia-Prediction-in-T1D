#!/usr/bin/env python3
"""Compare real events with the event-disabled full-history model.

Both runs use the same CGM encoder and prediction head. The disabled model
replaces the event state with zero; this isolates the effect of the captured
event input within that architecture, but its event encoder receives no
gradient and therefore has less effective training capacity.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from compare_controlled_neural_archives import _check_reported_metrics
from compare_full_history_neural_archives import CONTRACT_VERSION, paired_contract
from compare_loop_pilot_archives import compare, metadata


def compare_event_ablation(real_events: Path, disabled_events: Path,
                           *, draws: int = 2000, seed: int = 20261003) -> dict:
    real = metadata(real_events, "validation")
    disabled = metadata(disabled_events, "validation")
    if (real.get("contract_version") != CONTRACT_VERSION
            or disabled.get("contract_version") != CONTRACT_VERSION):
        raise ValueError("both archives must use the full-history neural contract")
    if (real.get("variant"), disabled.get("variant")) != (
            "history-event", "history-event-zero"):
        raise ValueError("expected real events followed by the event-disabled variant")
    for report in (real, disabled):
        if (report.get("mode") != "train" or report.get("fixture_only")
                or report.get("complete") is not True
                or report.get("prediction_identity_verified") is not True):
            raise ValueError("comparison requires completed, verified training archives")
    if paired_contract(real) != paired_contract(disabled):
        raise ValueError("event ablation differs in split, seed, input, code or windows")
    if real.get("trainable_parameters") != disabled.get("trainable_parameters"):
        raise ValueError("event ablation has different declared parameter counts")

    result = compare(real_events, disabled_events, group="validation",
                     draws=draws, seed=seed)
    _check_reported_metrics(real, result, "first", "validation")
    _check_reported_metrics(disabled, result, "second", "validation")
    result.update({
        "contract_version": CONTRACT_VERSION,
        "first_variant": "history-event",
        "second_variant": "history-event-zero",
        "declared_parameter_count_each": real["trainable_parameters"],
        "interpretation": (
            "Development validation only. The disabled branch receives no "
            "event information or event-encoder gradients, so equal declared "
            "parameter counts do not imply equal effective capacity. This "
            "ablation does not isolate graph relations."
        ),
    })
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("real_events", type=Path)
    parser.add_argument("disabled_events", type=Path)
    parser.add_argument("--draws", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20261003)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("paired comparison output already exists")
    result = compare_event_ablation(args.real_events, args.disabled_events,
                                    draws=args.draws, seed=args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
