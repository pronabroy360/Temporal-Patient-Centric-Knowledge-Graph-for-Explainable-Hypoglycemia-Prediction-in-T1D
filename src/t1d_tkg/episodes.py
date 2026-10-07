"""Confirmed CGM episode and alert matching utilities."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable

from .events import Event


def confirmed_episode_onsets(
    cgm_events: Iterable[Event],
    *,
    threshold: float = 70.0,
    step_minutes: int = 5,
    min_consecutive: int = 3,
) -> list[datetime]:
    """Return onset times for runs of consecutive low CGM readings.

    Missing/invalid readings break a run.  The onset is emitted once per run,
    even if the low lasts for many samples.
    """

    ordered = sorted((event for event in cgm_events if event.event_type == "cgm" and event.quality_status in {"observed_valid", "derived_valid"} and event.value is not None), key=lambda event: event.event_time)
    runs: list[list[Event]] = []
    current: list[Event] = []
    step = timedelta(minutes=step_minutes)
    for event in ordered:
        is_low = event.value < threshold
        consecutive = bool(current) and event.event_time - current[-1].event_time == step
        if is_low and (not current or consecutive and current[-1].value < threshold):
            current.append(event)
        else:
            if len(current) >= min_consecutive:
                runs.append(current)
            current = [event] if is_low else []
    if len(current) >= min_consecutive:
        runs.append(current)
    return [run[0].event_time for run in runs]


def suppress_alerts(alert_times: Iterable[datetime], *, refractory_minutes: int = 30) -> list[datetime]:
    """Apply chronological refractory suppression to alert timestamps."""

    ordered = sorted(alert_times)
    if not ordered:
        return []
    accepted = [ordered[0]]
    refractory = timedelta(minutes=refractory_minutes)
    for alert in ordered[1:]:
        if alert - accepted[-1] >= refractory:
            accepted.append(alert)
    return accepted


def simulate_alerts(
    index_times: Iterable[datetime],
    scores: Iterable[float],
    *,
    threshold: float,
    refractory_minutes: int = 30,
) -> list[datetime]:
    """Issue thresholded alerts with chronological refractory suppression."""

    pairs = list(zip(index_times, scores))
    if not pairs:
        return []
    if any(time.tzinfo is None or time.utcoffset() is None for time, _ in pairs):
        raise ValueError("alert index times must be timezone-aware")
    if refractory_minutes < 0:
        raise ValueError("refractory_minutes cannot be negative")
    ordered = sorted(pairs, key=lambda pair: pair[0])
    return suppress_alerts(
        (time for time, score in ordered if float(score) >= threshold),
        refractory_minutes=refractory_minutes,
    )


def select_alert_threshold(
    validation_predictions: dict[str, tuple[Iterable[datetime], Iterable[float]]],
    episodes_by_patient: dict[str, Iterable[datetime]],
    eligible_minutes_by_patient: dict[str, float],
    candidate_thresholds: Iterable[float],
    *,
    horizon_minutes: int,
    refractory_minutes: int = 30,
    max_unmatched_alerts_per_day: float = 1.0,
) -> dict[str, object]:
    """Choose a validation threshold under the prespecified alert budget.

    The returned candidate table is intended for archival reporting. A
    threshold is selected only when its unmatched-alert burden is within the
    supplied budget; ties maximize matched episodes, then minimize burden, then
    choose the higher threshold deterministically.
    """

    if horizon_minutes <= 0 or max_unmatched_alerts_per_day < 0:
        raise ValueError("horizon_minutes must be positive and alert budget non-negative")
    patients = sorted(set(validation_predictions) | set(episodes_by_patient) | set(eligible_minutes_by_patient))
    if not patients or any(patient not in validation_predictions or patient not in episodes_by_patient for patient in patients):
        raise ValueError("validation predictions and episodes must cover the same patients")
    evaluable_days = sum(float(eligible_minutes_by_patient.get(patient, 0.0)) for patient in patients) / (24.0 * 60.0)
    if evaluable_days <= 0:
        raise ValueError("eligible monitoring time must be positive")
    episodes = {patient: sorted(episodes_by_patient[patient]) for patient in patients}
    candidates: list[dict[str, object]] = []
    for threshold in sorted({float(value) for value in candidate_thresholds}):
        matched = 0
        total_episodes = sum(len(episodes[patient]) for patient in patients)
        unmatched_alerts = 0
        alert_count = 0
        for patient in patients:
            times, scores = validation_predictions[patient]
            alerts = simulate_alerts(times, scores, threshold=threshold, refractory_minutes=refractory_minutes)
            result = match_alerts_to_episodes(alerts, episodes[patient], horizon_minutes=horizon_minutes)
            matched += int(result["matched"])
            unmatched_alerts += int(result["unmatched_alerts"])
            alert_count += len(alerts)
        burden = unmatched_alerts / evaluable_days
        candidates.append(
            {
                "threshold": threshold,
                "alerts": alert_count,
                "matched_episodes": matched,
                "total_episodes": total_episodes,
                "episode_sensitivity": None if total_episodes == 0 else matched / total_episodes,
                "unmatched_alerts": unmatched_alerts,
                "unmatched_alerts_per_evaluable_day": burden,
                "feasible": burden <= max_unmatched_alerts_per_day,
            }
        )
    feasible = [item for item in candidates if item["feasible"]]
    selected = None
    if feasible:
        selected = max(feasible, key=lambda item: (int(item["matched_episodes"]), -float(item["unmatched_alerts_per_evaluable_day"]), float(item["threshold"])))
    return {
        "selected": selected,
        "candidates": candidates,
        "evaluable_days": evaluable_days,
        "horizon_minutes": horizon_minutes,
        "refractory_minutes": refractory_minutes,
        "max_unmatched_alerts_per_day": max_unmatched_alerts_per_day,
    }


def match_alerts_to_episodes(
    alert_times: Iterable[datetime],
    onset_times: Iterable[datetime],
    *,
    horizon_minutes: int,
) -> dict[str, object]:
    """One-to-one chronological alert matching for event-level reporting."""

    alerts = sorted(alert_times)
    onsets = sorted(onset_times)
    horizon = timedelta(minutes=horizon_minutes)
    matched: list[tuple[datetime, datetime]] = []
    used: set[int] = set()
    for alert in alerts:
        candidate = next((index for index, onset in enumerate(onsets) if index not in used and timedelta(0) < onset - alert <= horizon), None)
        if candidate is not None:
            used.add(candidate)
            matched.append((alert, onsets[candidate]))
    leads = [(onset - alert).total_seconds() / 60 for alert, onset in matched]
    return {
        "alerts": len(alerts),
        "episodes": len(onsets),
        "matched": len(matched),
        "missed_episodes": len(onsets) - len(matched),
        "unmatched_alerts": len(alerts) - len(matched),
        "lead_times_minutes": leads,
        "matches": matched,
    }
