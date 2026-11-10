# Decisive experiments and claim boundaries

Updated: 31 October 2026. The graph-generic versus exact-parameter-count event-sequence comparison favors graph-generic in all ten one-epoch fits, but does not isolate topology because alignment, fusion, and computation differ. The stricter same-input, same-timing, exactly parameter-matched time-aligned pooling comparison is complete for two seeds and five patient-disjoint folds at two epochs; pooling leads graph message passing on participant-macro AP in all ten fold-seed pairs and on Brier across every second-seed fold. Typed routing remains mixed, nearest-endpoint perturbation shows small sensitivity, and event-age reassignment effects are very small. Event-disabled graph evidence still covers one fold/seed. A recovered full-history sequence event-zero ablation on outer-0/seed 20261003 (two epochs) favors event-zero, but is a separate architecture and its archive lacks an explicit locked-holdout-use marker; it does not replicate the graph ablation. The sampled deletion screen remains selection-conditioned. Results support a bounded comparison of these implementations, not a general claim for or against graph methods. The [research protocol](research_protocol.md) governs labels, splits and metrics; the [current novelty evidence report](novelty_evidence_report_2026_10_31.md) consolidates results and prior work. Direct graph-based hypoglycemia prediction and LSTM-versus-GAT comparisons are prior work; the remaining candidate contribution must be stated as the controlled result for this endpoint, cohort, and protocol.

Execution status has advanced since this specification: the matched G0-vs-B4
screening contrast is complete for two seeds and five folds; several relation
perturbations also have two-seed/five-fold coverage. The ordered gates and
limits are maintained in [Next research steps after the first matched graph
comparison](next_steps_after_controlled_first_gate.md) and the current
[novelty evidence report](novelty_evidence_report_2026_10_31.md).

## E0: Feasibility and information audit

Produce the patient audit in the research plan. Additionally record source fields with actual availability timestamps, assumed timestamps, corrected values, missing capture metadata and placeholders. Determine which event relations are directly recorded versus constructed from types/timing.

For each edge family, report its count, contributing participants, relation-frequency distribution and whether endpoint types plus time determine its label. Measure a development-only relation-prediction control if dependence is not obvious. Report sparse/unidentifiable relations; do not invent them.

Gate: a fixed eligible-window manifest, verified provenance and enough participant/episode evidence for the intended precision. Sample-size adequacy is not established by the number of windows.

## E1: Controlled representation benchmark

| ID | Model / representation | Purpose |
|---|---|---|
| B0 | Current glucose and slope scores | Basic forecasting reference. |
| B1 | Logistic regression and boosted trees | Strong engineered-feature reference. |
| B2 | Multimodal GRU | Original primary comparator. |
| B3 | GRU-D-style mask/time baseline | Ensure missingness handling is not mistaken for KG benefit. |
| B4 | Event-sequence model using individual events, values, types and exact admissible times | Controls graph structure while retaining the same recorded event information. The dual-GRU late-fusion implementation and graph-generic pilot both have exactly 36,883 parameters; their one-fold/one-seed paired screening result favors G0. See [capacity-matched control](loop_non_graph_capacity_matched_control.md). |
| B5 | Time-neighborhood GNN | Match the temporal graph family without claiming exact GAT-BiGRU reproduction. |
| B6 | Fixed modality-summary physiology graph | Test individual events against physiology-inspired summary graphs. |
| B7 | Visibility graph on CGM | Relevant CGM-only reference; compare against the CGM-only subset of other models. |
| G0 | Individual-event graph, shared/generic edge transform | Control event resolution and topology. |
| G1 | Same graph, relation-specific transforms | Main typed-graph candidate. |
| G2 | Same graph, edge representation derived from endpoint types and time | Test whether relation labels contribute beyond reconstructible descriptors. |

All full-modality models receive the same admissible records and engineered summaries. If B6 compresses events into summaries, compare it to a summary-only sequence control as well; otherwise a G1−B6 difference confounds graph design with information loss. If exact reproduction is unavailable, label the implementation as an adaptation and list the departures.

