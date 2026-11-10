# Causal event-endpoint perturbation — Loop development folds

## Design

This development-only experiment compared the generic temporal event graph,
which links each event to its nearest observed later CGM grid point, with a
matched graph that uses the second-nearest observed later CGM point when one is
available and otherwise falls back to nearest. The perturbation preserves
event records and timestamps, CGM history, event features, each participant
split, model layout, optimizer, seed, one-epoch budget, and prediction windows.
No future edges are allowed. Each model has 36,883 declared trainable
parameters. The same seed (`20261004`) was evaluated over all five outer folds.
Across folds, the runs cover 652 participant-fold assignments (participants
may recur across folds), 44,028,064 validation windows, and 1,296,297 positive
labels. Manifest, input, source and window identity digests match within the
pairs; all saved prediction sets passed identity checks. The locked holdout was
not used.

## Paired results

Differences below are **nearest endpoint minus second-nearest endpoint**.
Intervals are 10,000-draw paired participant-bootstrap intervals over fixed
predictions and therefore condition on the fitted models.

| Fold | Participants | Nearest AP | Second-nearest AP | AP difference (95% interval) | Nearest macro Brier | Second-nearest macro Brier | Brier difference (95% interval) |
|---|---:|---:|---:|---:|---:|---:|---:|
| outer-0 | 130 | 0.473800 | 0.474431 | −0.000631 [−0.001338, +0.000069] | 0.022036 | 0.021985 | +0.0000509 [+0.0000249, +0.0000774] |
| outer-1 | 141 | 0.459570 | 0.452889 | +0.006681 [+0.005551, +0.007850] | 0.019985 | 0.020247 | −0.0002618 [−0.0003405, −0.0001880] |
| outer-2 | 124 | 0.444437 | 0.444620 | −0.000183 [−0.000979, +0.000596] | 0.019922 | 0.019990 | −0.0000686 [−0.0001067, −0.0000326] |
| outer-3 | 130 | 0.469174 | 0.467556 | +0.001618 [+0.001084, +0.002134] | 0.019777 | 0.019834 | −0.0000571 [−0.0000791, −0.0000360] |
| outer-4 | 127 | 0.475577 | 0.471227 | +0.004350 [+0.003747, +0.004959] | 0.022465 | 0.022632 | −0.0001664 [−0.0002180, −0.0001219] |

Across five folds, nearest endpoints have higher AP on three folds and second-
nearest on two; nearest endpoints have lower macro Brier on four folds and
second-nearest on one. Unweighted mean fold differences are **+0.002367 AP**
and **−0.0001006 macro Brier**, descriptive only. Fold-level direction is not
uniform, and the paired intervals do not account for retraining, seed, fold,
or cohort uncertainty. These results support the limited statement that this
specific causal endpoint assignment can affect model predictions; they do not
establish a robust predictive advantage or clinical value.

## Interpretation

This is an endpoint-assignment sensitivity experiment, not a test of all
clinical relation semantics. The “second-nearest” alternative changes a
specific graph edge target while retaining event content and timing; it does
not show that learned relations are clinically valid or that graph explanations
are faithful. The results also do not isolate benefits over a non-graph model.

## Second-seed replication — complete, 28 October 2026

A second one-epoch seed (`20261005`) completed all five outer folds. Every
nearest/shifted pair passed the strict contract comparator, including matching
source/input digests, training membership, model size, optimizer, validation
rows, and prediction identity; the locked holdout was not accessed.

