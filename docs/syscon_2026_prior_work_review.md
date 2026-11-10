# Prior-work review: Sarwar et al., SysCon 2026

**Reviewed:** 18 October 2026  
**Purpose:** Verify the closest overlap between the SysCon paper and this project's proposed patient-event relation study. This note supplements, but does not replace, the main novelty assessment.

## Sources and verification scope

The methods review uses the full manuscript uploaded by first author Muhammad Abdullah Sarwar to ResearchGate. The page labels the file “Author content” and records the upload date as 8 May 2026. The manuscript front matter identifies the title, six authors, the 2026 IEEE International Systems Conference, and DOI `10.1109/SysCon66367.2026.11503533`. This is primary author content, but it is not a version comparison against IEEE's final typeset copy. The [IEEE Xplore record](https://ieeexplore.ieee.org/document/11503533) is the publisher record for that DOI; its content could not be independently read in this review because the page required a JavaScript/robot check. The [official SysCon 2026 site](https://2026.ieeesyscon.org/) and [conference program](https://confcats-siteplex.s3.us-east-1.amazonaws.com/syscon26/syscon25_program_grid_web_01_bb5fa5af90.pdf) independently identify the event as the 20th Annual IEEE International Systems Conference, scheduled for 6–9 April 2026 in Halifax.

