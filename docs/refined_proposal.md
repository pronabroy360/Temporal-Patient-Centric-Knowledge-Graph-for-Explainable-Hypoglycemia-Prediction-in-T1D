# Refined research proposal v0.3

Date: 18 October 2026. Status: research design, not empirical validation. Supersedes broad novelty statements in the starter handbook and v0.2. Read alongside the [prior-work assessment](novelty_assessment.md), [SysCon methods review](syscon_2026_prior_work_review.md), and [operational protocol](research_protocol.md).

## Working title

**Timestamped Treatment-Event Representations for Incident Hypoglycemia Prediction in T1D: A Patient-Disjoint Comparison of Graphs, Sequences, and Modality Summaries**

Keep T1D-TKG as the project identifier. This title states the question without presupposing graph superiority. A later result-specific manuscript title can follow the evidence.

## Problem and rationale

CGM, insulin delivery, meals and activity can be represented as sequences, modality summaries, or timestamped event instances connected to CGM history. Prior work already includes patient-specific semantic T1D graphs, temporal graph forecasting, physiology-typed multimodal graphs, and graph-structure faithfulness diagnostics. Dave et al. (2021) already compare short-horizon hypoglycemia prediction with and without engineered insulin/carbohydrate context; the source abstract/body discrepancy means its 30-minute effect should not be stated definitively without table reconciliation. Meal-anchored postprandial prediction and aggregate carbohydrate-on-board nocturnal-risk models also predate this work. The October 2026 Khokhar et al. preprint evaluates an any-future-CGM-below-70 outcome at 30 minutes with patient-disjoint outer folds, multimodal-versus-sequence controls, and explanation perturbation checks; its stated covariates do not include raw insulin/meal transaction events or graph relations. Thus, the endpoint, horizon, patient split, use of event-derived context, multimodal model comparison, and explanation evaluation are not novelty claims. The candidate contribution is narrower: a patient-disjoint, information- and timing-matched comparison of raw event-instance relations against equally informed event-aware non-graph and summary encodings, with current Loop results favoring non-graph pooling. This remains a candidate empirical contribution rather than a demonstrated graph advantage.

The specific opportunity is an empirical decomposition of representation value, rather than treating the introduction of a KG as the result. The [prior-work assessment](novelty_assessment.md) and [focused prior-art review](targeted_prior_art_search_2026_10_31.md) document why each component alone is insufficient and which comparisons are needed. The literature matrix currently contains 70 unique records; review remains targeted rather than systematic. Li, Ge & Chen (2020) already use event-order relations in a dynamic KG over diabetes event streams, but do not report hypoglycemia-risk prediction results on those diabetes data. Zecchin et al. (2016) and Apicella et al. (2026) also make context inclusion and representation comparisons established topics. The candidate is therefore a narrow result about event-instance relation utility under matched controls, not graph construction or contextual-input novelty. Acharya and Lee (2014) already construct temporal causal relations over diabetic event instances including insulin, glucose and hypoglycemic symptoms; Li et al. (2020) also use event-order KG relations on diabetes logs. The project cannot claim the representation itself is new. A PubMed-indexed 2026 review and a recent OhioT1DM/SMARTDIAB attention-LSTM study further confirm that contextual inputs and interpretable multimodal T1D risk prediction are established; the distinction remains the matched event-relation test, not those ingredients.

## Research questions and hypotheses

| Question | Hypothesis to test | What would contradict it? |
|---|---|---|
| RQ1: Does representing timestamped insulin/food event instances improve 30-minute incident-low prediction on unseen participants over the same event information encoded as sequences or modality summaries? | A patient-macro AP or calibration advantage persists in matched, patient-disjoint development comparisons and is not an artifact of extra information, split, or capacity. | The advantage disappears against an information-matched sequence, generic graph, or summary-sequence control, or is too uncertain. |
| RQ2: Does modality-derived typed message routing contribute beyond generic message passing and endpoint/time-reconstructible controls? | Typed routing improves the preregistered metric under equal inputs, training budget, initial weights, and capacity, and the result replicates. | Generic routing or reconstructed endpoint/time features explain the result. |
| RQ3: Is any observed representation advantage preserved when event availability is delayed? | The relative advantage persists when every model receives the same admissible records. | Gains occur only under optimistic retrospective occurrence-time replay. This is secondary and requires measured arrival metadata or explicitly simulated scenarios. |
| RQ4: Do event-level explanations faithfully trace prediction evidence? | Recomputed event deletions/retentions have greater fidelity than matched random sets, with valid provenance and adequate stability. | A plausible path has weak predictor fidelity, poor stability, or invalid provenance. Graph explanations themselves are established prior work. |

