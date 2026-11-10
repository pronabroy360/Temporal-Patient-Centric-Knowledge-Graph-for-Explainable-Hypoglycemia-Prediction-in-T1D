# Novelty evidence report: temporal event graphs for T1D hypoglycemia

**Evidence cut-off:** 31 October 2026  
**Status:** Development-stage, retrospective evidence synthesis. This report
does not establish a first-in-field claim or clinical validation. The locked
183-person final-performance group remains unopened. A predeclared eight-epoch
outer-0 CPU comparison is now complete at one additional seed; it slightly
favors time-aligned pooling, with a much smaller difference than the primary
two-epoch aggregate. It is a schedule-sensitivity check, not a convergence
claim. The second seed of the
five-fold, two-epoch time-aligned pooling comparison is complete. Across 652
disjoint validation participants, graph-minus-control participant-macro AP is
−0.012193 (95% fixed-prediction participant interval [−0.012935, −0.011445])
and macro-Brier is +0.0001728 ([+0.0001554, +0.0001894]), both favoring
pooling. Per-fold and aggregate saved-prediction audits are linked in the
evidence table below. A primary-source verification note was added at
[`primary_source_novelty_check_2026_10_31.md`](primary_source_novelty_check_2026_10_31.md).
The source note includes the full methods of Hüni's University of Bern thesis,
a related author-work predecessor to the 2025 LSTM-versus-GAT chapter, and
corrects the status of the second-seed experiment. The refreshed
[artifact-integrity audit](../audit/novelty_evidence_bundle_20261031_v10.json)
checks the first-seed outer-0 pair, all five second-seed pairs, and both
eight-epoch run archives; the
[manuscript verification](../manuscript/verification.json) checks all ten
aligned-control pairs and the cross-seed prediction-window identities. A
[correction note](novelty_evidence_audit_correction_2026_10_31.md) explains a
missing verification summary in superseded v4/v5 audit outputs.

## Executive conclusion

The project should **not** claim novelty for a patient-centric or temporal
knowledge graph, graph-based glucose forecasting, hypoglycemia prediction
with graphs, graph explanations, or the use of insulin and meal context.
Precedents include a 2024 de Bruijn graph that forecasts pediatric
hypoglycemia, a 2024 University of Bern thesis (followed by a 2025
LSTM-versus-GAT chapter) comparing visibility-graph and LSTM hypoglycemia-event
prediction on 37 people with T1D, and a 2026 JAMIA temporal GAT-BiGRU study that predicts risk from
feature-enriched temporal graph nodes on OhioT1DM and BrisT1D and uses
GNNExplainer. The 2026 full-text GLIMMER study further establishes public
multimodal T1D data with CGM, basal, bolus and carbohydrate features, while
MT-HypoNet reports multicenter retrospective and prospective CGM-based
hypoglycemia forewarning. A 2026 multimodal T1D forecasting benchmark also
makes benchmark standardization and controlled modality comparison an
existing research direction. The JAMIA and SysCon
records have overlapping authors and subject matter and should be treated as
closely related outputs until their data and experiment overlap is checked;
they are not independent replication evidence. The ESWC 2024 and HSU project
also preclude novelty claims based on the broad patient-specific semantic KG
framing. Chen et al.’s IJCAI 2024 TRANS paper also establishes a general
temporal heterogeneous graph with diagnosis/procedure/medication-code nodes,
timestamped visit nodes, message passing, and graph explanations for EHR
next-visit prediction. The 31 October targeted source update adds BG-BERT (multimodal,
forecast-derived low-glucose detection), Sun et al. (future-disturbance-aware
sequence distillation), and PhyNet (physiological/counterfactual faithfulness)
as adjacent precedents. These narrow claims about event inclusion,
availability-aware temporal modeling, and explanation credibility. The
31 October closing search also recorded Oviedo et al.'s personalized
meal/bolus-triggered postprandial hypoglycemia prediction and IDMVis's
temporal event-sequence visualization for T1D decision support. These further
limit novelty claims about event-triggered hypoglycemia prediction and
temporal event representation; neither is the project's rolling,
patient-disjoint, matched relation comparison. The closing pass also verified
Ibrahim et al.'s five-seed, two-cohort counterfactual physiology study and
Akrong et al.'s feature-deletion and stability evaluation for glucose
forecast explanations. These make broad novelty claims for physiology-aware
evaluation or explanation-faithfulness metrics untenable, while neither
studies event-instance graph relations. The latest search added a 225-person patient-level CGM-only hypoglycemia event predictor and a 449-person retrospective event-cause classifier with insulin/carbohydrate validation. These establish patient-level short-horizon prediction and post-event cause interpretation as prior work, with different endpoints and tasks from this graph comparison. The inspected records do not establish the exact same-information, same-timing,
capacity-aware event-instance relation comparison for this project’s
patient-disjoint incident-within-horizon endpoint.

A full 31 October review of a newly located 26 October arXiv preprint makes
the task-level overlap clearer: it predicts any observed future CGM below 70
mg/dL within 30/60/120 minutes, uses patient-disjoint outer folds on
T1DiabetesGranada, and compares sequence with multimodal/state-updating models
while testing explanation faithfulness, stability, and perturbation response.
Its described modalities are CGM, static clinical variables, biochemical and
diagnostic records, and monitoring/context summaries; it does not describe raw
timestamped insulin or meal transaction instances or graph relations. The
preprint's internal chronological anchor split, incomplete reproducibility
details, and unreviewed status constrain direct numeric comparison. This
source removes task formulation, patient-level evaluation, multimodal
comparison, and explanation robustness from the novelty claim; only the
specific event-instance relation comparison remains a candidate gap. A
separate TFT supplement record is bibliographically verified but its methods
remain inaccessible. The additional primary-source check found that Dave et
al. already compared short-horizon hypoglycemia prediction with and without
engineered insulin/carbohydrate context, although its abstract and body
disagree on the 30-minute incremental effect and contextual records were
available for only a subset. Meal-anchored risk prediction and nocturnal
models using meal/bolus candidates or aggregate carbohydrate-on-board also
predate this work. The matrix now contains 69 unique records after correcting the 2019 Seo et al. author key and completing a small citation-chain screen; the search remains targeted rather than systematic. See the [source-by-source comparison](targeted_prior_art_search_2026_10_31.md).

The strongest candidate contribution is narrower and empirical: an auditable
Loop development study comparing **raw timestamped insulin/meal transaction
alignment to CGM windows** with increasingly controlled same-information models on
patient-disjoint folds, followed by probes of routing and event-to-time
assignment. The graph model outperformed a late-fusion sequence comparator in
ten one-epoch seed-fold fits, but that advantage did not persist against the
more stringent control. Across five two-epoch folds at the first seed,
time-aligned pooling had higher participant-macro AP in every fold; its Brier
score was better in four. At a second seed, pooling had higher AP and lower
macro-Brier in all five folds under one frozen source digest. Across the 652
participants, pooling led AP for 632 (graph for 18 of the 650 participants
with defined AP) and Brier for 567 (graph for 85). The bootstrap intervals
condition on these saved predictions, and both seeds use the same patient
folds, so this is not independent-cohort evidence. The first-seed source
digests also differ across folds; its first outer-4 graph artifact was
excluded after a strict source mismatch and rerun. The graph-vs-sequence
advantage is comparator-dependent. No current result isolates a general graph
topology effect, shows that typed clinical relations add information, or
establishes benefit over an equally optimized CGM-only predictor. The result
is a preliminary, implementation-specific negative comparison, not
confirmatory evidence of a novel clinical knowledge graph.