| Fold | Participants | Nearest-minus-shifted AP (95% fixed-model interval) | Nearest-minus-shifted macro-Brier (95% fixed-model interval) |
|---|---:|---:|---:|
| outer-0 | 130 | +0.001615 [+0.000980, +0.002263] | +0.0000189 [+0.0000010, +0.0000375] |
| outer-1 | 141 | +0.003555 [+0.002729, +0.004363] | −0.0001642 [−0.0002062, −0.0001225] |
| outer-2 | 124 | +0.001039 [−0.000182, +0.002215] | −0.0000620 [−0.0001138, −0.0000103] |
| outer-3 | 130 | +0.001413 [+0.000958, +0.001870] | −0.0000215 [−0.0000367, −0.0000078] |
| outer-4 | 127 | +0.000907 [+0.000004, +0.001877] | −0.0000179 [−0.0000505, +0.0000106] |

Across this seed, AP favors nearest on 5/5 folds and macro-Brier on 4/5. Across
both seeds, nearest has higher AP and lower macro-Brier in 8/10 seed-fold pairs.
To account for the same participants recurring across seeds, we averaged each
participant's paired metric difference over both fixed seeds and resampled
participants (10,000 draws). Mean AP difference is **+0.002097** (95% interval
**[+0.001761, +0.002443]**, 455/650 AP-defined participants positive); mean
macro-Brier difference is **−0.0000773** (**[−0.0000957, −0.0000594]**, nearest
lower for 408/652 participants). This bootstrap conditions on the two trained
seeds and does not estimate training-seed variability. It supports endpoint
assignment sensitivity for this particular model and dataset, not a broad
clinical relation benefit. See the [seed-20261005 five-fold
summary](../audit/loop_relation_endpoint_perturbation_seed20261005_five_fold_summary_20261028.json),
[combined two-seed summary](../audit/loop_relation_endpoint_perturbation_two_seed_five_fold_summary_20261028.json),
[participant-cluster bootstrap](../audit/loop_relation_endpoint_perturbation_two_seed_participant_cluster_bootstrap_20261028.json),
and the [outer-4 paired audit](../audit/loop_relation_endpoint_perturbation_outer4_seed20261005_paired_20261028.json).

Across both seeds and all five outer folds, nearest has higher AP in 8/10
seed-fold pairs and lower macro-Brier in 8/10. The descriptive unweighted mean
across the ten seed-fold differences is **+0.002036 AP** and **−0.0000750
macro-Brier**. These ten pairs are not ten independent samples: folds reuse
the same partition scheme and participants recur across the two seeds. This is
evidence that this particular endpoint choice can matter, not proof that the
relations are clinically valid or that the nearest endpoint gives a robust
benefit. See the [combined two-seed summary](../audit/loop_relation_endpoint_perturbation_two_seed_five_fold_summary_20261028.json).

To account for repeated participant appearances, a second aggregate first
averaged each participant's paired metric difference over both fixed seeds,
then bootstrap-resampled participants (10,000 draws). The participant-level
mean AP difference was **+0.002097** (95% interval **[+0.001761,
+0.002443]**, 455/650 AP-defined participants positive); mean macro-Brier
difference was **−0.0000773** (**[−0.0000957, −0.0000594]**, nearest lower for
408/652 participants). These intervals reflect participant sampling
conditional on the two trained seeds. They do not quantify variability across
new training seeds, budgets, or cohorts. The [cluster-bootstrap audit](../audit/loop_relation_endpoint_perturbation_two_seed_participant_cluster_bootstrap_20261028.json)
contains the reproducible aggregate and the script is
[`summarize_two_seed_endpoint_perturbation.py`](../scripts/summarize_two_seed_endpoint_perturbation.py).

## Limits and next step

Both seed screens cover all five outer folds; each fit uses one training
epoch. The participant-cluster bootstrap conditions on the two fitted seeds;
it does not capture variation across new seeds, training budgets, or cohorts.
The intervention tests sensitivity to a particular causal endpoint rule, not
all graph relation semantics, clinical validity, explanation faithfulness, or
real-time availability. Occurrence-time replay still assumes immediate
availability, which has not been measured. Next assess event-order and
relation-shuffle controls and explanation faithfulness before making a
relation-level claim. Keep the locked holdout sealed.

## Reproducibility records

