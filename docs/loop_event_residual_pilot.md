# Loop frozen-CGM event residual diagnostic

The first recorded-event summary model was weaker than the matched CGM model.
This diagnostic asks the narrower next question: do the same captured events
add signal when the selected CGM predictor is held fixed?

The runner loads the completed CGM archive for the requested outer fold and
fits only this additive branch:

```text
logit(p) = logit(p_frozen_CGM) + event_residual(event_features)
```

The CGM weights, normalization and intercept are never updated. Before fitting,
an all-zero residual gives exactly the frozen CGM probability. The runner
requires a matching completed baseline archive, model-manifest checksum, CGM
window identity and event-cache partition count. It evaluates **outer-0
validation only**; it cannot score the internal development-test or the locked
holdout.

## Prespecified variants and tuning grid

`presence-quality` uses event counts, recency, missing-value counts and basal
ambiguity without insulin or carbohydrate magnitudes. `value-timing` adds the
permitted reported basal rate, normal bolus amount and gram carbohydrate value.
Unknown values remain unknown-event indicators and do not become zero doses.

Run the two variants across L2 values `0.0001`, `0.001`, `0.01` and epochs `1`,
`2`: 12 development candidates total. Select one only from outer-0 validation
by participant-macro AP, then Brier score, then the simpler variant. Archive
every result, including a negative result. Do not run development-test results
until selection is frozen.

## Commands

The existing completed outer-0 CGM archive is a valid frozen base predictor.
Run this loop from the repository root; it reads only the protected caches and
does not repartition or reread the raw Loop tables:

```bash
for variant in presence-quality value-timing; do
  for l2 in 0.0001 0.001 0.01; do
    for epochs in 1 2; do
      PYTHONPATH=src python3 scripts/run_loop_event_residual_pilot.py \
        --feature-cache-directory private/loop_cgm_feature_cache \
        --event-cache-directory private/loop_event_instance_cache \
        --model-manifest private/loop_model_manifest.json \
        --cgm-baseline-artifacts private/pilot_runs/loop_cgm_logistic_outer0_development_test_v2 \
        --fold outer-0 \
        --variant "$variant" \
        --l2 "$l2" \
        --epochs "$epochs" \
        --learning-rate 0.002 \
        --output "audit/loop_event_residual_outer0_${variant}_l2${l2}_epochs${epochs}.json" || break 3
    done
  done
done
```

Each report archives aligned validation predictions with both residual and
frozen-CGM scores. The residual must be compared using the paired archive tool
before interpreting a difference. These are optimistic occurrence-time replay
results: Loop does not provide a validated observed event-availability clock.

After all twelve commands complete, validate the grid and select the one
prespecified development candidate without reading development-test data:

```bash
PYTHONPATH=src python3 scripts/summarize_loop_event_residual_candidates.py \
  --directory audit \
  --output audit/loop_event_residual_outer0_selection.json
```

The summarizer rejects missing, duplicate, legacy-metric or non-comparable
reports. It ranks higher participant-macro AP first, lower Brier second, then
the presence/quality variant, lower L2 and fewer epochs as deterministic
tie-breakers.
