# Refined research proposal v0.2

Date: 10 September 2026. Status: research design, not empirical validation. Supersedes broad novelty statements in the starter handbook. Read alongside the [prior-work assessment](novelty_assessment.md) and [operational protocol](research_protocol.md).

## Working title

**When Do Temporal Patient Knowledge Graphs Help Hypoglycemia Prediction? A Controlled Study of Clinical Event Relations and Information Availability in T1D**

Keep T1D-TKG as the project identifier. This title states the question without presupposing graph superiority. A later result-specific manuscript title can follow the evidence.

## Problem and rationale

CGM, insulin delivery, meals and activity can be represented as sequences, modality summaries, or individual clinical events in a graph. Existing semantic and temporal graph work already motivates these representations. What this project will test is whether individual-event relations provide useful inductive bias when competitors receive the same information and are evaluated on the same advance-warning task. It will also test whether a displayed explanation refers only to records that could have been used at prediction time.

The specific opportunity is an empirical decomposition of representation value, rather than treating the introduction of a KG as the result. The [prior-work assessment](novelty_assessment.md) documents why each component alone is insufficient and which comparisons are needed.

## Research questions and hypotheses

| Question | Hypothesis to test | What would contradict it? |
|---|---|---|
| RQ1: Does an individual-event graph help on unseen participants? | Its 30-minute participant-macro AP exceeds the matched multimodal GRU and remains competitive with a strong event-sequence comparator. | Gains disappear against information-matched sequences or are too uncertain. |
| RQ2: Which representation feature matters? | Relation-specific message passing contributes beyond event resolution, temporal features and parameter count. | A generic graph or capacity-matched sequence explains the gain. |
| RQ3: Is relational benefit preserved when information arrives late? | Some benefit remains when all models use the same admissible records. | Gains occur only under optimistic retrospective availability. This hypothesis is secondary and conditional on a valid delay study. |
| RQ4: Do graph explanations trace faithful event evidence? | Important event sets outperform matched random sets under both deletion and retention, without unavailable or stale-derived evidence. | A plausible path has weak predictor fidelity, poor stability or invalid provenance. |

External transport is a planned validation stage. Personalization is a separate experiment, not implicit evidence from a Patient node. If actual reporting metadata cannot be obtained, RQ3 becomes a clearly labeled sensitivity study of assumed delays.

## Proposed contributions

1. A versioned patient-event representation and benchmark that separates event-instance resolution, relation typing, temporal features and information availability under patient-disjoint prediction.
2. Controlled evidence about whether and when clinical event relations add value beyond matched sequence, generic event-graph and physiology-summary representations.
3. Prediction-specific event explanations with traceable input versions, valid feature recomputation and quantified fidelity/stability.

These are intended outputs. A result may refute the benefit hypothesis while still answering the questions. A new ontology, neural architecture or clinical discovery is not promised.

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

A clinically explicit meal–bolus link is permitted only when source data supplies one or a clearly labeled, development-frozen heuristic is being tested. Do not create false clinical knowledge to make the graph appear richer. If such extra relations are introduced, supply them to the event-sequence comparator as well.

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
