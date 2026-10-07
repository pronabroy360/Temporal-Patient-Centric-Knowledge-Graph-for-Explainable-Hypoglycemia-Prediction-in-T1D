# Loop CGM persistence/slope baseline

The first release-backed comparator is a non-learned CGM-only rule. At each
eligible prediction time, it takes the two most recent observed CGM readings,
extends their slope across the next 30 minutes, and alerts if the projected
trajectory goes below 70 mg/dL. It uses no auxiliary events, learned weights,
or locked-holdout data.

Run it on development participants only:

```bash
PYTHONPATH=src python3 scripts/audit_loop_partitioned_cgm.py \
  'data/Loop study public dataset 2023-01-31' \
  --development-manifest private/loop_development_manifest.json \
  --manifest-group development \
  --skip-tolerance-comparison \
  --logical-grid-tolerance 1 \
  --rule-baseline-output audit/loop_cgm_rule_development.json \
  --output audit/loop_cgm_rule_development_audit.json
```

The rule result includes participant-macro average precision, Brier score, and
aggregate confusion counts. It is a reference floor, not a calibrated model.
The locked 183-participant holdout must not be evaluated until model and alert
choices are frozen.
