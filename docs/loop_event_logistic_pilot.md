# Loop recorded-event pilot

The corrected implementation and run sequence are specified in
[corrected pilot recovery](corrected_pilot_recovery.md). That document
supersedes the earlier ten-feature pilot description and run recommendation.

The current model uses fourteen features: two CGM features and twelve event
summaries/quality indicators. The contract is `(t−120 minutes,t]`, normal
bolus component only, explicit missingness, and unresolved simultaneous basal
states. It assumes immediate record availability in a retrospective replay.

First repeat CGM configuration selection with the corrected AP metric. Then
use that configuration for a validation-only event pilot. Corrected CGM
selection and five-fold development evaluation are now complete. The command
below reuses the protected CGM cache and only partitions/sorts basal, bolus,
and food source records:

```bash
PYTHONPATH=src python3 scripts/run_loop_event_logistic_pilot.py \
  'data/Loop study public dataset 2023-01-31' \
  --feature-cache-directory private/loop_cgm_feature_cache \
  --model-manifest private/loop_model_manifest.json \
  --fold outer-0 --epochs 2 --learning-rate 0.002 \
  --evaluation-scope validation \
  --output audit/loop_event_logistic_outer0_validation_v2.json
```

All models must pass frozen-window identity verification. This first run tests
the fixed CGM-selected optimizer as a transparent event-summary comparator.
Do not interpret an event-summary gain as evidence for graph relations.