An additional recovered two-epoch full-history sequence ablation on outer-0
also favored the event-zero branch over the event-enabled branch for both AP
and Brier. This is a different sequence architecture, not a replication of
the graph event ablation, and the archive does not carry an explicit
`locked_holdout_used` field. It is included as a separately bounded result;
the current evidence does not support a general claim that adding event
content helps or hurts across model families.

The defensible paper direction is a **controlled, dataset- and task-specific
comparison**, with the method explicitly named a temporal event graph unless
the manuscript implements and evaluates a semantically grounded knowledge
graph. Whether that empirical comparison itself is novel remains provisional:
the closest matched event-relation comparison has not been established in the
retrieved primary sources, but no systematic search has been completed. Do not
use “first” language.

## 1. What the project actually represents and predicts

The current research-scale experiment is a retrospective Loop public-release
analysis with a frozen patient-disjoint development manifest. The main graph
uses a 24-slot masked CGM history, up to 64 retained basal, bolus, and food
event instances in a two-hour lookback, and one event-to-CGM edge per retained
event. The relation/edge assignment is reconstructed from occurrence time,
the event's modality, and the observed CGM grid. It is not an independently
annotated clinical relation ontology. The main endpoint is any CGM value below
70 mg/dL during the next 30 minutes when future coverage is complete, subject
to the frozen eligibility rule.

The main development index contains 835 participants overall; the model split
uses 652 development participants and reserves 183 for a later final test.
The modeling cache covers 44,028,064 development windows and 1,296,297
positive labels. The 64-event cap was chosen after a truncation audit: 16
events would truncate 39.27% of windows, while 64 would truncate 17,720
windows (about 0.04%). These are data-processing facts, not evidence of
clinical event completeness.

The primary availability limitation is material. The upload-linkage audit did
not establish first-usable times for basal, bolus, food, or CGM records with
sufficient completeness and validity. The models replay occurrence times
under an assumed immediate-availability policy. This is an optimistic
retrospective input condition, not a real-time or prospective evaluation.
Missing event records mean “not present in the retained source,” not verified
clinical absence.

## 2. Completed predictive and relation evidence

