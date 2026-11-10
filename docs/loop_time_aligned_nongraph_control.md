# Time-aligned non-graph control: implementation and run gate

Updated: 30 October 2026

## Why this control is needed

The existing graph-versus-late-fusion sequence comparison gives the graph
events at observed CGM positions before its recurrent readout, while the
sequence comparator summarizes its event sequence separately. The graph's
advantage therefore cannot be attributed specifically to message passing.
This control preserves the same input events and causal event-to-time-bin
assignment, but pools event-only embeddings directly within bins and uses
ordinary node fusion plus a GRU. It removes the graph's event-CGM pairwise
message function.

## Frozen implementation contract

- 24 five-minute CGM slots, with the same value and observation-mask inputs.
- Up to 64 individual basal, bolus, and food event tokens from the same two-hour
  lookback and canonical event cache.
- Each event is assigned to the nearest observed CGM slot at or after its
  recorded occurrence time. No future slot may receive an event.
- Graph arm: event-CGM pair representation, edge expert, per-slot message
  aggregation and GRU readout.
- Non-graph arm: event-only embedding, direct per-slot pooling, count-normalized
  event summaries, gated CGM/event fusion and GRU readout.
- Both arms have exactly 36,883 trainable parameters, use the same AdamW
  optimizer (learning rate 0.0002, weight decay 0.0001), batch size, epoch
  count, participant split, cached windows, and immediate-availability
  assumption.
- Given the same random seed, shared CGM/event encoders, recurrent readout,
  and prediction head initialize identically. The notebook preflight checks
  this before training.
- The first generated notebook runs outer-0, seed 20261029, for two epochs and
  saves a paired validation audit with 10,000 participant-bootstrap draws.
  It is a development pilot. The locked cohort is never loaded for model
  fitting or scoring.

The parameter equality is exact by construction: CGM encoder 192, event
encoder 1,152, aligned fusion 8,320, two-branch gate 130, event-channel gates
16, GRU 24,960, and prediction head 2,113 parameters.

## Artifacts and verification state

- Kaggle notebook: [`loop_time_aligned_control.ipynb`](../kaggle_event_sequence_gru/loop_time_aligned_control.ipynb)
- Standalone one-cell source: [`ONE_CELL_TIME_ALIGNED_CONTROL.py`](../kaggle_event_sequence_gru/ONE_CELL_TIME_ALIGNED_CONTROL.py)
- Trainer variant: [`train_history_relations.py`](../kaggle_event_sequence_gru/train_history_relations.py), `--variant aligned-nongraph`
- Strict paired evaluator: [`compare_full_history_aligned_control.py`](../scripts/compare_full_history_aligned_control.py)

The notebook's embedded code archive SHA-256, notebook source compilation,
presence of the updated trainer/comparator, and exact parameter arithmetic
were checked locally. The pilot was then trained locally using an isolated
Python 3.12 environment (`torch==2.15.0`) on the Apple M4 MPS device. Both
arms passed CPU and MPS preflight. The matching private preflight receipt
verified the source, input content, manifest, participant membership, and
window identity before training.

### Completed five-fold, one-seed comparison

| Fold | Participants | Windows | Graph AP | Aligned AP | Graph-minus-control AP (95% participant CI) | Graph macro-Brier | Aligned macro-Brier | Graph-minus-control Brier (95% participant CI) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| outer-0 | 130 | 8,885,621 | 0.498579 | 0.507520 | −0.008941 [−0.009766, −0.008136] | 0.020534 | 0.020652 | −0.000118 [−0.000177, −0.000060] |
| outer-1 | 141 | 9,386,356 | 0.487658 | 0.493560 | −0.005902 [−0.006855, −0.004940] | 0.019487 | 0.019313 | +0.000174 [+0.000146, +0.000204] |
| outer-2 | 124 | 8,395,597 | 0.473438 | 0.484578 | −0.011140 [−0.012849, −0.009501] | 0.019139 | 0.018987 | +0.000152 [+0.000118, +0.000188] |
| outer-3 | 130 | 9,167,239 | 0.498401 | 0.505002 | −0.006601 [−0.007319, −0.005948] | 0.019143 | 0.019065 | +0.000078 [+0.000039, +0.000113] |
| outer-4 | 127 | 8,193,251 | 0.505888 | 0.511579 | −0.005691 [−0.006656, −0.004758] | 0.020478 | 0.020367 | +0.000111 [+0.000090, +0.000131] |

