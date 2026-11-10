# Non-graph sequence control for the temporal-relation pilot

Updated: 19 October 2026

## Purpose

The generic-edge versus typed-edge pilot only compares two graph-routing
choices. It cannot establish whether a graph helps over a model that receives
the same recorded information. This control adds a non-graph, late-fusion
sequence model for the primary comparison `graph-generic` versus a
capacity-matched CGM-history plus event-sequence predictor.

Both models use the same 24-step CGM history (value and observation mask), the
same occurrence-time replay of up to 64 event tokens, the same recorded event
values and relative event ages, and the same frozen patient split and labels.
The sequence control uses independent GRUs for CGM history and the ordered
event sequence, then concatenates their states for prediction. It has no nodes,
edges, message passing, or relation-specific routing. It therefore tests the
value of the tested graph topology and message-passing implementation over an
event sequence, not whether the data contain clinically meaningful causal
relations.

## Exact capacity contract

The graph pilots have 36,883 trainable parameters. The existing
`history-event` model has 36,609 parameters, so it is close but not an exact
capacity match. A separate `history-event-capacity-matched` variant uses these
widths:

| Component | Width |
|---|---:|
| CGM-history GRU | 66 |
| Event-token embedding | 27 |
| Event-sequence GRU | 67 |
| Late-fusion prediction head | 24 |
| Total trainable parameters | **36,883** |

The count is tested algebraically and again by the runtime smoke test against
the instantiated PyTorch model. Existing history-only and history-event
variants are unchanged. The capacity-matched comparison should use outer-0,
seed `20261003`, one epoch initially, batch size 4096, 3 data workers, AdamW
(`2e-4`, weight decay `1e-4`), and the same frozen input and validation rows as
the relation pilot. The one-epoch run is a screening gate only: existing
history models were still improving between epochs 1 and 2, so the one-epoch
comparison below is a screening result; model-family conclusions still require
replication across the five development folds and multiple seeds.

## Completed first matched comparison — 19 October 2026

The development-only `history-event-capacity-matched` run completed on Kaggle
for outer-0, seed `20261003`, one epoch, batch size 4096, and three workers.
It trained on the expected 26,949,192 windows and evaluated the same 130
validation participants, 8,885,621 windows, and 274,044 positive labels as the
saved `graph-generic` run. Both models have exactly 36,883 trainable
parameters. A strict paired comparison verified shared input content, frozen
window and prediction identities, fold, seed, training membership, optimizer,
event/history budgets, and identical participant/time/label rows. The original
paired audit used 2,000 participant-bootstrap draws (bootstrap seed
`20261003`); a follow-up used 10,000 draws (seed `20261019`) on the same fixed
predictions. The point estimates were identical and the confidence intervals
were stable to the higher draw count.

The graph-generic model scored participant-macro AP **0.474481** versus
**0.389901** for the capacity-matched non-graph sequence model. The paired
graph-minus-sequence AP difference was **+0.084580** (10,000-draw 95%
participant-bootstrap interval **[+0.078104, +0.090816]**); graph AP was
higher for 126 of 130 participants. Participant-macro Brier was **0.021522**
versus **0.024211**, with difference **−0.002690** (10,000-draw 95% interval
**[−0.003043, −0.002347]**); graph Brier was lower for all 130 participants.
Pooled Brier was 0.021164 versus 0.023823.

This is the first direct evidence in this project that the tested graph model
adds predictive value beyond a non-graph model with the same recorded inputs
and exact parameter count. It remains a screening result from one seed, one
fold, and one epoch. The intervals resample participants conditional on these
two fitted models; they do not capture training variability or establish
general graph superiority. It does not establish clinical causality or
explanation faithfulness. Event replay still assumes immediate availability
from occurrence time, and that assumption has not been measured.

## Local Apple MPS cross-hardware fit — 19 October 2026

To verify that the Kaggle result was not a runner-specific artifact, both
variants were freshly fit on the same development input using an Apple M4 MPS
accelerator. They used outer-0, seed `20261003`, one epoch, batch size 4096,
two producer workers, AdamW (`2e-4`, weight decay `1e-4`), and exactly 36,883
parameters per model. The fresh local input preflight passed across all 64
history/feature/CGM/event partitions and returned the same input content,
manifest, training-membership, window, and prediction-window digests as the
Kaggle comparison. Both prediction sets verified across 130 participants,
8,885,621 windows, and 274,044 positives; `locked_holdout_used` is false.

The MPS graph-generic model scored participant-macro AP **0.475384** and
macro Brier **0.021945**. Its capacity-matched non-graph sequence control
scored AP **0.394764** and Brier **0.023899**. The paired graph-minus-sequence
AP difference was **+0.080620** (10,000-draw participant-bootstrap 95% interval
**[+0.071498, +0.089245]**); graph AP was higher for 114/130 participants.
The macro Brier difference was **−0.001953** (interval
**[−0.002211, −0.001708]**); graph Brier was lower for 127/130 participants.
These fixed-fit intervals do not measure refit uncertainty.

