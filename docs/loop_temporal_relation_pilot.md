# Generic-edge versus typed temporal-relation pilot

## Five-fold modality-routing replication — 20 October 2026

The one-epoch `graph-typed` versus `graph-generic` comparison is now complete
on all five patient-disjoint development validation folds for seed `20261004`.
Each model has 36,883 trainable parameters and uses the same input contract,
24-step CGM history, up to 64 event instances, training budget, optimizer,
and fold-specific prediction windows. All five run archives report complete
training and verified prediction identity; the strict paired audits also
confirmed matching manifests and window identities. Across the folds this
covers 652 development participants and 44,028,064 validation windows. The
locked holdout was not used.

| Fold | Typed − generic participant-macro AP (paired 95% interval) | Typed − generic participant-macro Brier |
|---|---:|---:|
| outer-0 | −0.002015 [−0.002942, −0.001097] | +0.00007870 |
| outer-1 | −0.001809 [−0.002957, −0.000691] | +0.00002327 |
| outer-2 | −0.001174 [−0.001661, −0.000716] | −0.00000891 |
| outer-3 | +0.000718 [+0.000289, +0.001149] | −0.00001100 |
| outer-4 | +0.001902 [+0.001054, +0.002754] | −0.00011623 |

Typed routing has higher AP in two folds and generic routing in three. The
unweighted mean of the five fold-level AP differences is **−0.000476** (range
**−0.002015 to +0.001902**); the unweighted mean macro-Brier difference is
**−0.00000683**, with typed lower in three folds and generic lower in two.
These averages are descriptive only. The per-fold participant-bootstrap
intervals condition on each pair of fixed fits and do not quantify seed,
refitting, or study-level uncertainty. This is mixed evidence, not a reliable
typed-routing gain or a broad rejection of typed relations.

The result tests only this specific routing rule: modality IDs are derived
from basal/bolus/food event features, and events connect to the nearest
observed later CGM slot. It does not test independently annotated clinical
relation semantics or establish the value of graph structure as a whole.
Immediate event availability remains assumed rather than measured. The
machine-readable fold data and audit references are in
[`audit/loop_relation_typed_vs_generic_seed20261004_five_fold_summary_20261020.json`](../audit/loop_relation_typed_vs_generic_seed20261004_five_fold_summary_20261020.json).

The next discriminating test is a prespecified relation perturbation that
preserves event and CGM inputs, timestamps, parameter count, and training
budget while breaking the event-to-CGM relation assignment. Compare it with
the same generic graph and a matched event-disabled branch. Then evaluate
explanation faithfulness with a prespecified intervention test. Do not use the
locked holdout until model selection and the full protocol are frozen.

## Latest verified execution — 19 October 2026

The corrected development-only pilot completed on Kaggle for `outer-0`, seed
`20261003`, using one full-data epoch per matched model. Both branches ran on
CUDA (`Tesla T4` ×2), used 36,883 trainable parameters, and passed checkpoint
and participant-level prediction-identity validation. The locked holdout was
not used. The strict paired comparison covered the same 130 validation
participants, 8,885,621 windows, and 274,044 positive labels.

The one-epoch generic shared-edge model scored participant-macro AP **0.47448**
and participant-macro Brier **0.021522**. Modality-typed routing scored AP
**0.47186** and Brier **0.021619**. The paired typed-minus-generic AP difference
was **−0.002622** (95% participant-bootstrap interval **[−0.003386,
−0.001909]**); typed routing had higher AP for 35 participants and lower AP
for 95. Its participant-macro Brier difference was **+0.0000974** (95% interval
**[+0.0000758, +0.0001213]**), with higher Brier for 105 participants and lower
Brier for 25. Thus this pilot does not support a predictive benefit from the
tested modality-specific routing. The confidence interval conditions on these
two fixed fits and does not include uncertainty from retraining, seeds, folds,
or cohort selection.

This is a one-seed, one-fold, one-epoch development pilot, not a definitive
model comparison and not evidence that knowledge graphs are generally
ineffective. The conclusion is narrower: under this matched setup, event
modality-specific expert routing did not improve performance over the generic
edge operation. Relations are deterministically derived from event modality
and timestamp ordering; they are not independently annotated clinical facts.
Event availability is replayed by occurrence time with immediate availability
assumed, not measured. The comparison does not establish that a graph adds
information beyond a same-capacity, same-information non-graph model.

The complete Kaggle bundle is
`/kaggle/working/loop_temporal_relations_fixed_20261018T153138Z_bundle.zip`
(251,155,821 bytes; SHA-256
`cee3c39501f87d4d171cffec023dea4ad161388e300296a892558edff9da9493`). It
contains both model run directories, validation predictions, checkpoints,
paired comparison, and run metadata. The metric and provenance summary is
recorded in
[`audit/loop_temporal_relation_outer0_paired_pilot.json`](../audit/loop_temporal_relation_outer0_paired_pilot.json).
The ZIP remains in Kaggle working storage and has not yet been copied into the
local project. Download and verify it before relying on the raw prediction
archives outside that session.