Match training/search budgets and report parameter counts and learning curves. Compare width-adjusted G0/G1 models and a sequence model of similar capacity. Use at least three fixed seeds, paired folds and participant-level intervals. A result favoring G1 over B2 alone is insufficient for a semantic-value claim.

The graph-generic versus late-fusion event-sequence contrast is now complete for two seeds across five folds at one epoch per fit; it favored graph-generic in all ten pairs, but the models differ in event-CGM alignment, fusion, and computation, so it does not isolate topology. The stricter graph-generic versus time-aligned-pooling comparison is complete for two seeds across five folds at two epochs and favors pooling in all ten AP comparisons. An eight-epoch check exists for outer-0 at one seed and slightly favors pooling, but does not establish convergence. The semantic-routing contrast is AP(G1)−AP(G0); a one-seed five-fold pilot is mixed and gives no typed-relation gain. G1 versus G2 tests whether modality routing adds beyond endpoint/time-reconstructible features. These contrasts require identical event instances, values, times, folds and training budgets. AP(G0)−AP(B2) is a secondary multimodal-versus-CGM comparison because it does not isolate graph structure. Also compare summary-graph against summary-sequence so event aggregation does not confound topology. If relation labels are reconstructible and G2 performs similarly, describe any benefit as structured parameterization, not new clinical information.

## E2: Event-resolution, timing and relation ablations

Hold graph input membership fixed when ablating time encoding. Test no time attributes, shared time function, and relation-specific time function with matched capacity. Record whether topology still reveals ordering; removing time attributes does not make an ordered graph atemporal.

Separately compare raw event instances to time-binned sums under both graph and sequence families. Supply identical bin widths and summary definitions. These comparisons distinguish fine temporal resolution from graph effects.

For the current event-to-CGM message-sum architecture, shuffling event-token
rows is invariant to the model's sum aggregation and is not an informative
order control. A post-hoc fixed-checkpoint event-age reassignment instead
preserves the per-window event and age multisets but breaks event-to-time and
derived-endpoint pairing. Across five epoch-1 outer-fold checkpoints for each
of two seeds, original-minus-reassigned AP is positive in all ten fits (mean
fold-seed difference +0.0001118), but only 3/10 fold-specific participant
intervals exclude zero. Macro-Brier direction is evenly split (5/10 positive;
4/10 intervals exclude zero). The same 652 participants recur across seeds,
so these are not ten independent observations and intervals must not be
pooled. The consistency supports a small fixed-fit sensitivity to the event-
time pairing under one deterministic age rotation. It does not establish
temporal-relation value, explanation faithfulness, causal validity, or clinical
utility. See the [control report](loop_event_age_reassignment_control.md)
and [two-seed summary](../audit/loop_event_age_reassignment_two_seed_five_fold_summary_20261029.json).

Remove insulin/meal/activity only as modality analyses, not proof of relational semantics. Removing all edges also changes receptive fields and connectivity; describe this as a structural intervention. A fixed permutation of relation names preserves information and is a sanity check, not a semantic corruption experiment.

## E3: Reporting-availability sensitivity

Eligibility and labels stay fixed across imposed event-delay scenarios so changes in the evaluated cohort do not masquerade as robustness. Restrict the initial experiment to auxiliary event reporting delays while retaining the CGM-based eligibility contract. CGM acquisition latency would require a separate stale-reading eligibility protocol.

For an event at τ, impose arrival a=τ+d. Start with development-frozen d in {0, 15, 30, 60} minutes for meals and self-reported exercise, each separately and together. These values are stress scenarios, not estimates of real logging behavior. For naturally observed arrival times, use those instead and report their empirical distribution. Do not change occurrence time to simulate reporting latency; timestamp error is a separate experiment.

| Condition | Training | Evaluation input | Interpretation |
|---|---|---|---|
| Immediate-record reference | Immediate availability assumption | Immediate record set | Retrospective optimistic reference, not deployable evidence when actual arrivals are unknown. |
| Delayed replay | Immediate or measured training arrivals | Only events with a<=t | Sensitivity to delayed inputs; all model families see the same replay. |
| Delay-trained replay | Development-defined delay augmentation | Same delayed replay as above | Tests adaptation to the specified delay regime, not an oracle advantage. |