Across the five disjoint validation folds (652 participants total), the aligned
non-graph control has higher participant-macro AP in every fold. Macro-Brier
favors the graph only in outer-0 and favors aligned pooling in outer-1 through
outer-4. Each per-fold audit recomputed both metrics from saved predictions,
verified identical prediction-window identities, and checked matching inputs,
split, training budget, optimizer, and 36,883-parameter counts. The 10,000-draw
percentile intervals resample participants conditional on fixed predictions;
they are not model-refitting intervals.

The five pairs do not share one whole-project source digest: outer-0 used
`168ee086…`, outer-1 and outer-4 used `a4d1a919…`, and outer-2 and outer-3
used `a54c2f8a…`. Pair matching is valid within each fold, but this is not an
exact-source five-fold replication. The first outer-4 graph run recorded
`a54c2f8a…` while its control recorded `a4d1a919…`; the strict evaluator
rejected that pair, and it is excluded. The outer-4 graph was repeated at
`a4d1a919…`; only that matched pair is reported here. No pooled five-fold
inferential estimate is claimed.

This is a five-fold, one-seed development comparison. AP direction is
consistent, but Brier direction is not. The evidence does not show an AP
benefit from graph message passing over this matched control; the earlier
graph advantage over a late-fusion sequence model remains comparator-dependent.
Training-seed uncertainty is not measured.

Verified outputs:

- Graph run: `private/pilot_runs/loop_aligned_control_outer0_seed20261029/graph-generic`
- Aligned non-graph run: `private/pilot_runs/loop_aligned_control_outer0_seed20261029/aligned-nongraph`
- Paired comparison: [`loop_graph_vs_aligned_nongraph_outer0_seed20261029.json`](../audit/loop_graph_vs_aligned_nongraph_outer0_seed20261029.json)
- Outer-1 graph run: `private/pilot_runs/loop_aligned_control_outer1_seed20261029/graph-generic`
- Outer-1 aligned non-graph run: `private/pilot_runs/loop_aligned_control_outer1_seed20261029/aligned-nongraph`
- Outer-1 paired comparison: [`loop_graph_vs_aligned_nongraph_outer1_seed20261029.json`](../audit/loop_graph_vs_aligned_nongraph_outer1_seed20261029.json)
- Outer-2 paired comparison: [`loop_graph_vs_aligned_nongraph_outer2_seed20261029_current_source_rerun.json`](../audit/loop_graph_vs_aligned_nongraph_outer2_seed20261029_current_source_rerun.json)
- Outer-3 paired comparison: [`loop_graph_vs_aligned_nongraph_outer3_seed20261029_current_source.json`](../audit/loop_graph_vs_aligned_nongraph_outer3_seed20261029_current_source.json)
- Outer-4 matched-source paired comparison: [`loop_graph_vs_aligned_nongraph_outer4_seed20261029_source_a4d.json`](../audit/loop_graph_vs_aligned_nongraph_outer4_seed20261029_source_a4d.json)
- Rejected outer-4 graph artifact with a different source digest: `private/pilot_runs/loop_aligned_control_outer4_seed20261029_current_source/graph-generic`
- Matched outer-4 graph rerun: `private/pilot_runs/loop_aligned_control_outer4_seed20261029_current_source/graph-generic-source-a4d-rerun`
- Current evidence integrity audit (including the separate eight-epoch outer-0 schedule check): [`novelty_evidence_bundle_20261031_v9.json`](../audit/novelty_evidence_bundle_20261031_v9.json)

