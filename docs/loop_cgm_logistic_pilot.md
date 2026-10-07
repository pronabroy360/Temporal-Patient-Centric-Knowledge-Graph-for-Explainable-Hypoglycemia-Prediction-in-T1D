# Loop CGM logistic development pilot

This pilot trains a memory-bounded logistic model on two CGM-only features:
current glucose and the elapsed-time-adjusted slope from the prior observed
reading. It uses one protected development fold at a time.

The default run reports validation only. The internal development-test group is
not evaluated while choosing epochs or learning rate, and the locked holdout is
never read by this script.

The report now includes the persistence/slope rule on the exact same validation
windows. Use that within-run comparison; do not compare a logistic validation
result with the earlier all-development rule result.

```bash
PYTHONPATH=src python3 scripts/run_loop_cgm_logistic_pilot.py \
  'data/Loop study public dataset 2023-01-31' \
  --model-manifest private/loop_model_manifest.json \
  --fold outer-0 \
  --epochs 1 \
  --learning-rate 0.002 \
  --output audit/loop_cgm_logistic_outer0_validation.json
```

The operation partitions and sorts the full CGM release, then makes one pass
for standardization and one pass per epoch. It requires at least 20 GiB free
space before starting and stops at a 10 GiB safety floor. Treat the first
one-epoch run as a pipeline and optimization-stability check, not a final
model result.
