# Fixed-checkpoint event-age reassignment control

Updated: 29 October 2026.

## Purpose and boundary

The current temporal graph does not consume event-token order as a sequence:
it assigns each event to an observed later CGM point and sums messages at that
CGM node. A permutation of event-token rows alone would therefore be a
structurally uninformative order control. The implemented diagnostic instead
reassigns the retained event ages among active event records within each
prediction window. It preserves the same event records, CGM history, labels,
age multiset, active-event count, model weights, and validation windows while
breaking each event record's pairing with its time and derived endpoint.

The age values are rotated by one position among the active newest-first event
slots. This is a deterministic, fixed-model input perturbation. It does not
refit the model, identify a causal effect, validate clinical relations, or test
whether the graph is better than a capacity-matched non-graph model. The
participant-bootstrap interval is conditional on the saved fit.

## Implementation and status

The inference implementation is
[`scripts/evaluate_event_age_reassignment.py`](../scripts/evaluate_event_age_reassignment.py).
It checks the saved run and epoch-1 checkpoint contracts, revalidates the
development-only staged cache with its fold receipt, checks window and label
counts, recomputes the exact prediction-window identity, and emits aggregate
participant-macro AP/Brier comparisons only. The locked holdout is excluded.

The first screen is complete for outer-0, seed `20261005`, using the saved
`graph-generic` epoch-1 checkpoint. Its 130 participants, 8,885,621 windows,
274,044 positives, and prediction-window identity all match the saved run.
Unperturbed replay reproduces saved participant-macro AP within `4.96e-8` and
macro-Brier within `1.70e-10`.

Original minus age-reassigned participant-macro AP is `+0.0002569` (10,000-
draw paired participant bootstrap 95% interval `[+0.0001281, +0.0003931]`);
87 of 130 participants favor the original pairing. Original minus
age-reassigned macro-Brier is `+0.00000214` (95% interval
`[-0.00000085, +0.00000505]`), which includes zero. The reassignment changed
124,545,358 active event-age values across 7,029,075 windows with at least two
retained events. This is a small, one-checkpoint ranking sensitivity; the
Brier result is inconclusive and this does not establish clinically valid
relations or generalizable benefit. Aggregate results are in
[`loop_event_age_reassignment_outer0_seed20261005_20261028.json`](../audit/loop_event_age_reassignment_outer0_seed20261005_20261028.json).

The replay used CPU because this Mac PyTorch environment reports neither CUDA
nor MPS. The previously authorized Kaggle URL returned a “We can't find that
page” screen in the current browser bridge, so no Kaggle runtime was inspected
or modified. The already-running Kaggle session remains untouched.

There is also an exact-source limitation: the saved run's source digest is
`70b3def4dac6413c96147045aa5b175a06fb00ace7e95d1bb15f382cff49cff2`, while
the current project source digest is different. The script reports both and
does not present source identity as verified. The unperturbed predictions do
reproduce the saved metrics and identity to tight tolerances. The script
requires the checkpoint and run metadata to agree, loads the checkpoint
strictly into the current architecture, and revalidates the exact data/split
contract. Interpret this as a post-hoc diagnostic conditional on those
compatibility checks, not as an exact source-reproduction claim.

## Reproduce the screen

From the repository root, in the project's Python environment with PyTorch:

```bash
PYTHONPATH=src:scripts:kaggle_event_sequence_gru python scripts/evaluate_event_age_reassignment.py \
  --input-directory private/kaggle_loop_full_history_input \
  --source-run private/mps_research/outer0_seed20261005_graph_generic_endpoint_v1 \
  --checkpoint private/mps_research/outer0_seed20261005_graph_generic_endpoint_v1/checkpoint-epoch-1.pt \
  --preflight-receipt private/mps_research/preflight_outer-0_receipt.json \
  --fold outer-0 --seed 20261005 --device cpu \
  --batch-size 2048 --workers 2 \
  --output audit/loop_event_age_reassignment_outer0_seed20261005_20261028.json
```

On an available accelerator, use `--device cuda` or `--device mps`. This
screen completed on CPU. It reported 130 participants, 8,885,621 windows,
274,044 positives, and the saved run's exact prediction-window identity.

The five-fold, seed-`20261005` replication is also complete. Across its 652
participants, 44,028,064 windows, and 1,296,297 positive labels, the descriptive
unweighted mean fold AP difference is `+0.0001155`, with the original pairing
favoring AP in all five folds; only the outer-0 participant interval excludes
zero. Mean fold macro-Brier difference is `-0.00000134`, and three folds favor
the original pairing; only outer-3's interval excludes zero. These averages
are descriptive, not a pooled bootstrap or independent-fold inferential test.
The five-fold summary is
[`loop_event_age_reassignment_seed20261005_five_fold_summary_20261028.json`](../audit/loop_event_age_reassignment_seed20261005_five_fold_summary_20261028.json).
The second seed, `20261004`, is complete across all five folds as well. The
original event-time pairing has higher AP in all ten seed-fold fits, but only
three of ten fold-specific participant intervals exclude zero. The mean AP
difference over the ten fits is `+0.0001118`. Macro-Brier differences are
positive in five fits and negative in five; four of ten fold intervals exclude
zero. These ten fits reuse the same 652 participants across seeds. Their
fold-specific intervals must not be pooled, and we did not retain participant
deltas across seeds for a cluster bootstrap. See the [second-seed summary](../audit/loop_event_age_reassignment_seed20261004_five_fold_summary_20261029.json)
and [two-seed summary](../audit/loop_event_age_reassignment_two_seed_five_fold_summary_20261029.json).
The interpretation remains limited to one deterministic age rotation on
fixed epoch-1 models. The next gate is explanation faithfulness, not a claim
that graph relations are clinically valid.