This independently trained cross-hardware pair reproduces the direction and
similar magnitude of the Kaggle screening result. It is a robustness check on
the same fold, seed, epoch budget, and cohort, not an independent seed or
cohort replication. The Kaggle fit used three workers and the local fit used
two; source hashes and hardware are retained in the audit. The follow-up does
not establish graph-family superiority or the value of typed relations.
Predictions, checkpoints, run contracts, and the paired report are under the
ignored private directory `private/mps_research/`; the aggregate audit is
[`audit/loop_mps_outer0_graph_vs_sequence_paired_20261019.json`](../audit/loop_mps_outer0_graph_vs_sequence_paired_20261019.json).

## Outer-0 second-seed replication — 20 October 2026

The same frozen one-epoch contract was independently fit on Apple MPS for
outer-0 with seed `20261004`. The graph and sequence runs used the same 130
validation participants, 8,885,621 windows, 274,044 positives, training
membership, input digest, optimizer, batch size, event/history budgets, and
36,883 parameters per model. Prediction-window identity matched exactly;
the locked holdout was not used.

Graph-generic scored participant-macro AP **0.473152** and macro Brier
**0.022039**; the sequence control scored AP **0.394613** and Brier
**0.024217**. The paired 10,000-draw participant bootstrap gave AP difference
**+0.078540** (95% interval **[+0.069529, +0.087102]**), with graph AP higher
for 114/130 participants. Macro-Brier difference was **−0.002178** (95%
interval **[−0.002464, −0.001901]**), with graph Brier lower for 128/130.
The interval conditions on these two fitted predictions and is not training
uncertainty.

The AP and Brier differences have the same direction and similar magnitude
under seeds `20261003` and `20261004` on outer-0. This is an initial two-seed
replication on one fold; it does not establish seed robustness across folds,
convergence, or semantic relation value. The model contrast remains between
two specific architectures, despite matched parameter count, inputs, and
training contract. Relation shuffle, endpoint/time reconstruction,
event-order perturbation, and multi-seed results across additional folds are
still needed before claiming that clinical relation semantics explain the
advantage.

The seed-20261004 audit is
[`audit/loop_mps_outer0_seed20261004_graph_vs_sequence_paired_20261020.json`](../audit/loop_mps_outer0_seed20261004_graph_vs_sequence_paired_20261020.json).
Both run directories and their checkpoints/predictions are protected under
`private/mps_research/outer0_seed20261004_{graph_generic,sequence_mps}/`.
The machine-readable two-seed summary is
[`audit/loop_mps_outer0_graph_sequence_two_seed_summary_20261020.json`](../audit/loop_mps_outer0_graph_sequence_two_seed_summary_20261020.json).

The second seed was then completed on outer-1 under the same contract. Graph-
generic scored AP **0.459892** versus **0.369684** for the sequence control;
paired difference **+0.090208** (95% interval **[+0.081627, +0.098271]**).
Macro-Brier difference was **−0.002430** (95% interval
**[−0.002807, −0.002070]**). The pair matched on all 9,386,356 validation
windows and 141 participants; AP was defined for 140 participants. Both
prediction identity digests matched, with 36,883 parameters per model and no
holdout use. This is the second seed on two folds, still one epoch. The
two-seed/two-fold machine-readable interim summary is
[`audit/loop_mps_graph_sequence_two_seed_two_fold_summary_20261020.json`](../audit/loop_mps_graph_sequence_two_seed_two_fold_summary_20261020.json).

**Update, 20 October 2026 — second seed complete across all five folds.**
Seed `20261004` has now completed on outer-2, outer-3, and outer-4 as well.
All five paired audits verify identical validation windows per pair, 36,883
parameters per model, the same frozen manifest and input, and no locked-holdout
use. Graph-generic has higher participant-macro AP in every fold at both
seeds. Across the five folds, the descriptive mean AP difference is +0.086532
for seed `20261003` and +0.086575 for seed `20261004`; the corresponding mean
macro-Brier differences are −0.002113 and −0.002220. These fold means are
descriptive, not inferential intervals. The individual paired bootstrap
intervals condition on fixed predictions and do not capture model-fitting or
seed uncertainty. Each fit remains a one-epoch exploratory screen, and the
graph and sequence architectures differ beyond topology. Therefore the
replication supports this graph-generic implementation over this matched
sequence control on these development folds, but does not isolate clinical
relation semantics or establish explanation faithfulness.

The three new seed-`20261004` paired audits are
[`outer-2`](../audit/loop_mps_outer2_seed20261004_graph_vs_sequence_paired_20261020.json),
[`outer-3`](../audit/loop_mps_outer3_seed20261004_graph_vs_sequence_paired_20261020.json),
and [`outer-4`](../audit/loop_mps_outer4_seed20261004_graph_vs_sequence_paired_20261020.json).
The complete machine-readable two-seed/five-fold summary is
[`audit/loop_mps_graph_sequence_two_seed_five_fold_summary_20261020.json`](../audit/loop_mps_graph_sequence_two_seed_five_fold_summary_20261020.json).
Next, test relation semantics with event-disabled and relation-perturbation
controls under matched capacity and training, then test explanation fidelity;
do not open the locked holdout until those choices are frozen.