The original Kaggle notebook remains a reproducible run path. The completed
pilot used the equivalent local trainer; the Kaggle session was not changed.

Current embedded source archive SHA-256:
`41bb2662897c66edb9a499b7834c56f2d5520dbae41007b971fe01db418d41e4`.

## Run sequence

1. Add the generated notebook to Kaggle, attach the validated development-only
   full-history input (or the base input plus matching history-cache archive),
   and select the GPU runtime.
2. Run its single cell. It verifies cache hashes and the no-holdout contract
   before either model starts, then trains `graph-generic` and
   `aligned-nongraph` sequentially with the same fold, seed, and epoch count.
3. Download the printed `*_bundle.zip`. Preserve the exact ZIP and SHA-256; do
   not replace a prior run directory.
4. Run the paired evaluator from the bundled project code or local checkout:

   ```bash
   PYTHONPATH=src:scripts:kaggle_event_sequence_gru \
     python3 scripts/compare_full_history_aligned_control.py \
     PATH/graph-generic PATH/aligned-nongraph \
     --draws 10000 --seed 20261029 \
     --output audit/loop_graph_vs_aligned_nongraph_outer0_seed20261029.json
   ```

The evaluator refuses mismatched seed, fold, training budget, source digest,
optimizer, participant membership, window identity, event availability,
parameter count, or prediction rows. It recomputes the paired metrics from the
prediction archives and checks them against both run summaries.

## Interpretation and completed second-seed replication

The first seed (20261029) favors aligned pooling on AP in all five folds;
macro-Brier favors the graph in outer-0 and pooling in outer-1 through outer-4.
Its source digests vary across folds, although each within-fold pair matches.
The initial unmatched outer-4 graph artifact was excluded and rerun at the
control source.

The prespecified second seed (20261030) completed all five folds at two epochs
per arm under the same frozen source digest
`a4d1a91916a675024110e1c30d54546c3aa0d51724480dfdbcdbb141dea71648`. Each
strict pair passed and matched on 36,883 parameters, inputs, optimizer,
training membership, and prediction identity; the locked holdout was unused.
Time-aligned pooling had higher AP and lower macro-Brier in all five folds.
The five-fold audit is
[`loop_graph_vs_aligned_nongraph_seed20261030_five_fold_summary.json`](../audit/loop_graph_vs_aligned_nongraph_seed20261030_five_fold_summary.json).
Across its 652 validation participants, graph-minus-control AP was −0.012193
(95% fixed-prediction participant interval [−0.012935, −0.011445]) over 650
AP-defined participants; macro-Brier was +0.0001728
([+0.0001554, +0.0001894]).

The prespecified cross-seed summary averages each participant's paired metric
difference over both fixed seeds before resampling participants. Before that
calculation, both seeds' fold-level prediction identity digests and participant
sets were checked for equality. Graph-minus-control AP was −0.009900 (95%
participant-bootstrap interval [−0.010477, −0.009345]) over 650 participants
with defined AP; macro-Brier was +0.0001264 ([+0.0001096, +0.0001429]) over
all 652. Pooling had higher AP for 639 participants and lower Brier for 528.
See
[`loop_graph_vs_aligned_nongraph_two_seed_five_fold_participant_summary.json`](../audit/loop_graph_vs_aligned_nongraph_two_seed_five_fold_participant_summary.json).
The intervals condition on the saved predictions from two fitted seeds and the
same participant folds. They do not estimate training-seed, refitting, or
external-cohort uncertainty.

These results argue against a predictive benefit from the tested graph
message-passing operation over this time-aligned pooling control under this
two-epoch Loop protocol. They do not show that graphs generally fail or that
clinical relations are invalid. The next empirical gates are a fair
multi-epoch/convergence comparison, a matched CGM-only model, replicated
event-disabled controls, and validation of event availability assumptions.
Keep the locked final-performance group closed until model choices and analyses
are frozen. External-cohort replication and independent explanation-faithfulness
evaluation remain necessary for broader claims.