- Outer-0 nearest-endpoint run: `private/mps_research/outer0_seed20261004_graph_generic_endpoint_v1`
- Outer-0 second-nearest run: `private/mps_research/outer0_seed20261004_graph_endpoint_shifted_v1`
- Paired, identifier-free result: [`audit/loop_relation_endpoint_perturbation_outer0_seed20261004_paired_20261025.json`](../audit/loop_relation_endpoint_perturbation_outer0_seed20261004_paired_20261025.json)
- Outer-1 paired result: [`audit/loop_relation_endpoint_perturbation_outer1_seed20261004_paired_20261025.json`](../audit/loop_relation_endpoint_perturbation_outer1_seed20261004_paired_20261025.json)
- Outer-2 nearest-endpoint run: `private/mps_research/outer2_seed20261004_graph_generic_endpoint_v2`
- Outer-2 second-nearest run: `private/mps_research/outer2_seed20261004_graph_endpoint_shifted_v1`
- Outer-2 paired result: [`audit/loop_relation_endpoint_perturbation_outer2_seed20261004_paired_20261026.json`](../audit/loop_relation_endpoint_perturbation_outer2_seed20261004_paired_20261026.json)
- Descriptive three-fold summary: [`audit/loop_relation_endpoint_perturbation_seed20261004_three_fold_summary_20261026.json`](../audit/loop_relation_endpoint_perturbation_seed20261004_three_fold_summary_20261026.json)
- Outer-3 nearest-endpoint run: `private/mps_research/outer3_seed20261004_graph_generic_endpoint_v1`
- Outer-3 second-nearest run: `private/mps_research/outer3_seed20261004_graph_endpoint_shifted_v1`
- Outer-3 paired result: [`audit/loop_relation_endpoint_perturbation_outer3_seed20261004_paired_20261026.json`](../audit/loop_relation_endpoint_perturbation_outer3_seed20261004_paired_20261026.json)
- Outer-4 nearest-endpoint run: `private/mps_research/outer4_seed20261004_graph_generic_endpoint_v1`
- Outer-4 second-nearest run: `private/mps_research/outer4_seed20261004_graph_endpoint_shifted_v1`
- Outer-4 paired result: [`audit/loop_relation_endpoint_perturbation_outer4_seed20261004_paired_20261026.json`](../audit/loop_relation_endpoint_perturbation_outer4_seed20261004_paired_20261026.json)
- Descriptive five-fold summary: [`audit/loop_relation_endpoint_perturbation_seed20261004_five_fold_summary_20261026.json`](../audit/loop_relation_endpoint_perturbation_seed20261004_five_fold_summary_20261026.json)
- Historical four-fold summary: [`audit/loop_relation_endpoint_perturbation_seed20261004_four_fold_summary_20261026.json`](../audit/loop_relation_endpoint_perturbation_seed20261004_four_fold_summary_20261026.json)
- Descriptive two-fold summary: [`audit/loop_relation_endpoint_perturbation_seed20261004_two_fold_summary_20261025.json`](../audit/loop_relation_endpoint_perturbation_seed20261004_two_fold_summary_20261025.json)
- Comparator: `scripts/compare_full_history_endpoint_perturbation.py`
- Both runs: manifest SHA-256 `69b41e4acfae7d2afc990c8cd15d8fc3f969784d4e5f6534a9263033d341ad52`; window identity SHA-256 `26036d7d3d27c21a4407d15aacd916b98ba598dfded5da319288a74b54a592aa`; source SHA-256 `70b3def4dac6413c96147045aa5b175a06fb00ace7e95d1bb15f382cff49cff2`.

The strict comparator verified matched contracts, parameter counts, event
availability, validation windows, reported metrics, and development-only
status before generating the result. The local full-history notebook was
regenerated to include the current `temporal_relations.py` implementation;
the full suite then passed with 150 passed and 4 skipped tests.
