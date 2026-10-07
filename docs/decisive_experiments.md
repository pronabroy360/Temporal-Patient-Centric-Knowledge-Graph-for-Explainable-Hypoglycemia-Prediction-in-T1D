# Decisive experiments and claim boundaries

Date: 10 September 2026. All experiments below are **specified, not run**. Freeze their exact configurations on development data before final evaluation. The [research protocol](research_protocol.md) governs labels, splits and metrics.

Execution status has advanced since this specification: corrected CGM
development evaluation and the first negative recorded-event summary comparison
are complete. The current ordered implementation gates are maintained in
[Next research steps after the recorded-event summary result](next_steps_after_event_summary.md).

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
| B4 | Event-sequence model using individual events, values, types and exact admissible times | Control for loss of event resolution during gridding. |
| B5 | Time-neighborhood GNN | Match the temporal graph family without claiming exact GAT-BiGRU reproduction. |
| B6 | Fixed modality-summary physiology graph | Test individual events against physiology-inspired summary graphs. |
| B7 | Visibility graph on CGM | Relevant CGM-only reference; compare against the CGM-only subset of other models. |
| G0 | Individual-event graph, shared/generic edge transform | Control event resolution and topology. |
| G1 | Same graph, relation-specific transforms | Main typed-graph candidate. |
| G2 | Same graph, edge representation derived from endpoint types and time | Test whether relation labels contribute beyond reconstructible descriptors. |

All full-modality models receive the same admissible records and engineered summaries. If B6 compresses events into summaries, compare it to a summary-only sequence control as well; otherwise a G1−B6 difference confounds graph design with information loss. If exact reproduction is unavailable, label the implementation as an adaptation and list the departures.

Match training/search budgets and report parameter counts and learning curves. Compare width-adjusted G0/G1 models and a sequence model of similar capacity. Use at least three fixed seeds, paired folds and participant-level intervals. A result favoring G1 over B2 alone is insufficient for a semantic-value claim.

Primary prespecified contrast: AP(G1)−AP(B2), at 30 minutes. Key mechanistic contrast: AP(G1)−AP(G0). Required interpretive controls: G1 versus B4 and G2; summary-graph versus summary-sequence control. If relation labels are reconstructible and G2 performs similarly, describe the benefit as structured parameterization, not new clinical information.

## E2: Event-resolution, timing and relation ablations

Hold graph input membership fixed when ablating time encoding. Test no time attributes, shared time function, and relation-specific time function with matched capacity. Record whether topology still reveals ordering; removing time attributes does not make an ordered graph atemporal.

Separately compare raw event instances to time-binned sums under both graph and sequence families. Supply identical bin widths and summary definitions. These comparisons distinguish fine temporal resolution from graph effects.

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