| Comparison or control | Verified development evidence | What it supports | What it does not support |
|---|---|---|---|
| Graph-generic vs capacity-matched non-graph event sequence | Two seeds × five patient-disjoint outer folds; one epoch per fit; 36,883 parameters per model; 652 people, 44,028,064 windows and 1,296,297 positives per seed. Graph AP higher and macro-Brier lower in all 10 fold-seed pairs. AP differences range +0.07028 to +0.11047. Descriptive unweighted mean AP difference is +0.08653 for seed 20261003 and +0.08657 for seed 20261004. Per-fold participant bootstrap intervals condition on each pair of fixed models. | The tested graph parameterization did better than this exact-capacity event-sequence implementation on this Loop split and training schedule, under the same information, windows, optimizer, event budget and parameter count. | Not an isolated topology effect: the architectures differ in event-CGM alignment, fusion, and computation. One epoch may compare learning rates as much as converged performance. The ten fits are not ten independent cohorts; there is no uncertainty interval over seeds or studies. It does not establish clinical relation semantics or benefit over an equally optimized CGM-only model. |
| Graph-generic vs time-aligned non-graph event pooling | Seed 20261029 completed five folds at two epochs, with exactly 36,883 parameters per arm. Graph-minus-control AP was negative in all five folds (−0.008941, −0.005902, −0.011140, −0.006601, −0.005691); macro-Brier favored pooling in four of five. Seed 20261030 completed all five folds at two epochs under one frozen source digest. Per-fold graph-minus-control AP: outer-0 −0.008854 (95% fixed-prediction participant interval [−0.010005, −0.007736]); outer-1 −0.011153 ([−0.012896, −0.009550]); outer-2 −0.021387 ([−0.023610, −0.019330]); outer-3 −0.011318 ([−0.012458, −0.010314]); outer-4 −0.008666 ([−0.009782, −0.007650]). Macro-Brier differences were positive in all five folds (+0.0000393, +0.0001856, +0.0003404, +0.0001464, +0.0001585), favoring pooling. Recomputed over all 652 disjoint validation participants (44,028,064 windows), graph-minus-control participant-macro AP was −0.012193 (95% fixed-prediction participant interval [−0.012935, −0.011445]; pooling ahead for 632 vs graph ahead for 18 AP-defined participants); macro-Brier was +0.0001728 ([+0.0001554, +0.0001894]; pooling lower for 567 vs graph lower for 85 participants). The protocol-specified summary averaging each participant over both seeds gives AP −0.009900 (95% fixed-prediction participant interval [−0.010477, −0.009345]) and macro-Brier +0.0001264 ([+0.0001096, +0.0001429]); pooling leads AP for 639/650 and Brier for 528/652 participants. | In this tested setting, time-aligned pooling outperformed graph message passing across all folds and both seeds for AP, and for Brier across all five folds in the second seed. This argues against a claim that these graph relations or message-passing operations add predictive value over this information-, timing-, and capacity-matched control under this protocol. | This does not establish that graphs generally fail, that clinical relations are invalid, or that results generalize beyond this Loop release, split and two-epoch fitting schedule. Confidence intervals condition on saved predictions and do not estimate fit, seed, or cohort uncertainty. The first-seed source digest varies across folds; the second-seed runs share source digest `a4d1a91916a675024110e1c30d54546c3aa0d51724480dfdbcdbb141dea71648`. Event availability is retrospective occurrence time with immediate availability assumed, not measured. The locked holdout remains unopened. See the [five-fold protocol](loop_time_aligned_nongraph_control.md), the [second-seed aggregate audit](../audit/loop_graph_vs_aligned_nongraph_seed20261030_five_fold_summary.json), second-seed per-fold audits [outer-0](../audit/loop_graph_vs_aligned_nongraph_outer0_seed20261030_source_a4d.json), [outer-1](../audit/loop_graph_vs_aligned_nongraph_outer1_seed20261030_source_a4d.json), [outer-2](../audit/loop_graph_vs_aligned_nongraph_outer2_seed20261030_source_a4d.json), [outer-3](../audit/loop_graph_vs_aligned_nongraph_outer3_seed20261030_source_a4d.json), [outer-4](../audit/loop_graph_vs_aligned_nongraph_outer4_seed20261030_source_a4d.json), and first-seed [outer-2](../audit/loop_graph_vs_aligned_nongraph_outer2_seed20261029_current_source_rerun.json), [outer-3](../audit/loop_graph_vs_aligned_nongraph_outer3_seed20261029_current_source.json), and [outer-4](../audit/loop_graph_vs_aligned_nongraph_outer4_seed20261029_source_a4d.json) audits. |
| Eight-epoch schedule follow-up, outer-0, seed 20261031 (CPU) | Same frozen input, training membership, timing, optimizer, batch size, workers, and 36,883 parameters in both arms; 130 validation participants and 8,885,621 windows. Graph AP 0.533263 vs aligned pooling 0.533979; graph-minus-pooling AP −0.000716 (95% fixed-prediction participant interval [−0.001317, −0.000106]). Graph macro-Brier 0.019720 vs pooling 0.019706; difference +0.00001415 ([+0.00000111, +0.00002768]). | The longer fixed schedule preserves the direction favoring pooling, with a much smaller gap than the two-epoch aggregate. | One fold and one seed cannot establish convergence or estimate seed/cohort uncertainty. CPU execution is a schedule sensitivity analysis, not bitwise replication of GPU runs. The fixed-prediction interval does not include model refitting. See the [predeclared protocol and audit](loop_extended_schedule_protocol_2026_10_31.md) and [paired result](../audit/loop_longer_schedule_outer0_seed20261031_graph_vs_aligned_cpu8.json). |
| Modality-typed vs generic graph routing | Seed 20261004 across all five folds (652 participants and 44,028,064 windows); each variant 36,883 parameters. Typed-minus-generic AP ranges −0.002015 to +0.001902; typed routing has higher AP in 2/5 folds. Unweighted mean AP difference is −0.000476. Brier direction is also mixed. | This specific modality-derived expert-routing constraint has no consistent advantage over generic routing in the tested seed. | It does not disprove all possible typed relations, other definitions, training budgets, or clinical relations. It does not compare the graph against a sequence architecture. |
| Event-enabled vs event-disabled graph branch | Two paired outer-0 fits now exist. Seed 20261004 at one epoch favored event-enabled: AP difference +0.002800 (95% fixed-prediction participant interval [+0.001996, +0.003609]) and macro-Brier −0.0002003 ([-0.0002411, −0.0001597]). Seed 20261031 at two epochs favored event-disabled: graph-minus-disabled AP −0.002278 ([-0.003334, −0.001218]) and macro-Brier +0.00007086 ([+0.00004314, +0.00010078]). Each pair has 130 participants, 8,885,621 matched windows and 36,883 declared parameters per arm; the new pair shares input/source/training-membership hashes and explicitly records no locked-holdout use. | The event-input result changes direction across these two fixed schedules/seeds. There is no stable evidence here that recorded event inputs improve this graph's prediction. | Both are one-fold comparisons, and they use different seeds and epoch counts, so the difference in results cannot be attributed to seed or schedule alone. Disabling events removes event-derived inputs, event edges, and gradients to the event encoder/edge experts; equal declared parameter counts do not equal effective capacity. The paired intervals condition on fixed fits. Neither result isolates relation semantics or establishes clinical explanation quality. See the [one-epoch audit](../audit/loop_relation_event_ablation_outer0_seed20261004_paired_20261025.json) and [two-epoch audit](../audit/loop_graph_event_ablation_outer0_seed20261031_paired_20261031.json). |
| Recovered full-history sequence event-enabled vs event-zero branch | Outer-0, seed 20261003, two epochs, 130 participants and 8,885,621 identical validation windows; 36,609 declared parameters per arm. Event-enabled minus event-zero AP −0.008926 (10,000-draw fixed-prediction participant interval [−0.010428, −0.007443]); macro-Brier +0.0002728, favoring the event-zero arm. Event-enabled AP 0.460532 vs 0.469458; macro-Brier 0.021839 vs 0.021566. The paired archives share the manifest, window identity, source digest, training split, seed, and optimizer contract. | This separate full-history sequence architecture does not show a consistent benefit from event inputs; it makes the event-input result architecture- and schedule-dependent. | It is not a graph replication and uses two epochs, so it cannot be pooled with the one-epoch graph ablation. The event-zero branch also lacks event-encoder gradients, and fixed-prediction intervals exclude model-refit uncertainty. Its run metadata identifies validation scope but does not explicitly declare `locked_holdout_used`; do not describe that archive as carrying a positive no-holdout flag. See the [paired audit](../audit/loop_full_history_event_ablation_outer0_seed20261003_paired_20261031.json) and [recovered archives](loop_event_ablation_result_2026_10_25.md). |
| Nearest vs second-nearest causal CGM endpoint | Two seeds × five folds; 36,883 parameters, one epoch, same frozen windows. Nearest endpoint has higher AP and lower macro-Brier in 8/10 fold-seed pairs. A participant-cluster bootstrap averages each participant's paired difference across the two fixed seeds: AP +0.002097 (95% CI +0.001761 to +0.002443); macro-Brier −0.0000773 (−0.0000957 to −0.0000594), among 650 AP-defined participants. | Evidence of small sensitivity to this particular temporal endpoint assignment in the current graph. | Not proof of clinical relation validity, causality, general graph benefit, or training-seed stability. The interval is conditional on two fixed one-epoch seeds and one Loop development cohort. |
| Within-window event-age reassignment | Fixed-checkpoint replay across two seeds × five folds. All ten fits have a positive original-minus-reassigned AP difference; mean difference +0.0001118. Only 3/10 fold-specific participant intervals exclude zero. Brier direction is split 5/5; 4/10 intervals exclude zero. | Very small, metric-dependent sensitivity to one deterministic event-age rotation. | The ten fit-level results are not independent, and no cross-seed participant-delta bootstrap was retained. This is not evidence that clinical relations are valid or useful. |
| Sampled event deletion/retention screen | One epoch-1 graph-generic checkpoint, outer-0 seed 20261005. Deterministic sample of 518 windows (258 positive, 260 negative) from all 130 validation participants. Top-three events were selected by single-event deletion sensitivity; top-set joint deletion exceeded modality-matched random by 0.003943 participant-average absolute probability change (95% CI 0.003266 to 0.004665). Top-set retention stayed 0.003841 closer to the original prediction (95% CI 0.003203 to 0.004525). | Exploratory local model-sensitivity and sufficiency diagnostic under this masking rule. | The deletion comparison is selection-conditioned because deletion sensitivity selected the top events. This is not an independent attribution-faithfulness test, clinical correctness assessment, causal result, or usability study. |

The historical CGM-only, event-summary, and earlier GRU comparisons have
different architectures and training budgets. They remain relevant context but
do not substitute for a matched CGM-only graph control under the current
one-epoch protocol. In particular, the present graph-vs-sequence advantage
should not be described as evidence that adding events beats CGM alone.

The source digests of some replay evaluators differ from the historical
training source digests. For the fixed-checkpoint event-age controls, clean
replays reproduced stored metrics and window identities within tolerance.
The explanation audit reverified the data contract and window identity but
also reports source-digest mismatch. These are compatibility-checked
reanalyses, not claims that every historical run was regenerated from an
identical source tree.

