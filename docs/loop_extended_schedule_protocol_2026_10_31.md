# Extended matched training schedule: preregistered local run

**Status:** both arms completed and passed the paired artifact audit. This is a
single-fold, single-seed schedule-sensitivity result, not confirmatory evidence.

## Question

Does the two-epoch graph-versus-time-aligned-pooling result change when both
models receive a longer, identical optimization schedule on the same frozen
outer-0 development split?

## Frozen run plan

- Cohort and fold: Loop development data, `outer-0`; locked holdout excluded.
- Input contract: the existing verified full-history cache and preflight receipt
  (`private/mps_research/preflight_outer-0_receipt.json`), whose manifest and
  window identity must match the staged input before either run starts.
- Seed: `20261031` for both model initializations and data order.
- Models: `graph-generic` and `aligned-nongraph`, both with 36,883 parameters.
- Input, timing, optimizer, batch size, and worker count: identical; event
  tokens and their causal event-to-CGM-bin assignment are unchanged.
- Schedule: eight complete epochs for each model, with checkpoint after each
  epoch. No stopping based on validation metrics and no hyperparameter changes
  after inspecting these results.
- Primary outcome: participant-macro average precision on the frozen
  outer-0 validation windows. Secondary outcome: participant-macro Brier score.
- Hardware: explicit CPU. The local PyTorch build includes MPS support, but the
  execution environment exposes no Metal device. The separate Kaggle session
  is left untouched. These results will be labeled as a CPU run and will not
  be presented as a bitwise reproduction of earlier GPU runs.

## Interpretation boundary

This single fold-seed pair is an optimization diagnostic, not a confirmatory
experiment or independent replication. It tests whether the two-epoch result
is sensitive to a longer fixed schedule. If the longer runs reverse or narrow
the metric difference, the two-epoch primary conclusion must be qualified;
the locked holdout remains unopened regardless of outcome.

## Run outputs

Private checkpoints and predictions are written below
`private/mps_research/outer0_seed20261031_*`. A public aggregate audit may be
created only after both runs complete and paired window identities, source
digests, run settings, and the prediction files have been verified.

## Execution record

The graph arm completed all eight epochs on CPU and evaluated 8,885,621
validation windows from 130 participants. Its participant-macro AP was
0.533263 and participant-macro Brier was 0.019720. The run marked
`complete=true`, verified prediction identity, and reported the frozen window
identity `26036d7d3d27c21a4407d15aacd916b98ba598dfded5da319288a74b54a592aa`.
Training loss decreased from 0.083591 in epoch 1 to 0.063649 in epoch 8.
The aligned-nongraph arm also completed all eight epochs under the identical
contract. Its participant-macro AP was 0.533979 and Brier was 0.019706. The
paired graph-minus-pooling AP difference was −0.000716 (95% fixed-prediction
participant interval [−0.001317, −0.000106]); the macro-Brier difference was
+0.00001415 ([+0.00000111, +0.00002768]). Both differences slightly favored
pooling. The [paired audit](../audit/loop_longer_schedule_outer0_seed20261031_graph_vs_aligned_cpu8.json)
reconciles the two run summaries and shared validation prediction identity.
The [novelty evidence-bundle audit](../audit/novelty_evidence_bundle_20261031_v9.json)
checks the full pair contract and reports no holdout use or emitted identifiers.

This result is directionally compatible with the two-epoch comparison, while
the metric gap is much smaller. The intervals condition on these fixed fitted
predictions and do not estimate training-seed, refitting, or cohort
uncertainty. Eight epochs is not evidence of convergence by itself.