External transport is a planned validation stage. Personalization is a separate experiment, not implicit evidence from a Patient node. If actual reporting metadata cannot be obtained, RQ3 becomes a clearly labeled sensitivity study of assumed delays.

## Proposed contributions

1. A versioned Loop benchmark that separates timestamped event-instance resolution, modality aggregation, sequence encoding, message routing, and availability assumptions under patient-disjoint prediction.
2. Controlled evidence about whether and when event-instance representations or typed message-passing inductive bias help beyond matched sequence, generic-edge graph, endpoint/time, and modality-summary controls.
3. Prediction-specific event explanations with traceable input versions, valid feature recomputation and quantified fidelity/stability.

These are intended outputs. A result may refute the benefit hypothesis while still answering the questions. A new ontology, neural architecture, physiological relation taxonomy, or clinical discovery is not promised; the novelty candidate is a controlled empirical result, if supported.

## Empirical status update — 19 October 2026

The first exact-capacity graph-versus-non-graph sequence comparison is complete
on Loop outer-0, seed `20261003`, for one epoch. Graph-generic exceeded the
36,883-parameter dual-GRU sequence control on participant-macro AP (0.474481
vs 0.389901; paired difference +0.084580, 95% participant-bootstrap interval
[+0.078104, +0.090816] from 10,000 draws) and Brier (0.021522 vs 0.024211;
95% interval [−0.003043, −0.002347]). Predictions were
strictly paired on all 8,885,621 validation windows. This supports continuing
the controlled graph-integration question, but it does not resolve whether
timestamped event instances outperform modality summaries, nor whether
clinically typed relations add beyond generic graph connectivity. The
typed-versus-generic pilot slightly favored generic routing. Both are single
fold/seed screening results and require prespecified replication before a
confirmatory claim. The locked holdout remains unopened. See the [capacity-
matched comparison](loop_non_graph_capacity_matched_control.md) and [paired
audit](../audit/loop_graph_vs_capacity_matched_outer0_paired.json), with the
[10,000-draw sensitivity audit](../audit/loop_graph_vs_capacity_matched_outer0_paired_10000draws_20261019.json).

## Formal information contract

Let an event-field version v have occurrence time τ(v), first usable time a(v), source identifier and a value. At prediction index t, an admissible point observation satisfies τ(v) <= t and a(v) <= t. For a field revised later, select its most recent admissible version, not the latest version in the eventual database export. The known event set is D(t); build G(t)=B(D(t)) using a deterministic builder B.

For an interval, only known fields are used: an announced planned end and an observed completed end have different meanings. Elapsed duration is calculated as of t. Future completion measurements cannot enter earlier predictions. A late-reported old event may enter a later graph with its original occurrence time, provided it remains inside the configured history support; previously issued predictions are never rewritten.

The basic invariance requirement is:

```text
If D and D' contain identical admissible field versions at t,
then B(D,t) = B(D',t), regardless of their future records.
```

This follows from restricting the builder's dependencies; it is a software correctness property, not a new theorem. Provenance timestamps used for record extraction must not accidentally become future-information features.

An event's known age t−τ and known reporting lag a−τ can be distinct predictive attributes if a is observed. For unreported events, the model cannot know that an event exists or how late it will arrive. Never provide a synthetic per-event “missing” flag that reveals a withheld event.

## Representation and predictor

Use individual CGMReading, InsulinEvent, MealEvent and optional ExerciseEvent instances, with a PatientContext node containing only admissible context. Quantities stay as attributes. Relations record ownership, temporal adjacency and type-specific preceding/active events. Keep outcomes outside the input graph. The [schema](graph_schema.md) defines this initial candidate.

