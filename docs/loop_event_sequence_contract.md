# Loop individual-event sequence contract

The next non-graph comparator consumes the protected canonical event-instance
cache rather than compressed event totals. Its first implementation is a
position-aware linear sequence control; a recurrent encoder will be evaluated
only after this control establishes whether retained event resolution has any
incremental signal.

For every frozen CGM window it uses only `(t-120 minutes, t]` events, sorts by
UTC occurrence time, keeps the most recent `max_events` records, and records
both the active-event count and number dropped by truncation. Each retained
position has an explicit valid-position flag, basal/bolus/food modality,
stable hashed subtype channel, normalized age, numeric value, value-known
mask, same-time-variant count and exact-reexport provenance. Missing values
are encoded as value zero **with** a value-known mask of zero; they do not mean
clinical zero dose or carbohydrate.

This is still retrospective occurrence-time replay. Loop does not provide a
validated real-world availability timestamp. The comparator will use the same
cached CGM windows, 652 development participants, model manifest and frozen
window identity as the completed residual diagnostic. It will select on
outer-0 validation only; development-test and locked holdout remain closed.

A GRU may become the frozen B4 comparator only after the position-aware
control, a fixed maximum-event rule, truncation audit, parameter budget and
three fixed seeds are declared. Any graph test must use the same event
instances and truncation rule.

## First runnable control

The first cache-backed run fixes `max_events=16`, L2 `0.01` and two epochs to
match the strongest regularization/epoch setting from the completed residual
diagnostic. It is a development-only representation check, not final B4
selection:

```bash
PYTHONPATH=src python3 scripts/run_loop_event_sequence_linear_pilot.py \
  --feature-cache-directory private/loop_cgm_feature_cache \
  --event-cache-directory private/loop_event_instance_cache \
  --model-manifest private/loop_model_manifest.json \
  --cgm-baseline-artifacts private/pilot_runs/loop_cgm_logistic_outer0_development_test_v2 \
  --fold outer-0 \
  --max-events 16 \
  --l2 0.01 \
  --epochs 2 \
  --learning-rate 0.002 \
  --output audit/loop_event_sequence_linear_outer0_max16_validation.json
```

The report must reproduce the frozen-CGM validation metrics exactly and report
the fraction of truncated windows before any architecture or maximum-event
change is considered. It will not score development-test or locked-holdout
participants.