For each model m and scenario d, report AP(m,d), Brier score, episode sensitivity and false-alert burden. Freeze calibration and alert thresholds from the applicable validation regime. Report any regime-specific recalibration as an additional analysis.

The graph-specific question is the interaction:

```text
I(d) = [AP(G1,d) − AP(B4,d)] − [AP(G1,0) − AP(B4,0)]
```

Use paired participant resampling for its uncertainty; a large decline in every model is not a graph improvement. The paired shift AP(m,0)−AP(m,d) is scenario sensitivity, not a causal effect of reporting policy on patient outcomes. Do not train the graph on withheld events while making the baseline operate causally.

A fixed delay may be perfectly inferable from event type; learning that constant does not demonstrate a useful second clock. Compare models with and without reporting-lag attributes on the same admissible event set. If mixed-delay scenarios are added, define distributions and seeds before testing and give all models identical lag metadata.

Gate: without measured arrival timestamps, all results are explicitly simulated availability scenarios. No claim of real-world latency robustness.

## E4: Explanation integrity and fidelity

Test explanations only for frozen models using identical sampled cases. Record both raw-event deletion and message-edge masking, as they answer different questions. Upon raw-event removal, rebuild all dependent aggregates and topology; otherwise residual information can invalidate the experiment.

For each event set S, report p(G)−p(G without S), p(G)−p(G retaining S and required context), size, connectivity validity and matched-random differences. Do not select only positively influential events and then assume all probability changes will be positive. Retain low-risk explanations and errors in the sample.

Provenance checks: every displayed value corresponds to its version at t; no future outcome is cited; no unavailable event appears; the rendered evidence set matches the perturbed set. These are correctness checks, not evidence of clinical usability. Compare rank/set stability across seeds and prespecified admissible perturbations with the information set held fixed.

An explanation after receipt of a late record may validly differ from the previous explanation. Evaluate this as information revision, not automatically as instability. Blinded clinician review remains separately required for usability claims.

**Exploratory screen completed, 29 October 2026:** one outer-0, seed-20261005,
epoch-1 graph-generic checkpoint was audited on 518 hash-selected windows
across 130 participants. Top-three events were selected by single-event
deletion sensitivity and compared with random sets matched on size and
modality for joint deletion and retention. Top sets showed larger joint
deletion sensitivity and closer retained predictions, but selection used the
same deletion measure, so the deletion comparison is selection-conditioned.
This does not meet the independent attribution/perturbation design above and
does not establish clinical faithfulness. See the
[exploratory report](loop_graph_event_explanation_faithfulness.md) and
[aggregate artifact](../audit/loop_graph_event_explanation_faithfulness_outer0_seed20261005_20261029.json).

## E5: External validation and adaptation

Freeze all source-derived choices before external outcomes are exposed. Compare common-field versions of B2/B4/G0/G1/G2 on the external cohort. Any mapping-informed architecture changes must be trained and selected on source/development data. Report direct transfer separately from calibration or fine-tuning using separate external participants/blocks.

If no compatible external dataset is available, retain the internal study and limit claims. Do not describe different held-out participants within OhioT1DM as external validation.

## Results-to-claims map

| Observed pattern | Supported conclusion |
|---|---|
| G1 beats B2 but not B4 | Exact event representation may explain the advantage; graph superiority is unestablished. |
| G1 beats G0 but not G2 | Relation-specific parameterization may help; extra relation information is unestablished. |
| G1 beats matched controls with stable participant effects | Evidence for relational inductive bias under this cohort and protocol. |
| Advantage exists only with immediate retrospective records | Benefit is sensitive to optimistic availability assumptions. |
| Prediction similar, explanation fidelity stronger | Computational explanation advantage; clinical usability still unproven. |
| Wide intervals or few informative participants | Inconclusive, not equivalent and not superior. |
| No useful gain after matched controls | Negative evidence for the proposed benefit; retain and report the result. |

Avoid interpreting nonsignificance as equivalence. Any noninferiority margin, practical improvement threshold or confirmatory multiplicity procedure must be fixed before test evaluation with domain/statistical input.