### Matched experiment

Both variants use the same 24-slot CGM history, up to 64 retained event
instances, identical event-to-CGM edges, split, seed, optimizer, training
budget, initialization and 36,883-parameter budget. Each retained event
connects to its nearest observed CGM grid point at or after event time; future
edges are forbidden. The relation label comes from the source event's
basal/bolus/food modality and temporal ordering.

| Variant | Edge message routing |
|---|---|
| `graph-generic` | Uses a generic edge operation, averaging the shared expert bank for every edge. |
| `graph-typed` | Routes each edge to the expert selected by the event modality. |

The strict pairing verified matching input, split, training membership,
source code, validation-window identity, and prediction-window identity. It
compared per-participant metrics and used 2,000 participant-bootstrap draws.
These intervals quantify paired participant variation for the fixed runs,
not run-to-run or population-wide model uncertainty.

### Research implications and next gates

Do not claim that typed relations improved prediction from this result. Before
any stronger relation or graph claim, run multiple seeds and all five
development outer folds, compare against a non-graph model given the same
history/events and capacity, and include event-disabled and relation-shuffled
controls. Keep the locked holdout sealed until the protocol, model family,
preprocessing, and thresholds are frozen. A graph explanation claim also
requires a prespecified faithfulness test; attention or edge weights alone do
not establish clinical explanation quality.

The one-epoch relation pilot is also not directly comparable to the earlier
two-epoch event-sequence result. If the next experiment compares model families,
train them under a matched budget and information set. Event timing remains a
material limitation because recorded occurrence time does not tell us when an
event became available to a real-time predictor.

### Direct graph-versus-non-graph control — 19 October 2026

The missing same-information, same-capacity comparison has now completed for
outer-0, seed `20261003`, one epoch. The graph-generic model achieved
participant-macro AP **0.474481** and Brier **0.021522**. The non-graph
late-fusion CGM/event sequence model with exactly 36,883 parameters achieved
AP **0.389901** and Brier **0.024211**. The paired graph-minus-sequence AP
difference was **+0.084580** (10,000-draw 95% participant-bootstrap interval
**[+0.078104, +0.090816]**), while the participant-macro Brier difference was
**−0.002690** (10,000-draw 95% interval **[−0.003043, −0.002347]**). Exact per-window
identity, labels, model split, training membership, input digest, optimizer,
event/history budget, and prediction rows matched over 130 participants and
8,885,621 validation windows. A second paired analysis with 10,000 bootstrap
draws produced essentially unchanged point estimates; see the [sensitivity
audit](../audit/loop_graph_vs_capacity_matched_outer0_paired_10000draws_20261019.json).

This advances the research direction: the first controlled result favors the
tested graph message-passing parameterization over a matched-capacity
non-graph sequence model. It does not yet validate the typed relations: typed
routing was slightly below generic routing in the prior test. The current
finding is provisional because it is one seed, one fold, one epoch, and does
not include fit-to-fit variability. Replicate the predeclared graph-generic
versus capacity-matched sequence contrast across the five outer folds and
multiple seeds before making the central claim. Then test whether relation
semantics add beyond generic graph connectivity, using relation-shuffle and
event-order controls; retain an event-disabled control to isolate event
information. Keep the holdout sealed. Do not claim clinical explanation
faithfulness without a separate intervention/faithfulness evaluation.

The report and archive details are in
[`loop_non_graph_capacity_matched_control.md`](loop_non_graph_capacity_matched_control.md)
and [`audit/loop_graph_vs_capacity_matched_outer0_paired.json`](../audit/loop_graph_vs_capacity_matched_outer0_paired.json).

### Earlier execution failures (superseded)

The first generic attempt completed training but failed checkpoint validation
because its run metadata omitted `hidden`. A second failure was avoided by
stopping before rerun when Kaggle's import dialog remained on “Loading file...”
and the stale cell was still active. The runtime patch added `hidden` to the
checkpoint metadata, and the regression test now checks it against the
checkpoint contract. The eventual corrected run above completed both branches
and passed strict comparison. Earlier notes in this project describing the
pilot as not yet run are historical and are superseded by the 19 October
execution.

The current notebook and runner source are
[`loop_temporal_relation_pilot.ipynb`](../kaggle_event_sequence_gru/loop_temporal_relation_pilot.ipynb)
and [`RUN_TEMPORAL_RELATION_PILOT_FIXED.py`](../kaggle_event_sequence_gru/RUN_TEMPORAL_RELATION_PILOT_FIXED.py).
The analysis is informed by the
[prior-work review](syscon_2026_prior_work_review.md) and the
[novelty assessment](novelty_assessment.md). Novelty remains provisional until
the remaining controlled comparisons and replication are complete.
