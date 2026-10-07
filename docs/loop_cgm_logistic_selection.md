# CGM logistic configuration selection

**Suspended on 15 September 2026:** the historical AP implementation was
incorrect for tied scores. Repeat selection using the corrected metric as
described in [corrected pilot recovery](corrected_pilot_recovery.md).
The frozen selection below is retained only as historical provenance.

The outer-0 validation pilot establishes the feature set: current glucose and
recent slope. The remaining configuration choice is deliberately small to
avoid consuming the development validation set with an unrestricted search.

Compare these two candidates on the same outer-0 validation group:

| Candidate | Epochs | Learning rate |
|---|---:|---:|
| A | 1 | 0.002 |
| B | 2 | 0.002 |

Candidate A has already produced macro AP 0.4570 and Brier 0.0230. Select the
candidate with higher participant-macro AP; use lower Brier only to break an
AP tie. Do not run `--evaluate-development-test` during selection. The chosen
configuration will then be evaluated once across the five development test
folds before any locked-holdout evaluation.

## Frozen selection

Candidate B was selected on outer-0 validation: macro AP 0.45750 and Brier
0.02288, versus candidate A's 0.45703 and 0.02296. The improvement is small,
but B wins under the prespecified rule. The CGM logistic configuration is now
frozen at two epochs and learning rate 0.002.

Run candidate B:

```bash
PYTHONPATH=src python3 scripts/run_loop_cgm_logistic_pilot.py \
  'data/Loop study public dataset 2023-01-31' \
  --model-manifest private/loop_model_manifest.json \
  --fold outer-0 \
  --epochs 2 \
  --learning-rate 0.002 \
  --output audit/loop_cgm_logistic_outer0_epochs2_validation.json
```
