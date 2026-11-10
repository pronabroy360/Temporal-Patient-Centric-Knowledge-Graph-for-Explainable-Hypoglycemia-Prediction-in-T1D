# Primary-source novelty check (31 October 2026)

## Purpose and scope

This note checks the closest overlap claims against original papers, publisher
records, and the institutional project page. It is a focused verification,
not a systematic review and not evidence that no additional related work
exists. It supplements the [29 October primary prior-art update](primary_prior_art_update_2026_10_29.md)
and [SysCon methods review](syscon_2026_prior_work_review.md). The previously
reported second-seed experiment is now complete; stale status text has been
corrected.

## Event-aware T1D prediction and sequential-pattern precedents

Ma et al. use CGM, meal, and insulin time series to build a multidimensional
sequence database, mine hypoglycemia patterns with UniSeq, and issue early
alarms by pattern matching on OhioT1DM. Their abstract reports sensitivity
75.76%, precision 75%, F1 75.38%, and 25.17 minutes mean early warning. This
means multimodal temporal patterns over glucose, meals, and insulin are prior
work; a claim that this project is the first to combine these streams for
hypoglycemia warning is untenable. Their approach is sequential-pattern
mining, not an event-instance knowledge graph, and the accessible abstract
does not establish a same-information, same-capacity relation ablation.
[PubMed record and abstract](https://pubmed.ncbi.nlm.nih.gov/36387535/)
· [Full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC9647441/)

Zhu et al.'s ARISES study combines CGM, daily meal and bolus-insulin entries,
and wearable physiology in an attention-based recurrent model for glucose
prediction and hypo-/hyperglycemia warnings; it reports a 60-minute horizon
and a 12-adult, six-week study. Its chronological evaluation and deployment
work show that personalized multimodal prediction, wearable context, and
real-time warnings also predate this project. It does not test event-instance
graph relations. The study's data are proprietary, and its small cohort limits
direct benchmark comparison. [npj Digital Medicine article](https://www.nature.com/articles/s41746-022-00626-5)
· [Full text record](https://pmc.ncbi.nlm.nih.gov/articles/PMC9237131/)

Athanasiou et al. combine CGM, insulin, and meal information from 12 people
with T1D with an insulin-signaling mathematical model and tree-based models
with TreeSHAP. The PubMed abstract reports risk windows of 0–30 and 30–60
minutes. This is further precedent for personalized, interpretable,
event-aware hypoglycemia risk prediction, but not a KG or a matched event-
relation ablation; split and event-availability details remain unverified
from the abstract. [PubMed abstract](https://pubmed.ncbi.nlm.nih.gov/40039236/)

These works constrain the framing but are not direct replications of this
Loop study: datasets, labels, model capacities, and evaluation designs differ.
The candidate distinction is specifically the incremental value of relations
among timestamped event instances against aligned non-graph controls with
identical inputs and protected splits.

## Verified closest overlaps

### ESWC 2024: patient-specific semantic KG for T1D hypoglycemia

The official proceedings PDF is titled *Enhancing Hypoglycemia Prediction in
Type 1 Diabetes through Semantic Knowledge Integration and Machine Learning
Optimization* (Onwuchekwa, Weber, and Maleshkova). It explicitly proposes
patient-specific and evidence-based knowledge graphs, ontologies, graph
embeddings, and ML for T1D hypoglycemia. The paper says that the work is in an
early stage; its future work includes real-world validation, scalability, and
generalizability. Its preliminary numerical table is a glucose-prediction
comparison on one MIMIC-III patient, while much of the KG/model evaluation is
described as a plan. It therefore rules out novelty of the broad semantic,
patient-specific KG framing, but does not establish a completed prospective
outpatient event-instance benchmark or a matched graph-relation ablation.
[Official ESWC paper PDF](https://2024.eswc-conferences.org/wp-content/uploads/2024/05/77770363.pdf)

### Scientific Reports 2024: de Bruijn graph for pediatric hypoglycemia forecasting

Cakiroglu et al. discretize CGM readings into glucose-state symbols and use an
extended de Bruijn graph to forecast pediatric hypoglycemia within
approximately 30 minutes. The article reports 15 pediatric patients and
leave-one-out evaluation. This is a direct precedent for graph-based
hypoglycemia forecasting and a short horizon, but its graph is a symbolic
glucose-sequence graph rather than a graph connecting recorded insulin/meal
transactions to CGM history. It does not establish this project's matched
event-relation comparison.
[Nature publisher article](https://www.nature.com/articles/s41598-024-82649-4)
· [PubMed record](https://pubmed.ncbi.nlm.nih.gov/39732907/)

### Frontiers 2023: retrospective hypoglycemia cause classification

Zaitcev et al. used self-care histories, insulin, food, activity, and temporal
features to classify patient-labeled reasons for prior hypoglycemia episodes
in 54 people with T1D. This overlaps context-aware interpretation and
behavioral explanation, but it classifies causes after a recorded episode
rather than predicting future incident risk or evaluating graph-message
passing.
[Frontiers article](https://www.frontiersin.org/journals/clinical-diabetes-and-healthcare/articles/10.3389/fcdhc.2023.1095859/full)

### S+SSPR 2024 / Springer 2025: graph neural network for hypo events

Hüni, Garcia-Tirado, and Riesen compare LSTM and graph-attention models for
advance hypoglycemia-event prediction from CGM in 37 people with T1D. Although
the final Springer chapter remains subscription-only, the University of Bern
hosts Hüni's 2024 bachelor thesis, a detailed author-work predecessor with
methods and results. Do not assume the thesis and final chapter are identical.

The thesis uses only CGM readings and timestamps, sampled at five-minute
intervals. It defines positives as any glucose value below 70 mg/dL within the
future horizon and evaluates 30-, 60-, and 120-minute CGM windows against
15-, 30-, and 60-minute horizons. Thus it includes the same 120-minute-history,
30-minute-horizon endpoint family as this project. Its GAT operates on natural
visibility graphs whose nodes are CGM values with sequence position and whose
edges encode visibility and distance; it does not represent individual insulin
or meal transactions. At 120 minutes of history and 30 minutes ahead, the thesis
reports mean F2 of 0.348 for LSTM and 0.409 for GNN across the 37 patient
datasets.

The thesis trains a separate model for each patient dataset, window, and
horizon. It splits each patient's ordered samples 70/30, using the first 70%
for training and the last 30% for validation. This is chronological
within-person validation, not a patient-disjoint unseen-person test. The
reported LSTM/GAT comparison is not documented as parameter-matched. It
therefore rules out a broad “first graph-versus-sequence comparison” or “first
graph for T1D hypoglycemia-event prediction” claim, but does not answer whether
timestamped clinical-event relations help under patient-disjoint, same-input,
capacity-matched conditions.

[Official University of Bern thesis PDF](https://prg.inf.unibe.ch/wp-content/uploads/2024/08/BA_FabianHuni.pdf)
· [Author dataset repository and label specification](https://github.com/fabianHueni/cgm-visibility-graph-dataset)
· [Springer publisher chapter](https://link.springer.com/chapter/10.1007/978-3-031-80507-3_6)

### 2026 JAMIA: temporal graph hypoglycemia prediction and explanation

The OUP publisher abstract and PubMed record for Sarwar et al., *GAT-BiGRU:
explainable multi-task temporal graph learning for glucose forecasting,
hypoglycemia risk, and counterfactual insulin adjustment*, describe 30- and
60-minute hypoglycemia risk, feature-enriched CGM time-point nodes in a
temporal k-neighborhood graph, OhioT1DM and BrisT1D evaluation, and
GNNExplainer. The OUP supplementary DOCX was also retrieved and inspected.
It describes directed temporal edges from past to present with k=10,
23-dimensional node features, and regression plus two classification labels.
It does not describe individual basal/bolus/food transaction nodes. Its
supplement's split table says OhioT1DM uses 80% sessions for training and 20%
for validation plus held-out temporal segments, which does not resolve whether
the held-out test is participant-disjoint. For BrisT1D, it lists 80% of
windows for training, 20% for validation, and 15 unseen patients for testing.
Thus this is direct prior art for temporal time-point graphs, multimodal
prediction, and graph explanations, but its Ohio split unit and event-node
details remain uncertain. The inspected abstract and supplement do not report
an event-instance graph versus same-information, same-timing, capacity-matched
non-graph relation experiment. The main article body is listed by PMC as
embargoed until 18 June 2027; this is distinct from the accessible OUP
supplement. [OUP article and supplementary data](https://academic.oup.com/jamia/article-abstract/33/9/1713/8711207#supplementary-data)
· [PubMed record](https://pubmed.ncbi.nlm.nih.gov/42314749/)
· [PMC record and release date](https://pmc.ncbi.nlm.nih.gov/articles/PMC13580734/)

### 2026 GLIMMER and MT-HypoNet: multimodal and multicenter forecasting

The Springer Nature full article for Khamesian et al.'s GLIMMER study reports
OhioT1DM and AZT1D (25 adults, 26,707 monitoring hours), CGM, basal, bolus and
carbohydrate features, and per-person chronological splits for the newly
collected AZT1D cohort. This is strong prior art for multimodal T1D forecasting,
glycemic-region-aware objectives and an openly available event-rich dataset.
It does not test an event-instance KG or same-information relation ablation;
AZT1D's described splits are within person rather than unseen-person external
validation. [Publisher full text](https://doi.org/10.1186/s44398-026-00032-x)
· [AZT1D dataset publication](https://doi.org/10.1109/BSN66969.2025.11337496)

The complete open-access article was checked after the initial abstract-only
screen. The retrospective cohort contains 1,662 participants from seven
centers. Loop is the primary training source, with inter-patient five-fold
cross-validation; the Loop table lists 844 participants (436 female, 408
male). The model uses a two-hour history to predict glucose at 5–30-minute
steps and forewarn hypoglycemia in the next 30 minutes. Its sustained-low
definition requires three consecutive CGM readings below 70 mg/dL. The
separate prospective cohort contains 36 perioperative participants with T2D;
it does not provide prospective T1D validation. The methods say insulin,
carbohydrate, and time-of-day inputs can be incorporated and call these
channels optional, but do not clearly identify the channel configuration for
the headline Loop result. The article does not describe an event-instance
graph versus same-information, same-timing, capacity-matched non-graph
relation experiment in the inspected methods. This is a paper-specific
finding, not evidence that no such study exists elsewhere.
[Full open-access article](https://pmc.ncbi.nlm.nih.gov/articles/PMC13019577/)
· [iScience publisher record](https://doi.org/10.1016/j.isci.2026.115294)
· [PubMed record](https://pubmed.ncbi.nlm.nih.gov/41907406/)

Both records were added to the literature matrix. They support retaining only
the narrow candidate question: whether explicit timestamped event-instance
relations add value under the same inputs, observation time, capacity, and
patient-disjoint evaluation as non-graph alternatives. Neither establishes
that such a relation test is absent from the entire field.

### SysCon 2026: physiology graph, multimodal summaries, and diagnostics

The inspected author-uploaded SysCon manuscript is titled *Explainable
Multitask Graph Network for Blood Glucose Forecasting and Hypoglycemia Risk
Classification*. It describes BrisT1D, glucose/insulin/carbohydrate/activity
and other context, a fixed physiology-inspired directed topology with
time-varying node attributes, multitask glucose prediction and threshold
classification, and graph diagnostic/perturbation analyses. The feature
construction summarizes historical signals over a window; insulin and
carbohydrate inputs are summary features rather than separate transaction
nodes. Its methods describe single future-value threshold labels at forecast
steps. It overlaps strongly with graph-based multimodal risk modeling and
structural explanation diagnostics, so the novelty boundary cannot rest on
those broad ingredients. The evaluation/split and relation tests need to be
compared from the full methods; the inspected text's split wording is
insufficient to establish patient disjointness. This source is author-uploaded
primary content rather than the final IEEE typeset article.
[Author-uploaded full manuscript and metadata](https://www.researchgate.net/publication/404642556_Explainable_Multitask_Graph_Network_for_Blood_Glucose_Forecasting_and_Hypoglycemia_Risk_Classification)
· [IEEE publisher record](https://doi.org/10.1109/SysCon66367.2026.11503533)

The JAMIA and SysCon records share authors and subject matter. Until the
relationship between the versions, data, and experiments is established from
the full article records, describe them as closely related outputs from the
same research line rather than treating them as independent replications.

### HSU project: directly overlapping ongoing direction

The Helmut-Schmidt University Data Engineering group’s project page (last
changed 6 August 2026) states that its T1D digital twin enhances DiaData into a
graph-based semantic representation with a clinically standardized ontology;
short-term hypoglycemia onset is its primary use case. This directly overlaps
the high-level idea of a patient-specific semantic graph for T1D and
hypoglycemia. The page presents an ongoing project, not completed comparative
predictive results. Accordingly, avoid claims that the overall research
direction is unprecedented, and do not attribute unreported results to this
project.
[Official HSU project page](https://www.hsu-hh.de/dataeng/en/research/current-projects/digital-twins-for-diabetes-management/)

### Other recent overlap: multimodal T1D forecasting and hypoglycemia prediction

These works are adjacent rather than direct graph-relation tests, but they
further narrow claims about multimodal inputs, patient-disjoint evaluation,
and behavior-aware hypoglycemia prediction:

- **MetaboNet-Bench (2026 preprint)** presents an open benchmark for glucose forecasting
  from CGM, insulin, and carbohydrate data, with novel-patient and
  known-patient splits and modality/model comparisons. It makes standardized
  multimodal forecasting and patient-wise generalization established
  directions. Its task is glucose forecasting; it does not test event-instance
  graph edges against an exactly information-, timing-, and capacity-matched
  non-graph control.
  [Primary paper (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC13321326/)
  · [arXiv record](https://arxiv.org/abs/2606.18640)
- **Alkhateeb et al. (2026)** report patient-wise evaluated, hour-ahead
  multimodal hypoglycemia risk modeling for adults with T1D during and after
  Ramadan, using CGM plus wearable, sleep, clinical, and behavior-proxy inputs.
  This precludes claiming novelty for temporal, behavior-aware, multimodal
  hypoglycemia prediction in general. It is a recurrent/feature-based
  comparison in a Ramadan cohort, not an event-relation graph comparison.
  [Primary journal article](https://www.mdpi.com/1424-8220/26/8/2552)
- **Gallardo García et al. (2026)** compare nutritional inputs for
  multihorizon glucose forecasting using patient-wise partitions and T1-DEXI
  data. This further establishes nutrition-aware glucose forecasting and
  patient-wise evaluation as existing directions; it is not a hypoglycemia
  graph-relation study.
  [Primary JMIR AI article](https://ai.jmir.org/2026/1/e105049)
- **T1D-UOM (2025)** is a released longitudinal multimodal dataset with CGM,
  basal/bolus insulin, detailed food intake, activity, and sleep measurements.
  It demonstrates that richer timestamped multimodal data exist, but is a
  dataset contribution rather than a controlled hypoglycemia-model comparison.
  [Scientific Data article](https://www.nature.com/articles/s41597-025-05695-1)

## What the current project can still test

These sources make novelty of “a patient-centric/temporal KG for T1D
hypoglycemia,” graph-based hypoglycemia prediction, and broad context-aware
explanation indefensible. The remaining candidate is narrower and empirical: an auditable
Loop development comparison of individual timestamped event-to-CGM graph
message passing against non-graph models receiving the same event instances,
time bins, prediction windows, and parameter count, plus routing and
event-to-time perturbation probes.

The original graph model outperformed a late-fusion sequence comparator in
ten one-epoch seed-fold fits, but the advantage did not persist against the
stricter control. At two seeds and five two-epoch folds per seed, aligned
pooling led participant-macro AP in all ten fits and macro-Brier in nine. In
the prespecified participant aggregate averaging each individual's paired
differences across seeds, graph-minus-pooling AP was −0.009900 (95%
fixed-prediction participant interval [−0.010477, −0.009345]) among 650
AP-defined participants; macro-Brier difference was +0.0001264
([+0.0001096, +0.0001429]) across 652 participants, both favoring pooling.
These intervals condition on the two fixed fitted seeds, which reuse the same
patient folds; they do not estimate seed or cohort uncertainty. First-seed
source digests vary across folds; all second-seed folds share one digest. The
graph-versus-sequence result is comparator-dependent. Current experiments do
not establish that clinical relation semantics add information, that the
graph model is converged, or that it improves on an equally optimized strong
CGM-only model. This is a development-stage, implementation-specific
comparison, not confirmatory evidence for a novel clinical knowledge graph.

Use wording such as: “We conduct a patient-disjoint development comparison of
timestamp-aligned event message passing and a parameter-matched non-graph
temporal control.” Do not say “first,” “clinically validated relation,”
“faithful clinical explanation,” or “graph superiority.” A manuscript-level
novelty claim remains provisional: the second-seed gate is complete, but
convergence/optimization uncertainty, replicated event-disabled controls,
measured event availability (or a clearly labeled delay simulation),
independent explanation validation, external-cohort replication, full-text
review of paywalled methods, and a reproducible database search remain
outstanding.

## Evidence links

### Additional 31 October checks: interpretable and event-aware prediction

The [PubMed primary record](https://pubmed.ncbi.nlm.nih.gov/42224311/) for
Tziavaras et al. (2026) reports an autoencoder-guided attention-LSTM for
nocturnal hypoglycemia prediction up to 12 hours in advance. Its abstract says
the model uses a 24-hour CGM/meal/insulin history, incorporates simulated
glucose absorption, insulin kinetics and insulin-signaling physiology, and
was developed on OhioT1DM with external SMARTDIAB evaluation. This is strong
prior work for temporal, physiology-informed, event-aware, interpretable T1D
hypoglycemia prediction. It does not describe an event-instance graph or a
matched relation ablation; detailed methods and split mechanics were not
reviewed here.

The full [Frontiers primary article](https://www.frontiersin.org/journals/endocrinology/articles/10.3389/fendo.2026.1816599/full)
by Zhang et al. (2026) reports an interpretable in-hospital risk model using
65 demographic, diabetes, comorbidity and laboratory predictors in 1,498
adult inpatients across five hospitals. The primary outcome is in-hospital
capillary glucose below 3.9 mmol/L. It randomly divides the pooled cohort
70/30 for development/held-out validation, with five-fold tuning inside the
development group. This is a distinct static/encounter-level inpatient task,
but confirms that broad interpretable T1D hypoglycemia risk modeling and
within-study held-out evaluation are established.

- Onwuchekwa JID, Weber C, Maleshkova M. *Enhancing Hypoglycemia Prediction in
  Type 1 Diabetes through Semantic Knowledge Integration and Machine Learning
  Optimization.* ESWC 2024. [Proceedings PDF](https://2024.eswc-conferences.org/wp-content/uploads/2024/05/77770363.pdf).
- Hüni F. *Predicting Events of Hypoglycemia: A Comparison of Long
  Short-Term Memory and Graph Attention Network Based Approaches.* Bachelor
  thesis, University of Bern; 2024. [Official thesis PDF](https://prg.inf.unibe.ch/wp-content/uploads/2024/08/BA_FabianHuni.pdf).
- Hüni F, Garcia-Tirado J, Riesen K. *LSTM Networks and Graph Neural Networks
  for Predicting Events of Hypoglycemia.* S+SSPR 2024, published 2025.
  [Springer chapter](https://link.springer.com/chapter/10.1007/978-3-031-80507-3_6).
- Sarwar MA et al. *GAT-BiGRU: explainable multi-task temporal graph learning
  for glucose forecasting, hypoglycemia risk, and counterfactual insulin
  adjustment.* JAMIA 2026;33(9):1713–1725.
  [OUP article](https://academic.oup.com/jamia/article/33/9/1713/8711207).
- Jeffries N et al. *MetaboNet-Bench: A Multi-modal Benchmark for Glucose
  Forecasting in Type 1 Diabetes.* 2026.
  [Primary paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC13321326/).
- Alkhateeb M et al. *Temporal and Behaviour-Aware Multimodal Modelling for
  Hour-Ahead Hypoglycaemia Prediction During Ramadan Fasting in Type 1
  Diabetes.* Sensors 2026;26(8):2552.
  [Journal article](https://www.mdpi.com/1424-8220/26/8/2552).
- Gallardo García C et al. *Interpretable Multihorizon Glucose Forecasting for
  Assessing Nutritional Information Impact in Type 1 Diabetes Management.*
  JMIR AI 2026;5:e105049. [Journal article](https://ai.jmir.org/2026/1/e105049).
- Alsuhaymi A et al. *A Longitudinal Multimodal Dataset of Type 1 Diabetes.*
  Scientific Data 2025;12:1379.
  [Publisher article](https://www.nature.com/articles/s41597-025-05695-1).
- Sarwar MA et al. *Explainable Multitask Graph Network for Blood Glucose
  Forecasting and Hypoglycemia Risk Classification.* SysCon 2026.
  [Author full text](https://www.researchgate.net/publication/404642556_Explainable_Multitask_Graph_Network_for_Blood_Glucose_Forecasting_and_Hypoglycemia_Risk_Classification);
  [IEEE record](https://doi.org/10.1109/SysCon66367.2026.11503533).
- Helmut-Schmidt University, Data Engineering. *Digital Twins for Diabetes
  Management.* [Official project page](https://www.hsu-hh.de/dataeng/en/research/current-projects/digital-twins-for-diabetes-management/).
