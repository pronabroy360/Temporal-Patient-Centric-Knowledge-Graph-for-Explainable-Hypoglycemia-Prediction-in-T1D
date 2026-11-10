# Controlled epoch-1 checkpoint replay

The saved epoch-1 checkpoints were evaluated on the original outer-0
development-validation cohort. This was checkpoint evaluation only: no model
was retrained, the participant split and prediction windows were unchanged,
and the locked holdout was not accessed.

## Integrity and cohort checks

The Kaggle output bundle contains both complete evaluation runs and their
participant prediction files. The local ZIP is 243,869,545 bytes, its SHA-256
matches Kaggle's printed checksum
`c6fdef48c6bcaf7e7ad46cf849f57565081142bbb5fba5f8364515490ec0dcc7`, and
`unzip -t` reports no archive errors. The local paired-analysis script
recomputed metrics from the saved predictions, confirmed that both epoch-1
results match their reported metrics, and verified the exact shared validation
window identity. Both models cover 130 participants and 8,885,621 windows,
including 274,044 positive labels. Each result reports prediction identity
verification as true. The manifest, data-content digest, source fingerprint,
training membership, fold, seed, and metric version match the original
epoch-2 campaign.

| Checkpoint | Participant-macro AP (higher is better) | Participant-macro Brier (lower is better) | Pooled Brier (lower is better) |
|---|---:|---:|---:|
| CGM-only MLP, epoch 1 | 0.47934 | 0.021240 | 0.020883 |
| CGM-only MLP, epoch 2 | 0.48160 | 0.021118 | 0.020756 |
| Clean event GRU, epoch 1 | 0.44937 | 0.022337 | 0.022006 |
| Clean event GRU, epoch 2 | 0.46933 | 0.021578 | 0.021224 |

## Paired epoch comparisons

The script `scripts/summarize_controlled_epoch1_replay.py` compared fixed
participant predictions with 2,000 paired participant-bootstrap draws. For
each metric below, the difference is **epoch 1 minus epoch 2**.

| Model and metric | Difference | Paired 95% interval | Participants favoring epoch 2 |
|---|---:|---:|---:|
| CGM MLP participant-macro AP | −0.002260 | [−0.002705, −0.001841] | 105/130 |
| CGM MLP participant-macro Brier | +0.000122 | [+0.000096, +0.000148] | 99/130 |
| Clean GRU participant-macro AP | −0.019959 | [−0.021592, −0.018438] | 128/130 |
| Clean GRU participant-macro Brier | +0.000759 | [+0.000644, +0.000877] | 125/130 |

At epoch 1, the CGM MLP exceeds the clean GRU in participant-macro AP by
0.029972 (paired 95% fixed-prediction interval [0.027209, 0.032852]); its
participant-macro Brier is lower by 0.001097 (interval [−0.001259,
−0.000933]), and pooled Brier is lower by 0.001122. The CGM MLP has the better
participant-macro AP for 127 of 130 participants and the better participant-
macro Brier for 127 of 130.

## Interpretation and limits

The replay resolves the immediate optimization question: one epoch was too
early, particularly for the clean GRU, whose performance improved materially
by epoch 2. The epoch-2 CGM MLP remains ahead of the epoch-2 clean GRU on all
three reported aggregate metrics. This does not show that event information
or graph relations cannot help. It shows that the tested event sequence model
has not beaten its matched CGM-only comparator under this development setup.

These intervals resample participants while keeping model predictions fixed;
they do not measure retraining variability, cover other seeds or folds, or
support a locked-test claim. The experiment tests an event-sequence model, not
an explicit temporal knowledge graph. Recorded-event availability also remains
an assumed retrospective occurrence-time replay. Therefore the next empirical
gate is to predefine a fair convergence/tuning budget for both baselines across
additional seeds and development folds, then construct a stronger causal
full-CGM-history comparator. Only after those gates should explicit relation
ablation experiments proceed.

## Artifacts

- Paired analysis: `audit/loop_controlled_epoch1_replay_comparison.json`
- ZIP validation and provenance: `audit/loop_controlled_epoch1_replay_bundle_validation.json`
- Private archive: `private/loop_epoch1_replay_20261011T103602Z_a0f2f38d_bundle.zip`
- Private extracted predictions: `private/loop_epoch1_replay_extracted/`