Machine-readable evidence is indexed in the [five-fold second-seed graph-vs-aligned-pooling
summary](../audit/loop_graph_vs_aligned_nongraph_seed20261030_five_fold_summary.json), the [two-seed participant-level summary](../audit/loop_graph_vs_aligned_nongraph_two_seed_five_fold_participant_summary.json), and the [two-seed/five-fold
graph-vs-sequence summary](../audit/loop_mps_graph_sequence_two_seed_five_fold_summary_20261020.json),
[typed-routing summary](../audit/loop_relation_typed_vs_generic_seed20261004_five_fold_summary_20261020.json),
[event-input ablation](../audit/loop_relation_event_ablation_outer0_seed20261004_paired_20261025.json),
[endpoint sensitivity summary](../audit/loop_relation_endpoint_perturbation_two_seed_five_fold_summary_20261028.json),
[event-age reassignment summary](../audit/loop_event_age_reassignment_two_seed_five_fold_summary_20261029.json),
and [sampled deletion/retention report](../audit/loop_graph_event_explanation_faithfulness_outer0_seed20261005_20261029_v2.json). The latest [evidence-bundle audit](../audit/novelty_evidence_bundle_20261031_v10.json) checked 139 source/artifact records across graph-vs-sequence, both aligned-control seeds, routing, endpoint and event-age perturbations, explanation sensitivity, the eight-epoch CPU pair, and the recovered two-epoch sequence event ablation. Each supported section reports a verified status; the recovered archive is marked validation scope but lacks an explicit locked-holdout-use field. The two-seed participant-summary contract is cross-checked against the separate byte-identical saved-prediction recomputation receipt. The [manuscript verification](../manuscript/verification.json) additionally checks all ten two-epoch aligned-control pairs, within-fold source matches, cross-seed validation-window identities, the extended-schedule run contracts, and the excluded mismatched outer-4 run.

## 3. Closest prior work and its impact