Primary methods source: [Sarwar et al., author-uploaded full manuscript](https://www.researchgate.net/publication/404642556_Explainable_Multitask_Graph_Network_for_Blood_Glucose_Forecasting_and_Hypoglycemia_Risk_Classification). Publication identifier: [IEEE Xplore record, DOI 10.1109/SysCon66367.2026.11503533](https://doi.org/10.1109/SysCon66367.2026.11503533).

## What the manuscript specifies

| Topic | Verified description in the manuscript |
|---|---|
| Cohort and inputs | BrisT1D; CGM/glucose, insulin, carbohydrate intake, heart rate, activity, steps, calories, and circadian context. |
| Graph | A stable directed seven-node topology: insulin→glucose, heart-rate→glucose, carbohydrates→glucose, activity→heart-rate, steps→activity, and calories→activity, plus self-loops. The paper says it creates a graph for each patient and sequence index, with time-varying node attributes. |
| Temporal representation | Historical signals are summarized over a fixed past window. The manuscript describes per-node summaries such as glucose level/range/slope, heart-rate summaries, insulin and carbohydrate sums, activity code, and time-of-day features. Thus the observed formal construction is a sequence of graph instances with changing node features on a fixed topology. Although its contributions bullet says “temporal and physiologic edge types,” the methods equations define the stable physiological adjacency and do not specify a separate temporal edge type or a time-varying edge-generation rule. |
| Model and tasks | Two-layer, four-head GATv2 with shared graph embedding and two output heads: future glucose regression and binary hypoglycemia classification. It describes prediction steps at 5, 15, and 30 minutes, with glucose regression and a classification label derived from the corresponding future glucose value. |
| Label and censoring | The classification target is `1` when the single future glucose target is below 3.9 mmol/L and `0` otherwise. Rows without a valid future glucose target are dropped. The paper therefore evaluates point-threshold status at a future step, not whether a new low occurs at any point within a future interval. |
| Explanatory/structural diagnostics | The results section reports node ablations; deletion of high-attention edges compared with random or least-attended deletions; edge reinsertion; random-edge-drop experiments; and correlation between attention and the specified physiology priors (`ρ = 0.90`). These are already graph-structure reliance/faithfulness-style diagnostics. |

The basis for these entries is the manuscript's sections on temporal aggregation and targets, graph construction, training/evaluation, and “Graph Diagnostics and Structural Insights.” The manuscript reports performance values, but they should not be compared directly with this project's Loop results because cohort, labels, data processing, split, and metric setup differ.

## What is and is not established about its evaluation

The manuscript says BrisT1D was divided into “80% training, 20% validation, and a held-out test set,” and says hypoglycemic labels were stratified. That wording does not state the split unit (participant, day, sequence, or row), the held-out test fraction, whether adjacent/overlapping windows can cross partitions, or whether held-out test results informed model selection. The percentages as written also do not explain how the held-out test set fits alongside 80% training and 20% validation. Therefore, participant-disjointness and temporal leakage protection are **unverified**, not demonstrated absent. The paper's own limitations also say evaluation is focused mainly on BrisT1D and calls for larger-scale validation and real-time/prospective evaluation.

The manuscript lists “attention flow, counterfactuals, prototype retrieval” in its contribution bullets. In the methods/results text reviewed here, the diagnostics concretely described are attention visualizations and graph/node/edge perturbations. This review did not find sufficient operational details or reported results to treat counterfactual and prototype explanations, or explanation stability, as verified implemented analyses. Likewise, the paper mentions calibrated probabilities in a contribution bullet and reports Brier scores, but this review did not find a calibration procedure sufficient to characterize how calibration was performed. These are verification limits, not claims that the authors did not implement them elsewhere.

## Exact overlap with the current project

The project cannot claim novelty for any of the following in isolation:

- a graph for T1D glucose or hypoglycemia prediction;
- multimodal CGM, insulin, food/carbohydrate, and activity inputs;
- physiological/typed relations such as insulin→glucose or activity→heart-rate;
- time-varying graph inputs or temporal context;
- GAT-based prediction; or
- node/edge ablation and graph perturbation used to test structural reliance or explanation faithfulness.

The narrower distinction still visible in the reviewed methods is **representation granularity and the matched empirical question**. SysCon represents insulin, carbohydrates, and activity as modality-level nodes carrying window-aggregated values on a fixed physiology graph. The current Loop proposal represents individual timestamped basal, bolus, and food records as event instances linked into each prediction's CGM history, then asks whether relation-aware routing helps when the same captured events, history, timing, participant split, and model capacity are held fixed. That distinction is supported by the descriptions inspected; it does **not** establish that no other paper has tested event-instance graphs.

Even this wording needs care: if edge type is deterministically recoverable from event modality and endpoint/time attributes, the experiment tests whether a typed message-passing inductive bias helps, not whether the graph supplies new clinical facts or additional information. The pilot currently proposed in this repository compares modality-derived typed routing against generic routing on Loop; it is a relation-parameterization test, not a replication or head-to-head evaluation of SysCon's BrisT1D model. Any reported benefit must also survive an information-matched sequence baseline and same-architecture ablations before it supports a substantive relation claim.

## Narrowest defensible novelty statement

Use this only as a **candidate study contribution**, not as a proven “first” claim:

> We conduct a patient-disjoint, information- and capacity-matched study of whether representing recorded insulin and food transactions as timestamped event instances with typed links to CGM history improves prediction of incident hypoglycemia within a prespecified future horizon, compared with modality-summary, generic-event-graph, and sequence representations.

The distinction is the controlled empirical comparison, dataset/task specification, and event-instance granularity—not the existence of patient-centric graphs, temporal graph learning, physiological relations, explainability, or graph faithfulness tests. The endpoint must be described exactly as implemented. A future-point threshold target such as SysCon's is not interchangeable with an “any new low during the next 30 minutes” incident label.

Before elevating this to the paper's novelty claim:

1. Execute and preserve the relation-type pilot with verified inputs and an independent prediction/metric audit.
2. Compare typed and generic relations with identical event instances, timestamps, CGM information, training windows, parameters, and participant splits.
3. Include an information-matched non-graph event-sequence model and an endpoint/time-derived relation control; do not interpret modality-derived edges as extra clinical knowledge.
4. Replicate across seeds and patient-disjoint folds, report participant-level uncertainty and calibration, and keep the locked holdout unopened until model selection is frozen.
5. Complete a broader search and inspect the final IEEE version/supplement if accessible. This one close paper review cannot prove global novelty or absence of an equivalent event-instance study.

## Bottom-line assessment

SysCon 2026 substantially overlaps the project's broad motivation and removes any defensible claim to be first in multimodal physiology graphs or graph-relation explanation for T1D hypoglycemia. It does not, in the inspected formal construction, model each insulin/food record as a distinct event node; its inputs are temporally windowed modality summaries attached to fixed modality nodes. A carefully controlled event-instance-versus-summary/sequence study remains a plausible empirical distinction, but the study is not complete and its novelty is provisional. No graph-relation benefit or faithful explanation is established by this prior-work review.