Start with a small relation-aware encoder, elapsed-time edge attributes and a GRU over historical CGM embeddings. This deliberately uses established components. Add a dual-time attribute variant only if availability metadata or a labeled sensitivity scenario supports it. A two-time input is not called a new graph architecture.

Audit whether relation identity can be reconstructed from endpoint types and time. For example, insulin→CGM with prior_insulin may add no relation information beyond those node types and timestamps. Generic-relation ablation alone cannot establish a rich clinical semantics claim. Add an explicit comparator that reconstructs relation features from endpoints and time. If all relations are deterministic in that way, report relation-specific inductive bias and test the architecture against that comparator.

A clinically explicit meal–bolus link is permitted only when source data supplies one or a clearly labeled, development-frozen heuristic is being tested. Do not create false clinical knowledge to make the graph appear richer. If such extra relations are introduced, supply them to the event-sequence comparator as well. The current generic-vs-typed pilot uses a relation ID deterministically derived from event modality and time ordering; it tests message-passing parameterization, not additional clinical information.

## Data and feasibility

The primary cohort will be selected using the [access and field gate](dataset_fallback_strategy.md), rather than fixed in advance. The researcher reports being ineligible to submit the OhioT1DM DUA directly; OhioT1DM is therefore conditional on a supervising advisor submitting as the eligible institutional employee. If obtained, its published schema describes self-reported meal/exercise timing and insulin intervals but does not establish a separate first-usable timestamp for every field. It also notes a placeholder patient weight of 99, which must not be used as a measured phenotype. [Dataset description, section 3](https://webpages.charlotte.edu/rbunescu/data/ohiot1dm/bglp/OhioT1DM-dataset-paper.pdf).

Do not make the whole thesis depend on unverified reporting metadata. Proceed in two tracks:

- Core representation benchmark with explicitly stated source-availability assumptions.
- Availability study using real entry/upload timestamps if verified; otherwise use imposed delays and claim only scenario sensitivity.

The supplied Jaeb releases have now been screened. Loop is the provisional primary cohort because 835 participants occur in its CGM, basal, bolus and nonempty-food sets. DCLP3 and DCLP5 are insulin–CGM replication candidates because their Roche carbohydrate fields are empty; FLAIR and AIDE are CGM/treatment-context candidates. The [Loop audit](loop_release_audit.md) also identifies device-upload UTC metadata that may support an observed availability-time analysis after linkage and validation. T1DEXI remains conditional on study-specific approval. No equivalence among cohorts is assumed. All substantive data counts, events, precision assessments and subgroup feasibility are determined by release-specific audits.

## Evaluation and explanation

Retain the revised protocol's 30-minute primary task, 60-minute secondary task, non-low/recovered prediction eligibility, complete-future label rule, nested patient-disjoint validation, calibration and episode alerts. Run identical windows and folds across models; do not compare published headline scores as if they were obtained on this task.

The [experiment specification](decisive_experiments.md) separates model effects and input-availability effects. The primary comparison remains the full graph versus multimodal GRU. An event-sequence comparator, generic graph and endpoint-derived relation control must also be reported before asserting relational value.

Explanation records contain the prediction index, model/configuration version, source event IDs, values actually used, admissible field versions and mask definition. Deleting an event recomputes its aggregates and graph edges. Repeated predictions after a late entry have different information sets; explanation changes between them are not automatically instability. Compare stability only under stated, information-matched perturbations.

## Decision rules

Proceed to large experiments only after labels, source clocks, modality capture and train/test separation are auditable. If only summary features are reliably available, explicitly conduct a summary-graph comparison rather than claiming an event-instance method.

If prediction gains disappear after input/capacity matching, reject the benefit hypothesis. If gain comes from precise timestamps alone, credit temporal resolution. If relations help but explanations fail, narrow claims to prediction. If faithful explanations are the only advantage, evaluate their usability separately and do not infer clinical benefit. If actual latency data are absent, remove any claim of empirical real-world delay validation.

No fixed calendar deadline applies. Completion is determined by the evidence gates, reproducibility and the limits of the data.