| Prior work | Verified overlap | Remaining distinction for this study |
|---|---|---|
| Onwuchekwa et al., ESWC 2024, *Enhancing Hypoglycemia Prediction in Type 1 Diabetes through Semantic Knowledge Integration and Machine Learning Optimization* | Explicitly proposes patient-specific semantic KGs and ML for T1D hypoglycemia prediction, with ontology/embedding integration and preliminary analysis. | The inspected paper describes the work as early stage and does not establish this Loop incident-window benchmark or a same-information, exact-capacity event-graph versus sequence comparison. Its existence rules out claiming that patient-specific semantic KG hypoglycemia prediction is itself new. |
| Sarani Rad et al., 2024, *Personalized Diabetes Management with Digital Twins: A Patient-Centric Knowledge Graph Approach* | Patient-centric health KG/digital-twin framing and diabetes applications including glucose prediction and insulin optimization. | It does not establish this event-instance prediction comparison in the inspected work. Patient-centricity and the KG framing are not standalone novelty. |
| Cakiroglu et al., *A reinforcement learning approach to effective forecasting of pediatric hypoglycemia in diabetes I patients using an extended de Bruijn graph*, Scientific Reports 2024 | A graph over discretized glucose patterns forecasts hypoglycemia within 30 minutes in a 15-person pediatric cohort; the paper reports leave-one-out evaluation. | This rules out graph-based short-horizon hypoglycemia forecasting as new. Its graph represents glucose-state sequences, not transaction-level insulin/meal instances or the same-information relation ablation tested here. [Publisher article](https://www.nature.com/articles/s41598-024-82649-4). |
| Hüni's 2024 University of Bern thesis and related Hüni et al. S+SSPR 2024 / Springer 2025 chapter | The full thesis compares CGM-only LSTM and natural-visibility-graph GNN models using 37 people with T1D. It uses any future CGM value below 70 mg/dL as the label, includes the 120-minute-history/30-minute-horizon setting, and reports F2 0.348 (LSTM) versus 0.409 (GNN) averaged over patient datasets. | Models are fit separately per patient; the first 70% of ordered samples train and the last 30% validate, so the evaluation is within-person chronological, not patient-disjoint. The thesis does not document parameter matching. Nodes are CGM readings, not insulin/meal transactions. The final Springer chapter may not be identical to the thesis. This rules out broad first-graph, first graph-versus-sequence, and first matching endpoint/history claims; it does not answer the event-instance matched-control question. [Official thesis](https://prg.inf.unibe.ch/wp-content/uploads/2024/08/BA_FabianHuni.pdf), [repository](https://github.com/fabianHueni/cgm-visibility-graph-dataset), [chapter](https://link.springer.com/chapter/10.1007/978-3-031-80507-3_6). |
| Ma et al., 2022, multidimensional sequential-pattern mining for T1D hypoglycemia alarms | Uses CGM, meal, and insulin streams in a multidimensional sequence database; mines hypoglycemia patterns with UniSeq and evaluates pattern-matching alarms on OhioT1DM. Abstract reports 75.76% sensitivity, 75% precision, 75.38% F1, and 25.17-minute mean early alarm. | Multimodal temporal pattern mining for hypoglycemia warning is prior work. It is not an event-instance KG relation test and does not establish an information-, timing-, and capacity-matched relation ablation. Exact split mechanics and comparability to the current rolling label were not established from the inspected abstract. [PubMed](https://pubmed.ncbi.nlm.nih.gov/36387535/). |
| Zhu et al., 2022, ARISES wearable and deep-learning study | A six-week, 12-adult study combines CGM, daily meal/bolus entries and wearable physiology for glucose prediction and hypo-/hyperglycemia warnings; an attention-based recurrent model reports 60-minute results and real-time app inference. | Multimodal event-aware, personalized warning and real-time deployment are established. This is not a transaction-event graph comparison; data are proprietary and the cohort is small. [npj Digital Medicine](https://www.nature.com/articles/s41746-022-00626-5). |
| Athanasiou et al., EMBC 2024, personalized interpretable multilevel hypoglycemia risk | Uses CGM, insulin and meal information from 12 people with T1D, an insulin-signaling mathematical model, tree-based ML and TreeSHAP; abstract reports 0–30 and 30–60-minute risk windows. | Personalized interpretable event-aware risk prediction is prior work. It does not establish a KG relation test; detailed split and event-availability mechanics remain unverified from the abstract. [PubMed](https://pubmed.ncbi.nlm.nih.gov/40039236/). |
| Fleischer et al., 2022, CGM-only hypoglycemia event prediction | RUSBoost predicts sustained <70 mg/dL for at least 15 minutes up to 40 minutes ahead from one-hour CGM history in 225 adults with T1D; uses patient-level 70/30 train/test and event-level lead-time assessment. | Strong CGM-only patient-level baseline precedent, but no event inputs; label and 40-minute horizon differ from the present 30-minute any-low outcome. [Full text](https://www.frontiersin.org/journals/clinical-diabetes-and-healthcare/articles/10.3389/fcdhc.2022.1066744/full). |
| Cederblad et al., 2023, HypoCNN cause classification | 449 people with T1D and 42,120 detected events; clinician-labeled sample; uses treatment records to validate likely causes and a separate clinician evaluation cohort. | Cause interpretation after observed events is established; this is not prospective incident-low prediction or graph-based explanation. [PubMed](https://pubmed.ncbi.nlm.nih.gov/37052842/), [publisher](https://link.springer.com/article/10.1007/s13300-023-01403-7). |
| Piao et al., 2025, GARNN | Graph-attentive recurrent modeling of multivariate glucose time series, including meal/insulin signals and temporal interpretability. | The graph is over variables/time-series structure, not the present event-instance-to-CGM representation; its task and benchmark do not establish the current incident-low matched comparison. |
| Tziavaras et al., 2026, autoencoder-guided attention-LSTM for nocturnal hypoglycemia | The PubMed abstract reports a physiology-informed attention-LSTM using 24-hour CGM, meal, and insulin inputs to predict nocturnal hypoglycemia up to 12 hours ahead, with OhioT1DM testing and SMARTDIAB external validation; attention mapping is used for interpretation. | This establishes that long-history, physiology-informed, event-aware, interpretable hypoglycemia prediction with external validation is prior work. It is not a transaction-event graph or the matched event-relation ablation studied here. The full methods and split details were not reviewed. [PubMed record](https://pubmed.ncbi.nlm.nih.gov/42224311/). |
| Sarwar et al., SysCon 2026, *Explainable Multitask Graph Network for Blood Glucose Forecasting and Hypoglycemia Risk Classification* | Multimodal CGM, insulin, carbohydrates and activity; fixed physiology graph; glucose forecasting plus future-point hypoglycemia classification; graph/node/edge explanation diagnostics. | In the author manuscript inspected, modalities are summary nodes on a fixed topology rather than each timestamped treatment transaction as a separate event instance. Split-unit details and final IEEE text were not verified. Graphs, physiology edges and graph perturbation diagnostics are not novel in themselves. |
| Sarwar et al., 2026, JAMIA, *GAT-BiGRU: explainable multi-task temporal graph learning for glucose forecasting, hypoglycemia risk, and counterfactual insulin adjustment* | PubMed/OUP abstract establishes a temporal graph over feature-enriched CGM time points, GAT-BiGRU, multimodal 30/60-minute risk and GNNExplainer. The OUP supplement describes directed past-to-present k=10 temporal edges and 23-dimensional node features. It reports OhioT1DM session and temporal-segment splits and a BrisT1D test on 15 unseen patients. PMC lists the article body as embargoed until 18 June 2027. | This is direct prior art for temporal graph hypoglycemia prediction. Supplementary split wording does not resolve Ohio participant separation, and the inspected abstract/supplement do not describe event-instance nodes or an information-, timing-, and capacity-matched non-graph relation control. Treat those as unverified beyond inspected materials. [OUP article and supplement](https://academic.oup.com/jamia/article-abstract/33/9/1713/8711207#supplementary-data), [PMC release record](https://pmc.ncbi.nlm.nih.gov/articles/PMC13580734/). |
| Khamesian et al., 2026, *Glycemic-aware and architecture-agnostic training framework for blood glucose forecasting in type 1 diabetes* (GLIMMER) | Full primary Springer article reports OhioT1DM and the public AZT1D cohort (25 adults; 26,707 hours), with CGM, basal, bolus and carbohydrate features, dysglycemia-focused glucose forecasting, and per-person chronological AZT1D splits. | Multimodal CGM/insulin/meal inputs, accessible T1D data, and clinically weighted forecasting are established. The study is not a graph-relation comparison; its split and point-label task differ from our incident-within-horizon benchmark. It further narrows novelty to the relation-control question, not multimodal prediction or data release. [Publisher full text](https://doi.org/10.1186/s44398-026-00032-x). |
| Fang et al., 2026, *Glucose forecasting and hypoglycemia forewarning in type 1 and type 2 diabetes using deep learning* (MT-HypoNet) | Full text reports 1,662 retrospective participants from seven centers; Loop is the primary training source with inter-patient five-fold evaluation, two-hour histories, 5–30-minute BG forecasts, and 30-minute hypoglycemia forewarning. The Loop cohort has 844 participants. The sustained-low label requires three consecutive readings <70 mg/dL. A separate prospective cohort has 36 perioperative participants with T2D. Insulin, carbohydrate, and time-of-day channels are described as optional, but the principal Loop configuration is unclear. | Rules out claims to the first Loop-trained forewarning model, first inter-patient Loop evaluation, or first two-hour/30-minute setup. Prospective validation is T2D, not T1D. The inspected methods do not report the event-instance graph versus matched non-graph relation test; this is source-bounded, not evidence of absence in the field. [Full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC13019577/), [publisher](https://doi.org/10.1016/j.isci.2026.115294). |
| Zaitcev et al., 2023, *Automatic inference of hypoglycemia causes in type 1 diabetes: a feasibility study* | Retrospective classification of patient-labeled hypoglycemia causes using time-context, insulin, food, activity and self-care features from 54 people with T1D; the evaluated cases are retrospective labeled episodes. | This rules out broad claims to the first explainable or context-aware interpretation of hypoglycemia causes. It is cause classification after an episode, not prospective incident-risk prediction or a graph-message-passing comparison. [Frontiers article](https://www.frontiersin.org/journals/clinical-diabetes-and-healthcare/articles/10.3389/fcdhc.2023.1095859/full). |
| Zhang et al., 2026, interpretable in-hospital T1D hypoglycemia risk | Five-hospital retrospective study of 1,498 adult inpatients; demographics, clinical factors, comorbidities and labs feed standard ML models, with a random patient-level 70/30 split and held-out evaluation. | Interpretable T1D hypoglycemia-risk modeling and a within-system holdout are not novel broadly. Its static/last-measurement inpatient outcome is not a rolling outpatient CGM forecast or event-relation graph test. [Full Frontiers article](https://www.frontiersin.org/journals/endocrinology/articles/10.3389/fendo.2026.1816599/full). |
| Zheng et al., 2024, BG-BERT | OhioT1DM and DiaTrend glucose forecasts with aligned CGM, basal/bolus insulin and carbohydrate history; low-glucose detection is assessed at forecast points below 70 mg/dL for 30/60-minute horizons. Author-linked implementation is public. | The outcome is forecast-point threshold detection, not incident-within-horizon classification; partition unit is not shown to be participant-disjoint; no event-instance graph relation comparison. | Rules out novelty based only on multimodal event inputs or low-glucose forecasting. Preserve differences in endpoint and patient-level evaluation. [Author-hosted paper](https://sijieji.github.io/pdf/Glucose_Prediction_ICASSP_2024.pdf), [code](https://github.com/aiot-lab/BG-BERT), [DOI](https://doi.org/10.1109/ICASSP48485.2024.10446832). |
| Sun et al., 2026, future-aware sequence-to-sequence forecasting | Teacher uses historical CGM and future insulin/carbohydrate disturbance signals (IOB/COB); distilled student forecasts using historical inputs only. OhioT1DM and AZT1D; glucose trajectories up to 120 minutes. | Non-graph trajectory forecasting, not incident-low classification. Ohio supplied train/test split; AZT1D development/test described as first 80% / remaining 20%. | Event-aware sequences and information-availability handling are established. The candidate contribution must isolate event-instance relations under matched inputs and timing. [Publisher article](https://www.nature.com/articles/s41598-026-41787-7), [PubMed](https://pubmed.ncbi.nlm.nih.gov/41764313/). |
| Calzavara et al., 2026, PhyNet | CGM, insulin and carbohydrate glucose forecasting on T1DEXI and MetaboNet (848 people); counterfactual tests evaluate physiological response and unsafe recommendations. | PubMed abstract reviewed, full IEEE methods not retrieved; not an event graph or incident-low classification. | Predictive accuracy must be evaluated separately from explanation/physiological faithfulness and safety. [PubMed](https://pubmed.ncbi.nlm.nih.gov/42685163/), [IEEE](https://ieeexplore.ieee.org/abstract/document/11675927/). |
| Ibrahim et al., 2026, safety-oriented evaluation of neural digital twins | Five-seed patient-level comparisons on Manchester T1D-UOM and OhioT1DM; CGM, basal/bolus and meal events aligned on five-minute bins; IOB/COB proxies; counterfactual insulin/carbohydrate response analysis. | Patient-specific trajectory prediction, not unseen-patient incident-low prediction; non-graph models. | Matched event-aware controls and treatment-response plausibility evaluation are prior evaluation practices. Does not establish a graph relation test. [Full text](https://doi.org/10.3389/fendo.2026.1958918). |
| Akrong et al., 2026, explanation comparison for BG time-series | OhioT1DM BiLSTM; attention, saliency, integrated gradients, SHAP and LIME compared using feature deletion and noise stability, plus a scenario-based plausibility score. | Six people, one architecture; plausibility score is a heuristic and not clinician validation; no event graph. | Explainability assessment is established; any graph-explanation claim requires faithfulness evidence beyond displaying attention/subgraphs. [Full text](https://doi.org/10.1007/s44163-026-01328-7). |
| Chen et al., 2024, TRANS (IJCAI) | Temporal heterogeneous EHR graph with diagnosis, procedure, medication-code nodes, timestamped visit nodes, temporal edges/message passing, and graph explanations; next-visit diagnosis prediction on MIMIC-III, MIMIC-IV and CCAE. | General EHR diagnosis task, not T1D CGM forecasting; node semantics are coded concepts attached to visits rather than raw pump/meal transaction records. | Temporal patient event graphs with event nodes and explainers are established general methods. Limit any remaining novelty to the specific raw event transaction-to-CGM benchmark and its matched relation controls. [IJCAI version of record](https://ijcai.org/proceedings/2024/637), [DOI](https://doi.org/10.24963/ijcai.2024/637). |
| Jeffries et al., 2026 preprint, MetaboNet-Bench | Standardized multimodal T1D glucose forecasting with glucose, insulin and carbohydrates, model comparisons and modality ablations; a 30-minute primary prediction horizon and novel/known patient splits. | The task is glucose forecasting and clinical error evaluation, not the project's incident-low binary endpoint or event-instance graph-relation ablation. It nevertheless means benchmark and information-matched multimodal comparison are not new topics; differentiate the actual endpoint, event representation, controls and results. |

These boundaries are based on the cited papers and the full-text or abstract
material indicated in the [focused primary-source check](primary_source_novelty_check_2026_10_31.md),
[targeted prior-art update](targeted_prior_art_search_2026_10_31.md),
[prior-source addendum](closest_prior_work_event_graph_addendum_2026_10_19.md),
and [SysCon review](syscon_2026_prior_work_review.md). This is a targeted
search, not a systematic review. “Not established in inspected text” must
not be rewritten as “the prior work did not do this.”

## Additional close prior art verified 31 October 2026

The final targeted pass added an important methodological precedent: Li, Ge
and Chen explicitly represent event-time order as typed relations in a
dynamic knowledge graph and analyze AIM-94 diabetes event logs containing
insulin, glucose, hypoglycemic symptoms, meals and exercise. However, their
reported precision/recall prediction results concern mobile-system and
oil-well data; the diabetes material is used for event discovery and graph
analysis, not reported hypoglycemia-risk performance. This means event-order
knowledge graphs and their use with diabetes streams are prior art, while the
clinical prediction comparison remains distinct.

T1D input-context novelty is also ruled out by Zecchin et al. (2016), who
compared CGM with CGM-plus-insulin/meal inputs in 15 people for short-term
glucose regression, and by Dave et al. (2021), who separately compared
engineered insulin/carbohydrate context for short-horizon hypoglycemia risk.
Apicella et al.'s 2026 OhioT1DM preprint tests representation and context
levels for postprandial glycemic events and reports no systematic gain from
additional context. Oviedo et al. (2019) establish personalized meal/bolus
postprandial risk modeling, while Dave et al. (2021) also provide a sizeable
CGM-only sustained-low baseline. These studies use different tasks or
representations, but rule out novelty claims based on adding context,
patient-specific postprandial risk, or event-time graph construction alone.
See the [additional primary-source update](primary_source_novelty_update_2026_10_31.md)
and [targeted search addendum](targeted_prior_art_search_2026_10_31.md).

## Additional PubMed-indexed evidence checked 31 October 2026

The PubMed-focused follow-up identified Quader et al.'s 2026 systematic review
and meta-analysis (611 records screened, 20 included). Those counts describe
their review, not this project’s search. It confirms contextual inputs are an
established line of T1D hypoglycemia-prediction work, but does not answer the
event-instance graph question. Tziavaras et al. (2026) describe an OhioT1DM /
SMARTDIAB attention-LSTM for up to 12-hour nocturnal risk using 24-hour CGM,
meal, insulin and scheduled-basal inputs, with attention mapped to inputs.
Ferstad et al. (2024) report multi-cohort external validation for next-week
CGM-only risk. These further constrain broad novelty claims for multimodal
interpretability and risk prediction while differing in horizon, endpoint,
and representation. The current review still lacks native database exports
and its own PRISMA screening flow. See the [PubMed-indexed search addendum](targeted_prior_art_search_2026_10_31.md).

## Event-instance graph construction is not the novelty

Acharya and Lee (2014) already model timestamped diabetic event instances,
patient-linked event relations, temporal precedence, and causal network
structure over insulin, glucose, meal and hypoglycemic-symptom events. Li et
al. (2020) separately formalize typed event-time relations in a dynamic
knowledge graph and analyze diabetes logs. Postiglione et al. (2024) use
temporal patient KGs for future-disorder prediction in MIMIC-III. These works
make it untenable to claim novelty for representing temporal relations among
diabetic clinical events, event-instance graphs, or patient temporal KGs in
general. Their tasks differ from the current prospective-style CGM risk
classification comparison: causal network reconstruction, general stream
event timing, and hospital disorder prediction, respectively. The remaining
claim is empirical and task-specific: the effect of known event-relation
representations under matched information, timing, and capacity for this Loop
endpoint and participant split. The current two-seed, five-fold results favor
time-aligned non-graph pooling; hence the potentially publishable contribution
is the controlled comparison, including its negative graph result, if the
formal search and validation support it.

## 4. Recommended novelty wording

Suggested bounded statement:

> We conducted a retrospective, patient-disjoint Loop development comparison
> of an event-to-CGM graph and non-graph controls for prediction of any
> CGM-defined value below 70 mg/dL in the next 30 minutes. The graph exceeded
> one parameter-matched late-fusion event-sequence implementation in ten
> one-epoch fold-seed fits. Under a stricter two-epoch comparison with the
> same event inputs, timing, and parameter count, time-aligned event pooling
> had higher participant-macro average precision in all ten fold-seed fits
> and lower macro-Brier in nine. Averaging each participant’s paired effects
> across both fixed seeds gave graph-minus-pooling AP −0.009900 (95%
> fixed-prediction participant-bootstrap interval −0.010477 to −0.009345)
> and macro-Brier +0.0001264 (0.0001096 to 0.0001429). These results are
> specific to the Loop release, models, and tested schedules. A single
> eight-epoch outer-0 pair at another seed showed the same direction with a
> smaller gap, but does not establish convergence or seed-level stability.
> These results do not
> establish a general graph disadvantage, clinical relation validity, or
> clinical utility.

This wording attributes novelty to the **specific controlled empirical
question, event granularity, fixed cohort/endpoint, and resulting evidence**.
It does not claim that the graph is a validated knowledge graph or the first
of its kind. Before publication, a database-level systematic search should
test whether an equivalent event-instance matched comparison exists beyond
the primary sources reviewed here.

The 2026 MT-HypoNet study is a particularly close Loop comparator: it uses
two-hour histories and reports inter-patient five-fold Loop evaluation plus
30-minute hypoglycemia forewarning, but defines a hypoglycemia event as three
consecutive readings below 70 mg/dL. It describes insulin, carbohydrate, and
time inputs as optional without clearly identifying the channels used in its
headline Loop result. It does not report the event-instance graph versus
matched non-graph relation test posed here. Therefore, do not claim the first
Loop-trained forewarning model, the first patient-disjoint Loop evaluation, or
the first two-hour/30-minute setup. See the [31 October primary-source update](primary_source_novelty_update_2026_10_31.md)
for the evidence and remaining source limitations.

## 5. Work still required before a confirmatory paper

An access-compatible external evaluation route has been identified. A
follow-up strict window screen found 7,930,123 eligible
120-minute-history/30-minute-future windows in DCLP3 post-randomization data
(168 participants; 3.05% positive) and 5,113,177 numeric-only windows in DCLP5
(100 participants; 3.29% positive). Both include timestamped basal and bolus
events in the lookback for substantial subsets under the current timestamp
policy. DCLP3 baseline was excluded
because the release flags a participant's pre-admission CGM dates as
misaligned. DCLP5 required sorting, duplicate/conflict handling, and an
explicit low-sentinel sensitivity. These are release-local eligibility counts,
not model performance or external validation. The [DCLP audit](dclp_temporal_coverage_audit_2026_10_31.md)
records the window contract and remaining source-semantics gates; the window
and overlap counts need recomputation after timestamp policy is resolved.
Neither release has nonempty Roche carbohydrate records in the screened tables.
The follow-up pump-value screen found nonnegative numeric basal/bolus values.
Local Jaeb documentation describes basal rows as new-rate changes and DCLP5
boluses as amounts actually delivered. The DCLP5 glossary field name differs
from the released bolus column, units and zero-rate meaning remain unresolved,
and event availability is not recorded. Raw and adjusted timestamp fields
differ for substantial subsets, and Extended-bolus categories still need a
cross-release mapping. Raw-to-adjusted string differences are often many hours,
and a small number exceed 24 hours substantially; no shared timezone or
correction rule can be inferred from the strings alone. This narrows the
file-structure questions but does not
pass the event-semantics gate. A policy-controlled DCLP5 rerun found 9,981
more strict eligible windows and 286 more positive windows when adjusted CGM
timestamps were preferred versus raw CGM timestamps; raw-versus-adjusted event
time choices had smaller effects on aggregate lookback counts. The previous
eligibility screen mixed raw CGM with adjusted-preferred event times, so its
counts remain conditional until a justified clock policy is established. In
DCLP3, choosing adjusted-preferred rather than raw pump times changes the
number of eligible windows with both event types from 2,778,989 to 2,782,216,
while the CGM windows and labels remain fixed. See
the DCLP audit's
[pump-value and timestamp section](dclp_temporal_coverage_audit_2026_10_31.md#pump-value-and-source-timestamp-semantics-screen).

As a separate CGM-only diagnostic, the five frozen two-epoch Loop outer-fold
logistic models were replayed without refit on DCLP3 raw CGM timestamps and
DCLP5 under raw and adjusted-preferred CGM timestamp policies. All five
models beat the persistence-slope rule on participant-macro AP and Brier in
each cohort/policy, with outer-2 showing lower AP than the other folds. This
is not five independent replications because the same external participants
are reused. The outcome is release-local future CGM below 70 mg/dL, not an
adjudicated clinical episode. The models use only current CGM and recent
slope, and therefore do not validate insulin relations or the graph
hypothesis. Fixed-prediction participant intervals exclude refit, cohort, and
timestamp-policy uncertainty. See the detailed
[frozen-model transfer report](frozen_loop_cgm_jaeb_transfer_20261031.md) and
its identifier-free [DCLP3](../audit/dclp3_frozen_loop_cgm_logistic_transfer_raw_20261031_v3.json),
[DCLP5 raw](../audit/dclp5_frozen_loop_cgm_logistic_transfer_raw_20261031_v3.json),
and [DCLP5 adjusted-preferred](../audit/dclp5_frozen_loop_cgm_logistic_transfer_adjusted_20261031_v3.json)
artifacts.

The same-input, same-time-bin, same-parameter non-graph control is complete on
all five disjoint folds at each of two seeds and two epochs. A separate
eight-epoch pair is also complete on outer-0 at one seed. AP favors event
pooling in all ten fits; Brier favors pooling in nine of ten. The second seed
uses one frozen source digest across folds, while first-seed digests vary.
Current evidence still does not establish a general message-passing effect or
explain the earlier sequence-comparator difference. The next step is an
optimization/convergence study with a predeclared schedule and replicated
event-disabled controls, followed by realistic event-availability analysis.

1. **Convergence and training uncertainty:** the single-fold eight-epoch
   schedule check is partial progress only. Run more folds and independent
   seeds under a predeclared multi-epoch or convergence rule. Report model-fit
   variation; participant bootstrap intervals on fixed predictions are not a
   substitute.
2. **Replicated event-disabled and edge controls:** the graph event-disabled
   contrast is one fold/seed. Replicate it and use controls that retain event
   information while changing only the relation/endpoint mechanism. Preserve
   the effective-capacity caveat when zeroing inputs.
3. **Independent explanation test:** select attributions independently from
   the perturbation used to evaluate them, match random controls on event
   recency and value as well as modality, repeat across folds/seeds, and
   separate provenance validity from clinician usability.
4. **Availability:** obtain valid first-usable/arrival timestamps with enough
   coverage or restrict the claim to retrospective occurrence-time replay.
   The current upload linkage is not a real-time data contract.
5. **External insulin-only evaluation:** freeze a Loop-trained model and
   release-specific adapters, confirm basal-rate state semantics and time
   correction, reproduce the input/label identity, then score DCLP3/DCLP5
   without fitting on external outcomes. The window screen establishes
   feasibility only; it does not validate the model or meal-aware graph claim.
6. **Generalization and clinical evaluation:** external cohort harmonization,
   calibration/alert burden, episode-level operating metrics, subgroup
   analysis and one prespecified final-performance evaluation remain open.
7. **Broader prior-art search:** the OUP supplement for the closest 2026
   temporal time-point graph paper has now been inspected. Continue with a
   reproducible search of bibliographic databases for event-instance graph
   models and matched graph-vs-sequence diabetes benchmarks; check for code
   and full text when accessible. The GAT-BiGRU article body is listed as
   embargoed in PMC until 18 June 2027, so revisit its full methods then.

The ten aligned-control pairs ran on Apple M4 MPS in isolated Python 3.12
environments. Strict paired audits passed within every fold; all second-seed
runs share one source digest. First-seed source digests vary across folds and
an initially mismatched outer-4 graph artifact was excluded and replaced by
a source-matched rerun. The saved-prediction cross-seed participant summary
was regenerated in separate executions, and both regenerated JSON summaries
match their archived counterparts byte-for-byte. The two-seed participant
summary SHA-256 is
`22caa1fc0404e7c9107c1027a402df95e27ae4694662f06bd1011b37eb69627d`; the
seed-20261030 five-fold summary SHA-256 is
`5470b8b1e18d0f0745bc2ae235bad5995b670ceb6e295238952cf4cce5a66088`. The
recomputation scripts, digests, and aggregate metrics are in the
[recomputation receipt](../audit/novelty_recomputation_check_20261031.json).
The user's separate Kaggle session was left
untouched. Convergence, replicated event-disabled controls, measured event
availability, independent explanation validation, external-cohort validation,
and a systematic prior-art search remain open; no locked-holdout predictions
were accessed.

## Primary literature

- Onwuchekwa JID, Weber C, Maleshkova M. [Enhancing Hypoglycemia Prediction in Type 1 Diabetes through Semantic Knowledge Integration and Machine Learning Optimization](https://2024.eswc-conferences.org/wp-content/uploads/2024/05/77770363.pdf). ESWC 2024.
- Cakiroglu MO, Kurban H, Aljihmani L, et al. [A reinforcement learning approach to effective forecasting of pediatric hypoglycemia in diabetes I patients using an extended de Bruijn graph](https://www.nature.com/articles/s41598-024-82649-4). *Scientific Reports*. 2024;14:31251.
- Hüni F, Garcia-Tirado J, Riesen K. [LSTM Networks and Graph Neural Networks for Predicting Events of Hypoglycemia](https://link.springer.com/chapter/10.1007/978-3-031-80507-3_6). S+SSPR 2024, published online 2025.
- Hüni F. [Predicting Events of Hypoglycemia: A Comparison of Long Short-Term Memory and Graph Attention Network Based Approaches](https://prg.inf.unibe.ch/wp-content/uploads/2024/08/BA_FabianHuni.pdf). Bachelor thesis, University of Bern, 2024. This related author-work provides accessible methods and results; final chapter identity is not assumed.
- Zaitcev et al. [Automatic inference of hypoglycemia causes in type 1 diabetes: a feasibility study](https://www.frontiersin.org/journals/clinical-diabetes-and-healthcare/articles/10.3389/fcdhc.2023.1095859/full). *Front Clin Diabetes Healthc*. 2023.
- Rad FS, Hendawi R, Yang X, Li J. [Personalized Diabetes Management with Digital Twins: A Patient-Centric Knowledge Graph Approach](https://doi.org/10.3390/jpm14040359). *J Pers Med*. 2024;14(4):359.
- Piao C, Zhu T, Baldeweg SE, et al. [GARNN: An interpretable graph attentive recurrent neural network for predicting blood glucose levels via multivariate time series](https://doi.org/10.1016/j.neunet.2025.107229). *Neural Networks*. 2025;185:107229.
- Tziavaras K, Athanasiou M, Nikita KS. [Development of autoencoder-guided attention-LSTM models for predicting nocturnal hypoglycemia risk in Type 1 Diabetes](https://pubmed.ncbi.nlm.nih.gov/42224311/). *IEEE Trans Biomed Eng*. 2026. [Full-text availability and detailed split mechanics not checked.]
- Zhang Q, Saad SH, Zhou H, et al. [Development and validation of an interpretable machine learning model for predicting in-hospital hypoglycemia in adults with type 1 diabetes mellitus: a multicenter retrospective study](https://doi.org/10.3389/fendo.2026.1816599). *Front Endocrinol*. 2026;17:1816599.
- Sarwar MA, Maqsood S, Amini A, et al. [Explainable Multitask Graph Network for Blood Glucose Forecasting and Hypoglycemia Risk Classification](https://doi.org/10.1109/SysCon66367.2026.11503533). SysCon 2026. Methods reviewed from the [author-uploaded manuscript](https://www.researchgate.net/publication/404642556_Explainable_Multitask_Graph_Network_for_Blood_Glucose_Forecasting_and_Hypoglycemia_Risk_Classification); final publisher text was not accessible in this review.
- Sarwar MA, Maqsood S, Belousovienė E, Maskeliūnas R. [GAT-BiGRU: explainable multi-task temporal graph learning for glucose forecasting, hypoglycemia risk, and counterfactual insulin adjustment](https://doi.org/10.1093/jamia/ocag104). *J Am Med Inform Assoc*. 2026;33(9):1713–1725. [PubMed record](https://pubmed.ncbi.nlm.nih.gov/42314749/).
- Zaitcev A, Eissa MR, Hui Z, et al. [Automatic inference of hypoglycemia causes in type 1 diabetes: a feasibility study](https://www.frontiersin.org/journals/clinical-diabetes-and-healthcare/articles/10.3389/fcdhc.2023.1095859/full). *Front Clin Diabetes Healthc*. 2023;4:1095859.
- Jeffries N, Wolff M, Royston S, et al. [MetaboNet-Bench: A Multi-modal Benchmark for Glucose Forecasting in Type 1 Diabetes](https://arxiv.org/abs/2606.18640). arXiv:2606.18640v2, 2026 preprint.
- Khokhar PB, Gravino C, Palomba F. [Reliability-Aware Short-Term Glycemic Risk Prediction Using an Anchor-Based Comparative Framework of Sequence, Multimodal, and State-Updating Digital-Twin Models](https://arxiv.org/abs/2610.36363). arXiv:2610.36363v1, 2026 preprint.
- [Attention-Augmented Temporal Fusion Transformer for Short-Horizon Hypoglycemia Prediction in Type 1 Diabetes](https://doi.org/10.1016/j.eprac.2026.03.018). *Endocrine Practice*. 2026;32(4 Suppl):S336. Bibliographic record verified; publisher methods/abstract inaccessible in this review.


## Further context precedents from backward citation screening

The reference list of Quader et al.'s 2026 systematic review was used as a
backward-citation source; its 611 screened / 20 included studies are that
review's counts, not ours. Three additional primary studies sharpen the
novelty boundary. Bertachi et al. (2020) collected timestamped CGM, insulin,
meal and Fitbit activity/sleep data in ten adults with T1D for nocturnal risk
models; its small cohort and instance-pool split do not establish
patient-disjoint evaluation. Cichosz et al. (2015) compared CGM-derived
prediction with CGM plus heart-rate variability in 21 adults, but had only 12
hypoglycemic events. Mosquera-Lopez et al. (2023) modeled activity-related
risk using glucose, insulin exposure and activity in Tidepool, with a separate
T1DEXI pilot test set. These works establish that multimodal context,
incremental-context comparison and explainable risk modeling are not new
ingredients. They do not test the current raw event-instance relation
comparison. See the [targeted prior-art update](targeted_prior_art_search_2026_10_31.md)
and [Quader et al.](https://link.springer.com/article/10.1007/s40200-025-01820-4).

A further exact-title search verified Yu et al. (2024), an OhioT1DM nocturnal
warning model with asynchronous multimodal features and prior-knowledge-guided
dynamic attention. The paper analyzes 10 participant-specific datasets using
within-person temporal training/test periods, not held-out-patient evaluation.
It further rules out novelty based on multimodal asynchronous feature fusion
or guided attention alone. It does not use event-instance graph relations.
The current curated matrix contains 70 unique records; the source review
remains targeted rather than systematic. [Primary paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC11653906/),
[PubMed](https://pubmed.ncbi.nlm.nih.gov/39696373/).