The matched model's original report omitted `locked_holdout_used`. Before
comparison, the metadata was repaired transparently: the development input
contract states that the locked holdout is absent, and its training-membership
digest, fold, seed, and training counts exactly match the independent graph
run whose report explicitly records `locked_holdout_used=false`. No predictions
or metrics were changed. The trainer was also fixed to emit this field in
future runs.

The original paired metrics are recorded in
[`audit/loop_graph_vs_capacity_matched_outer0_paired.json`](../audit/loop_graph_vs_capacity_matched_outer0_paired.json), and the higher-draw sensitivity check is in
[`audit/loop_graph_vs_capacity_matched_outer0_paired_10000draws_20261019.json`](../audit/loop_graph_vs_capacity_matched_outer0_paired_10000draws_20261019.json).
The complete Kaggle archive, including checkpoints and all participant
prediction shards for both runs, is
`/kaggle/working/loop_graph_vs_capacity_matched_outer0_20261019_bundle.zip`
(251,995,219 bytes; SHA-256
`dc0285de0ca1bbd43d9458fcdfad6187b61dfeecac272829e2d6944cc84a3ae1`).
The paired JSON inside the Kaggle bundle has SHA-256
`340c0d8c4660777176d4e47f124c2d5f699dbc89ccf47b0239cb6eba2709673a`.
The complete bundle has also been downloaded to the ignored local path
`private/kaggle_artifacts/loop_graph_vs_capacity_matched_outer0_20261019_bundle.zip`.
Its ZIP CRC and SHA-256 were checked locally, and the strict paired comparator
was rerun from the extracted prediction shards. It reproduced the Kaggle AP,
Brier, participant counts, and intervals.

## Execution artifact and guardrails

`kaggle_event_sequence_gru/loop_matched_sequence_control.ipynb` is the
code-complete Kaggle notebook. It embeds the refreshed project trainer, so
only the validated development-only full-history input dataset needs to be
attached. The single cell verifies the embedded code digest and input
contract, requires CUDA, refuses to overwrite a prior run, verifies completion
and parameter count, then writes a ZIP with a streaming SHA-256 digest. It
automatically invokes the strict comparator if exactly one matching completed
`graph-generic` run is already under `/kaggle/working`; otherwise it clearly
marks the paired comparison pending. The completed run used the validated
full-history input and staged project trainer without stopping or resetting
the active Kaggle session.

After execution, compare the sequence-control archive against the saved
`graph-generic` archive using exact equality of participant, timestamp, label,
prediction-window identity, manifest, window identity, input content, fold,
seed, training membership, optimizer, and epoch/batch budget. Report paired
participant bootstrap differences for average precision and Brier score.
If those fit contracts differ, rerun the models under a common contract before
interpreting the comparison. Keep the locked holdout sealed.

The strict local comparator is
[`scripts/compare_graph_sequence_archives.py`](../scripts/compare_graph_sequence_archives.py).
It also requires matching training-window/positive counts and exactly equal
36,883-parameter budgets; model-specific source hashes are retained in the
report rather than incorrectly required to match. Once both run directories
are available locally, run:

```bash
PYTHONPATH=src python3 scripts/compare_graph_sequence_archives.py \
  path/to/graph-generic path/to/history-event-capacity-matched \
  --output audit/loop_graph_vs_sequence_outer0_paired.json
```

## Interpretation boundary

If the non-graph sequence model matches or exceeds the graph model, there is
no evidence from this pilot that graph message passing adds predictive value.
If the graph model leads, the result is only preliminary support for that
graph parameterization; it still needs repeated folds/seeds, event-order and
relation-shuffle controls, a harmonized training budget, and a prespecified
explanation-fidelity evaluation. The pilot's event availability remains
retrospective occurrence-time replay with immediate availability assumed,
not measured.

## Outer-1 patient-fold replication — 19 October 2026

The matched pair was repeated on outer-1 with seed `20261003`, one epoch,
batch size 4096, two producer workers, AdamW (`2e-4`, weight decay `1e-4`),
and 36,883 trainable parameters in each model. Both runs passed the same
verified input preflight and produced identity-verified predictions for all
9,386,356 validation windows across 141 participants (270,499 positives).
The locked holdout was not used.

Graph-generic achieved participant-macro AP **0.460125** and macro Brier
**0.020059**; the non-graph sequence control achieved AP **0.378379** and
Brier **0.022213**. The paired 10,000-draw participant bootstrap gave AP
difference **+0.081746** (95% interval **[+0.073130, +0.090150]**) and macro
Brier difference **−0.002153** (95% interval **[−0.002476, −0.001836]**).
The complete audit is
[`audit/loop_mps_outer1_graph_vs_sequence_paired_20261019.json`](../audit/loop_mps_outer1_graph_vs_sequence_paired_20261019.json).

This is a second fold on the same seed, not an independent seed replication.
The matching direction across outer-0 and outer-1 is encouraging, but the
one-epoch results remain exploratory. They do not isolate the benefit of
clinical relation semantics; relation-shuffle and endpoint/time reconstruction
controls and further seeds/folds are still required.
