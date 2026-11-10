# Novelty and evidence report — updated 29 October 2026

## Executive finding

The project has a credible, narrowly framed empirical question, but **it has not demonstrated a novel knowledge-graph method or a replicated predictive benefit from graph relations**. A published 2024 diabetes PHKG paper and a T1D digital-twin project page updated in August 2026 describe patient-centric/semantic graph approaches, with the latter naming short-term hypoglycemia-onset prediction as a primary use case. Together with the ESWC and SysCon papers, these rule out broad novelty claims about patient-specific KGs or graphs for T1D hypoglycemia. Recent 2024–2026 primary studies also establish personalized, meal/insulin-informed, patient-wise temporal hypoglycemia/glucose prediction. A new exact-parameter-count comparison on one Loop development fold found graph-generic ahead of a non-graph event-sequence model given the same history and event inputs. This is preliminary evidence for the tested graph parameterization, not a replicated model-family result. Separately, the generic-edge branch slightly outperformed modality-typed routing, so no typed-relation benefit is established. Novelty remains provisional; the review has not established the absence of an equivalent comparison.

The current Loop results are useful but limited development evidence. In one outer-fold and one seed, a CGM-history-only model performed better than its nearly parameter-matched history-plus-event counterpart. Earlier event-summary and short event-sequence pilots also failed to improve AP over their CGM references. The exact-capacity graph-versus-sequence control favors graph-generic across two seeds and five folds; the separate modality-typed routing screen is mixed. An outer-0 event-disabled comparison modestly favors retaining event inputs. The matched causal endpoint perturbation is complete across five folds for each of two seeds: nearest endpoints yield higher participant-macro AP and lower macro-Brier in 8/10 seed-fold pairs. A participant-cluster bootstrap that averages each participant's paired differences over both fixed seeds gives +0.002097 AP (95% interval +0.001761 to +0.002443) and −0.0000773 macro-Brier (−0.0000957 to −0.0000594). This is evidence of sensitivity to this particular edge-target assignment, conditional on two fixed seeds; it does not estimate training-seed uncertainty or establish clinical relation benefit. The experiments do not establish a novel KG method, explanation faithfulness, or performance on other populations.

**New fixed-checkpoint timing control, 29 October 2026:** within-window event-age reassignment was evaluated on the saved graph-generic epoch-1 checkpoints across five patient-disjoint folds for two fixed seeds. It preserves each window's event content and age multiset while breaking event-to-time pairing. The original pairing had higher AP in all 10 seed-fold fits, with mean difference +0.0001118, but only 3/10 fold-specific participant intervals excluded zero. Macro-Brier direction was split evenly; 4/10 intervals excluded zero. The same 652 people recur across seeds, so these intervals are not pooled and the ten fits are not independent. This is a small fixed-fit sensitivity to one deterministic timing reassignment, not a relation-validity, causal, or explanation-faithfulness result. Clean replay metrics and exact prediction-window identities reproduced for all ten checkpoints, although original training source digests are not reconstructable from the current workspace. See the [control protocol and results](loop_event_age_reassignment_control.md) and [two-seed aggregate](../audit/loop_event_age_reassignment_two_seed_five_fold_summary_20261029.json).

The graph pilot used 130 validation participants and 8,885,621 paired windows. Generic versus typed participant-macro AP was 0.474481 vs 0.471859 (typed-minus-generic −0.002622; 95% paired participant-bootstrap interval −0.003386 to −0.001909). Participant-macro Brier was 0.021522 vs 0.021619 (typed-minus-generic +0.0000974; interval +0.0000758 to +0.0001213). Both variants had 36,883 parameters and identical input, split, seed, and one-epoch budget. See the [detailed pilot report](loop_temporal_relation_pilot.md) and [audit receipt](../audit/loop_temporal_relation_outer0_paired_pilot.json).

The direct graph-benefit control then compared graph-generic with a non-graph
dual-GRU receiving the same 24-slot CGM history and up to 64 timestamped event
instances. Both had exactly 36,883 trainable parameters and used the same
outer-0 fold, seed `20261003`, one epoch, optimizer and data. The paired
comparison covered 130 participants and 8,885,621 rows. Graph-generic AP was
0.474481 versus 0.389901 (difference +0.084580; 95% participant-bootstrap
interval [+0.078104, +0.090816] from a 10,000-draw follow-up (bootstrap seed
`20261019`)); graph AP was
higher for 126/130 participants.
Macro Brier was 0.021522 versus 0.024211 (difference −0.002690; 95% interval
[−0.003043, −0.002347] from the same follow-up), and graph Brier was lower for
all participants. The fixed-prediction interval does not quantify refit variability. The full Kaggle
archive was downloaded, checksum-verified and independently re-compared
locally; a further fresh local run on 19 October reproduced all reported paired
metrics and contract fields exactly. See the [matched control report](loop_non_graph_capacity_matched_control.md),
[paired audit](../audit/loop_graph_vs_capacity_matched_outer0_paired.json),
[10,000-draw sensitivity audit](../audit/loop_graph_vs_capacity_matched_outer0_paired_10000draws_20261019.json), and
[independent 19 October recheck](../audit/loop_graph_vs_capacity_matched_outer0_independent_recheck_20261019.json).

An outer-1 matched replication was launched in Kaggle. Final downloaded logs at
00:32 UTC showed graph-generic at 50.9% and the non-graph sequence control at
47.8% of their one-epoch training passes. The Kaggle session then switched off
at its 12-hour boundary. Final refreshed run directories listed only `run.json`;
neither fit produced a checkpoint or validation predictions. This attempt is
incomplete and contributes no replication evidence. The partial logs are
preserved in the [termination record](../audit/loop_outer1_terminated_partial_20261019.json)
and [recovery bundle](../private/kaggle_artifacts/loop_outer1_terminated_partial_20261019_bundle.zip);
the next replication requires an available runtime and a verified resumable
checkpoint policy for the newly optimized source. Colab has not run this
replication: the saved seed-replication notebook is not the graph-versus-sequence
campaign, its current page reports `Connect T4`, and its diagnostics show the
required local and Drive input paths are absent. The Drive history-cache ZIP has
now been located and downloaded; its checksum exactly matches the already
validated local archive. The base input and history cache pass the local
full-history preflight, but they have not been staged into Colab. See the
[full handoff](kaggle_outer1_replication_handoff_2026_10_19.md) and the
[download integrity receipt](../audit/loop_history_drive_download_verification_20261019.json).
The latest Kaggle view shows the draft session off, the `Loop Temporal Relation
Pilot` event cancelled after 13 hours, and 0 active events; the account also
warns it is almost out of compute quota. No training is currently running.

This outer-1 attempt is distinct from the existing `Loop Sequence T1D
Controlled Comparison` draft inspected on 19 October. That page showed a
19h12m-running draft session, 0 Active Events, and the completed prior
history-only versus history-event comparison. A fresh tab of the saved draft
showed the full-history development input among its attached datasets, but its
console reported `Failed to fetch` and its session was off in that tab. The
existing session was left untouched. No new outer-1 fit or relation pilot was
launched; these browser states do not change the incomplete-replication
conclusion above.

## Novelty against the literature

A focused 19 October primary-source update adds a 2024 patient-centric diabetes PHKG paper, an active institutional T1D semantic-graph project whose stated use case is short-term hypoglycemia onset, a 2024 personalized short-horizon hypoglycemia model, a 2026 patient-wise hour-ahead temporal predictor, the 2025 meal-indexed hypoglycemia study, and the 2026 T1-DEXI event-input/LSTM comparator. Patient-centric graphs, temporal patient-wise prediction, treatment-event inclusion, and a sequence baseline are therefore not sufficient novelty claims. The candidate question remains whether explicit relations among individual event instances help for the rolling incident-low target under matched information, timing, capacity, and relation perturbations. The search does not establish absence of equivalent work. See the [19 October focused prior-work addendum](closest_prior_work_event_graph_addendum_2026_10_19.md) and [literature search log](literature_search_log.md).

| Prior work | What it already establishes | What remains different here |
|---|---|---|
| Onwuchekwa et al., ESWC 2024 paper and 2025 dissertation, [“Advancing Personalized Hypoglycemia Prediction”](https://doi.org/10.25819/ubsi/10693) | Direct prior work on patient-specific semantic KGs, ontologies, temporal semantics, text mining and graph embeddings for T1D hypoglycemia. The dissertation describes preliminary MIMIC-III glucose prediction for one patient. | The inspected dissertation chapter characterizes the KG/ML work as early-stage; it does not report an information-matched, patient-disjoint outpatient CGM benchmark or event-relation ablation. This does not establish absence elsewhere. KG construction or semantic patient-specific representation is not novel here; our candidate distinction remains a controlled event-instance relation study, provisional pending relation controls. |
| Sarani Rad et al., [patient-centric diabetes PHKG/digital twin, 2024](https://doi.org/10.3390/jpm14040359) | A patient-centric personal-health-KG framework integrates diabetes data through HL7 and describes glucose-prediction, insulin-optimization, lifestyle and visualization applications. | Conceptual and application-level precedent; it does not report the present rolling incident-low relation benchmark. |
| Helmut-Schmidt-Universität, [Digital Twins for Diabetes Management project](https://www.hsu-hh.de/dataeng/en/research/current-projects/digital-twins-for-diabetes-management/) | The institutional page updated 6 August 2026 describes a semantic graph-based DiaData representation for T1D and short-term hypoglycemia-onset prediction as a primary use case. | This is an ongoing project description, not a completed published evaluation; it does not give a matched event-instance relation experiment. It prevents a broad claim of conceptual novelty for semantic T1D graph plus hypo prediction. |
| Sarwar et al., JAMIA 2026, [GAT-BiGRU](https://doi.org/10.1093/jamia/ocag104) | A temporal graph model for multimodal glucose forecasting and 30/60-minute hypoglycemia risk, evaluated on OhioT1DM and BrisT1D, with GNNExplainer and counterfactual insulin adjustment. Its graph represents feature-enriched time points linked by historical neighborhoods. It directly rules out broad claims of the first temporal graph or explainable graph model for T1D hypoglycemia. | The abstract describes time-point history edges; it does not establish the event-instance relation ablation sought here. The full methods and supplement need review before making finer distinctions. |
| Sarwar et al., SysCon 2026, [author-uploaded full manuscript](https://www.researchgate.net/publication/404642556_Explainable_Multitask_Graph_Network_for_Blood_Glucose_Forecasting_and_Hypoglycemia_Risk_Classification) | BrisT1D; fixed seven-modality physiology graph with directed insulin/carbohydrate/activity relations; graph instances at each prediction time use rolling-window feature summaries and circadian context; GATv2; future glucose and 5/15/30-minute point-threshold risk outputs. The manuscript reports node ablation, top-attended-edge deletion/reinsertion, random edge-drop comparisons and attention/prior correlation. | Its label is future-point glucose below 3.9 mmol/L, unlike incident any-low-within-interval labels. The accessible split description is stratified but does not establish participant-disjoint assignment. This is an author-uploaded version; final IEEE version and independent reproduction are unavailable here. The inspected representation differs from individual transaction/event instances, but that gap remains an inference, not an exhaustive novelty result. |
| Taku et al., JMIR Diabetes 2026, [personalized RL and glucose forecasting](https://doi.org/10.2196/79195) | OhioT1DM 2018/2020 with 12 participants; CGM, pump insulin, self-reported meals and activity, and wearable signals. A two-hour state uses lagged/rolling/time features including time since last insulin and meal; the study forecasts glucose at 30/60 minutes and explains decisions with SHAP/LIME. Event-aware T1D glucose forecasting and explanation therefore predate this project. | It is a small-cohort RL/dosing and glucose-forecasting study, not a knowledge graph or matched typed-relation ablation for incident hypoglycemia. It further raises the bar: a contribution cannot rest on putting meal/insulin events into an explainable T1D predictor; it must isolate the value of event-instance relation structure under matched information and timing. |
| Athanasiou et al., [personalized interpretable hypoglycemia models, EMBC 2024](https://doi.org/10.1109/EMBC53108.2024.10781638) | Uses CGM, insulin, and meal information from 12 people with T1D for personalized 0–30- and 30–60-minute hypo-risk prediction with TreeSHAP. | The inspected abstract does not describe a knowledge graph or matched event-instance relation comparison; the small cohort and detailed split need method-level scrutiny. |
| Rehman et al., [meal-indexed postprandial glycemic-event prediction, PLOS Digital Health 2025](https://doi.org/10.1371/journal.pdig.0000996) | Uses meal/carbohydrate and bolus context and predicts hypoglycemia within four hours of meal onset; low glucose is ≤70 mg/dL for at least 15 minutes. | A meal-indexed endpoint differs from rolling incident-low prediction. It does not establish the value of event-instance graph relations against matched sequences. |
| [JMIR AI 2026 T1-DEXI glucose forecasting study](https://ai.jmir.org/2026/1/e105049) | Timestamped meals and boluses encoded on five-minute grids; 351 T1D adults; patient-wise split; TFT configurations plus an LSTM with aligned inputs for continuous glucose forecasting. | Event timing, patient-wise evaluation, and a sequence comparator are prior work. Its task is continuous glucose forecasting, and it tests nutritional detail rather than graph relations for the rolling low-event target. |
| Alkhateeb et al., [hour-ahead Ramadan hypoglycemia prediction, 2026](https://pmc.ncbi.nlm.nih.gov/articles/PMC13119999/) | Patient-wise 36-hour recurrent sequences over hourly CGM/wearable summaries; predicts any ≤70 mg/dL in the next hour among adults with T1D. | It establishes a close temporal hypoglycemia-prediction precedent, but uses aggregated wearable/context features rather than individual treatment-event nodes or KG relations. |
| Pyatak et al., [person-centered temporal network models](https://doi.org/10.1007/s12529-026-10483-1), 2026 | Individual temporal networks connect CGM with momentary symptoms, emotions and functioning for 158 adults with T1D over 14 days. This is a patient-centered temporal-network precedent. | The study analyzes individualized relationships and well-being, not near-term hypoglycemia forecasting or a treatment-event knowledge graph. It does not test predictive value from typed event relations. |
| Fang et al., [MT-HypoNet](https://doi.org/10.1016/j.isci.2026.115294), 2026 | Multitask CGM forecasting and hypoglycemia forewarning evaluated on a multicenter retrospective cohort of 1,662 people with T1D/T2D, external datasets, and prospective T2D cases. This establishes that large-cohort forecasting and hypoglycemia forewarning are active prior work. | It is not a typed event-relation or knowledge-graph study and has different populations and evaluation targets. Do not compare headline scores with Loop or present model scale alone as novelty. |
| Piao et al., [GARNN](https://arxiv.org/abs/2402.16230) | Graph-attentive recurrent glucose forecasting over multivariate time series, including insulin and meal signals, with variable-level explanations across multiple datasets. Graph attention plus recurrent modeling and event-aware glucose forecasting are not novel by themselves. | The project’s remaining candidate is an information-matched comparison of explicit clinical event relations against equally informed sequence and endpoint/time controls for incident hypoglycemia. |
| Hüni et al., [CGM visibility-graph work](https://github.com/fabianHueni/cgm-visibility-graph-dataset) | CGM can be represented with visibility graphs for hypoglycemia prediction. | It is a CGM-series graph, not evidence that patient-event relations add value. It belongs in the comparator review. |
| Aboye et al., [SparGlu (2026)](https://doi.org/10.1002/jim4.70055) | OhioT1DM glucose prediction has been evaluated with CGM, insulin and meal variables under progressively sparse sampling. Sparse-data robustness and multimodal time-series use are not new by themselves. | This does not answer whether typed event relations help under matched patient-disjoint hypoglycemia prediction. |

These are primary-source leads, not a systematic review. The literature search log records scope and access limits. Targeted 18 October checks added the full University of Siegen dissertation, the 2026 JMIR event-aware OhioT1DM study, a person-centered temporal-network study, and the multicenter MT-HypoNet paper. The 2026 literature makes broad claims about patient-centered graphs, temporal relations, event-aware T1D prediction, explainability, or scale untenable. The remaining candidate is narrower: a controlled test of whether an explicit relation parameterization over individual recorded events improves incident-risk prediction over matched event-sequence and endpoint/time controls. Do not compare headline metrics across these studies and Loop; cohorts, labels, splits and tasks differ.

## What has actually been analyzed

Loop is the **only cohort used for model training and validation** in the current evidence set. AIDE, DCLP3, DCLP5 and FLAIR were screened or audited for data suitability; they do not yet supply model results or external validation. AIDE has CGM and treatment-period context but no identified timestamped insulin-delivery, meal or activity event stream. DCLP3 and DCLP5 are insulin–CGM candidates but their reviewed carbohydrate fields are empty. FLAIR has daily treatment summaries rather than the event-level inputs needed for this relation claim.

The frozen Loop index has 56,375,850 eligible windows from 835 participants. The development caches contain 44,028,064 windows from 652 participants; the protected holdout has 183 participants and 12,347,786 windows. The primary full-history runs used the outer-0 validation set: 130 participants, 8,885,621 windows and 274,044 positive labels. The predictive holdout has not been scored; aggregate cohort coverage was audited during data preparation.

Event recording is incomplete at the window level. In 56,375,850 frozen 120-minute windows, 11,400,398 (20.22%) had no retained basal, bolus or food record, and only 12,771,176 (22.65%) had all three. Absence of a retained record is not evidence that no clinical event occurred. The event cache contains unknown-valued records and same-time variants. Event replay uses occurrence time and assumes immediate availability; validated first-usable timestamps are not available for the model cohort. Therefore no real-world delayed-reporting or bitemporal robustness claim is supported.

## Verified development evidence

All comparisons below use outer-0 validation and fixed saved predictions. Participant-bootstrap intervals quantify variation across these participants **conditional on the fitted predictions**; they do not include retraining, model-selection, fold or cohort uncertainty.

| Comparison | Participant-macro AP (first vs second) | Paired AP difference and 95% interval | Brier / interpretation |
|---|---:|---:|---|
| CGM-only MLP vs clean-GRU control, first gate | Seed 20261002: 0.48160 vs 0.46933; seed 20261004: 0.48213 vs 0.47350 | MLP−GRU AP: +0.01227 [ +0.01037, +0.01414 ] and +0.00863 [ +0.00692, +0.01029 ] | Direction repeated in two fits on the same outer-0 cohort; CGM-only has lower participant-macro and pooled Brier in both. This is not independent-cohort replication, and neither arm tests KG relations. |
| Corrected CGM logistic vs recorded-event summary logistic | 0.45706 vs 0.42577 | −0.03129 [ −0.03780, −0.02544 ] for event minus CGM | Event-summary model also has worse Brier. Negative evidence for this 14-feature summary setup only. |
| Frozen CGM logistic vs selected event residual | 0.45706 vs 0.44409 | −0.01296 [ −0.01552, −0.01036 ] for residual minus CGM | Residual has slightly better Brier but lower AP. The residual is an additive summary-feature branch, not a graph. |
| Frozen CGM logistic vs 16-event linear sequence residual | 0.45706 vs 0.40251 | −0.05454 descriptively | 38.64% of windows truncated at 16 events. This is an inadequate diagnostic, not a fair rejection of event sequences. |
| Full 24-step CGM history vs full history plus up to 64 events | 0.47187 vs 0.46053 | +0.01133 [ +0.00934, +0.01321 ] for history-only minus history+events | History-only has lower macro Brier by 0.000482 (95% [−0.000576, −0.000394]) and lower pooled Brier by 0.000462. Parameter counts are 36,607 vs 36,609. One seed and fold; architectures differ in where capacity is allocated, and no graph relation is tested. |
| Full-history event model vs same-architecture event-disabled branch | 0.46053 vs 0.46946 | −0.00893 [ −0.01040, −0.00736 ] for event-enabled minus event-disabled | Event-disabled has lower macro Brier by 0.000273 (95% difference event-enabled minus disabled [ +0.000205, +0.000342 ]) and lower pooled Brier by 0.000247. Both declare 36,609 parameters, but the disabled event encoder receives no gradients, so effective capacity is not matched. One seed/fold/two epochs; no graph relation is tested. |
| Epoch-1 full-history history-only vs history+events | 0.43014 vs 0.39708 | +0.03307 [ +0.03038, +0.03576 ] for history-only minus history+events | Paired on the same 130 participants and 8,885,621 windows. History-only has lower macro Brier by 0.000893 (95% [−0.001016, −0.000774]) and lower pooled Brier by 0.000857. This is a checkpoint optimization diagnostic, not a converged-model comparison. |

The recovered history-event epoch-1 checkpoint scores 0.39708 participant-macro AP and 0.02421 macro Brier; its epoch-2 checkpoint scores 0.46053 AP and 0.02184 macro Brier on the same windows. The paired epoch-2 minus epoch-1 AP gain is 0.06345 (95% fixed-prediction participant-bootstrap interval 0.05779 to 0.06860), and macro Brier improves by 0.002372 (interval 0.002077 to 0.002700). The history-only model also improved from epoch 1 to epoch 2. Both results show that the fixed two-epoch runs were still optimizing; do not interpret the epoch-1 cross-model gap as a model-quality conclusion.

The fixed first gate has now been reproduced with a second seed on the same 130 outer-0 validation participants. Across seeds 20261002 and 20261004, the CGM-only MLP had higher participant-macro AP and lower participant-macro and pooled Brier than the clean-GRU control in both fits. The paired AP differences were +0.01227 and +0.00863, respectively. The seed-specific paired intervals condition on each fit's saved predictions; the two seeds share participants, so they do not establish independent-cohort replication or estimate training-seed uncertainty. See the [machine-readable two-seed summary](../audit/loop_first_gate_two_seed_summary_20261018.json) and [verified seed-20261004 report](loop_seed20261004_second_gate_result.md). This replication strengthens the baseline direction only; it provides no evidence about KG relations.

The full-history archive checksums and ZIP contents were rechecked on 17 October 2026. The two epoch-2 participant prediction sets were independently recomputed and aligned on participant, index time and label. The history-only epoch-1 checkpoint replay was also verified against the original checkpoint and paired with its epoch-2 predictions. It improved AP from 0.43014 at epoch 1 to 0.47187 at epoch 2 in that fit; this is an optimization diagnostic, not convergence evidence.

A corrected directory-aware Kaggle runner completed a same-seed rerun on 18 October. Its paired report again favored history-only over history-plus-events: AP 0.471865 vs 0.460532 (difference +0.011334; 95% paired participant-bootstrap interval +0.009345 to +0.013209), with lower macro and pooled Brier for history-only. The aggregate and both branch bundles were recovered locally; ZIP integrity passed, all 8,885,621 validation windows aligned, and recomputation from the saved predictions matched Kaggle's paired metrics within 1e-15. This verifies the rerun and archive, not independent seed or fold replication. See the [independent reproduction record](../audit/loop_full_history_corrected_rerun_reproduced_20261018.json) and [live-run receipt](../audit/loop_full_history_live_kaggle_recheck_20261018.json).

The **history-event epoch-1 checkpoint replay is complete and independently verified**. After repairing Kaggle's split cache mount, the loader passed an exact feature-row parity check on partitions 2 and 3 (3 participants, 140,253 windows); the content was revalidated against the original receipt; and all 8,885,621 outer-0 validation windows were scored with identity hash `a68ad87255e8b8944b269a6995489640ee6b37576799e917d548a0d161700224`. The recovered bundle matches Kaggle's SHA-256 and passes ZIP integrity. Its paired epoch-1-versus-epoch-2 result shows substantial improvement at epoch 2, so the one-seed, two-epoch comparison is an optimization diagnostic rather than a converged-model test. The later event-disabled control is also recovered and independently reproduced locally; it favors the disabled branch, with the effective-capacity limitation described above. During the 18 October run, the stale editor tab still showed the old archive-only assertion while the separate corrected T4 x2 run completed; the stale traceback was not from the verified run. Use the [directory-aware notebook](../kaggle_event_sequence_gru/loop_full_history_comparison_input_fix.ipynb). See the [replay handoff](loop_full_history_epoch1_event_replay_handoff_2026_10_17.md) and [cache-discovery fix](kaggle_history_cache_discovery_fix.md).

## Novelty judgment and manuscript-safe wording

**Current judgment:** the broad concept is not novel; the narrow empirical contribution is plausible but remains provisional after the SysCon manuscript review. Current data support a positive graph-generic versus capacity-matched sequence comparison and a negative typed-versus-generic routing comparison. Endpoint perturbation changes results in a mostly consistent direction across the two-seed screen, but it only tests one graph construction choice. Neither a new KG method nor typed physiological graph edges nor graph explanation/edge-faithfulness analyses can be presented as new.

**Cross-hardware fit check — 19 October 2026:** the graph-generic and exact-capacity non-graph sequence variants were also freshly trained on the local Apple M4 MPS device. Their development input, outer-0 split, seed `20261003`, one-epoch budget, optimizer, and 36,883-parameter count matched; the full preflight and prediction identity checks passed. Graph AP was 0.475384 versus 0.394764 (paired difference +0.080620; 10,000-draw participant-bootstrap 95% interval [+0.071498, +0.089245]); graph AP was higher for 114/130 participants. Macro Brier was 0.021945 versus 0.023899 (difference −0.001953; interval [−0.002211, −0.001708]). This repeats the Kaggle direction on a second execution backend, but it remains the same fold and seed, not independent-cohort or seed replication. Fixed-fit intervals do not include refit variability. See the [MPS control record](loop_non_graph_capacity_matched_control.md#local-apple-mps-cross-hardware-fit--19-october-2026) and [paired audit](../audit/loop_mps_outer0_graph_vs_sequence_paired_20261019.json).

The exact-capacity non-graph dual-GRU control is implemented at 36,883 parameters and has completed one outer-0 training fit. A strict paired comparator verified the same input, split, participant membership, prediction rows and training budget. The graph model led in this screening comparison; the result still requires fold/seed replication and does not identify the clinical meaning of any edge. The raw bundle is locally preserved at `private/kaggle_artifacts/loop_graph_vs_capacity_matched_outer0_20261019_bundle.zip`. See [control design and result](loop_non_graph_capacity_matched_control.md).

Suggested current wording:

> In Loop development data, a graph-generic model with 36,883 parameters outperformed an information-matched non-graph event-sequence model with the same parameter count on paired average precision and Brier score across two seeds and five patient-disjoint folds. A separate five-fold screen found mixed results for modality-typed routing. In a matched nearest-versus-second-nearest causal endpoint perturbation, nearest endpoints had higher participant-macro AP and lower macro-Brier in 8 of 10 seed-fold pairs. A participant-cluster bootstrap averaged over the two fixed seeds estimated +0.002097 AP (95% interval +0.001761 to +0.002443) and −0.0000773 macro-Brier (−0.0000957 to −0.0000594). This remains an endpoint-sensitivity result conditional on two one-epoch fits, not evidence that clinically valid relations generally improve prediction; the tested edges are not independently annotated clinical facts.

If numerical results are reported, the graph-generic model scored
participant-macro AP 0.474481 versus 0.389901 (difference +0.084580; 10,000-
draw participant-bootstrap 95% interval [+0.078104, +0.090816]) and Brier
0.021522 versus 0.024211 (difference −0.002690; 95% interval
[−0.003043, −0.002347]). The intervals condition on these two fitted models;
they do not measure variation from retraining or other folds. The point
estimates are identical to the original paired audit, and the 10,000-draw
intervals are recorded in the [sensitivity audit](../audit/loop_graph_vs_capacity_matched_outer0_paired_10000draws_20261019.json).

Do **not** write “first temporal patient-centric KG,” “relations improve prediction,” “event data are uninformative,” “real-time explanation,” “clinically deployable,” or “externally validated.” A more specific novelty claim may become supportable only if the relation experiment distinguishes timestamped event-instance resolution from fixed modality summaries and sequence encodings, uses the same event information and prediction-time policy, replicates across training seeds with an appropriate multi-epoch budget, tests event-order and relation-shuffle controls, and measures explanation faithfulness. Even then, the contribution would be a controlled empirical result, not a first graph architecture or globally first use of relations.

## Execution gates still required for the proposed paper

1. Replicate the matched graph-generic versus sequence contrast and generic-versus-typed graph contrast across all development outer folds and at least three fixed seeds, using a prespecified common multi-epoch budget. Report participant-level uncertainty and correct AP-defined denominators; fixed-prediction bootstrap alone is not training uncertainty.
2. The nearest-versus-second-nearest causal endpoint perturbation is now complete across five folds for two seeds. Its result is limited to sensitivity to this edge-target rule. Extend the event-disabled control beyond outer-0, and test shuffled relations and event-order perturbations while preserving the event information appropriate to each control; these are still needed to distinguish relation structure from ordering and input effects.
3. Measure event capture and provenance; use actual arrival times only if validated. Otherwise label imposed delays as scenario sensitivity and do not claim empirical deployment-time availability.
4. Evaluate explanation fidelity by deleting raw events and rebuilding all derived features/edges; test stability under information-matched perturbations. No such explanation-faithfulness experiment is complete.
5. Freeze the protocol, then score the locked holdout once. Seek external validation only with compatible common fields and permission; the four screened auxiliary cohorts have not yet supplied external model evidence.

## Reproducibility pointers

- [Machine-readable evidence inventory and archive checksums](../audit/novelty_evidence_inventory_20261017.json)
- [Paired first-gate result](../audit/loop_controlled_first_gate_paired_2026_10_05.json)
- [Two-seed first-gate summary](../audit/loop_first_gate_two_seed_summary_20261018.json)
- [Event-summary paired result](../audit/loop_event_vs_cgm_outer0_validation_v3.json)
- [Event-residual paired result](../audit/loop_event_residual_outer0_best_vs_frozen_cgm.json)
- [Full-history paired result](../audit/loop_full_history_paired_recovered_20261017.json)
- [18 October independent recomputation of full-history comparison](../audit/loop_full_history_paired_recheck_20261018.json)
- [18 October corrected-run archive and prediction reproduction](../audit/loop_full_history_corrected_rerun_reproduced_20261018.json)
- [Additional independent paired-comparator reproduction](../audit/loop_full_history_independent_pair_reproduction_20261018.json)
- [Strict history-only epoch comparison](../audit/loop_full_history_history_only_epoch1_vs_epoch2_strict_20261017.json)
- [Strict history-event epoch comparison](../audit/loop_full_history_history_event_epoch1_vs_epoch2_strict_20261017.json)
- [Epoch-1 history-only vs event paired comparison](../audit/loop_full_history_history_only_vs_event_epoch1_20261017.json)
- [Full-history event vs event-disabled paired comparison](../audit/loop_full_history_event_zero_ablation_outer0_seed20261003_20261017.json)
- [Graph-generic vs capacity-matched non-graph sequence paired comparison](../audit/loop_graph_vs_capacity_matched_outer0_paired.json)
- [10,000-draw graph-vs-sequence bootstrap sensitivity audit](../audit/loop_graph_vs_capacity_matched_outer0_paired_10000draws_20261019.json)
- [Independent 19 October recheck of graph-vs-sequence comparison](../audit/loop_graph_vs_capacity_matched_outer0_independent_recheck_20261019.json)
- [Fresh exact rerun of the 10,000-draw paired graph-vs-sequence analysis](../audit/loop_graph_sequence_local_rerun_20261019.json)
- [Current execution status and local recheck inventory](../audit/novelty_evidence_inventory_20261017.json)
- [Independent reproduction from the recovered Kaggle archive](../audit/loop_full_history_event_ablation_verified_reproduction_20261017.json)
- [18 October independent recomputation of event ablation](../audit/loop_full_history_event_ablation_recheck_20261018.json)
- [Full-history run recovery and limits](loop_full_history_result_2026_10_17.md)
- [Literature search and access log](literature_search_log.md)

## Outer-1 MPS paired replication — 19 October 2026

A second patient-disjoint fold was trained locally on Apple MPS using the
same one-epoch, seed `20261003`, batch-4096, AdamW, 36,883-parameter contract
for the graph-generic and non-graph capacity-matched sequence models. Both
runs consumed all 25,756,087 expected training windows and produced verified
predictions on the same 9,386,356 outer-1 validation windows from 141
participants (270,499 positive labels). Both used the same manifest, input,
training-membership and prediction-window identity digests; the locked holdout
was not used.

Graph-generic scored participant-macro AP **0.460125** and macro Brier
**0.020059**. The matched sequence model scored AP **0.378379** and macro Brier
**0.022213**. In a paired bootstrap over fixed participant predictions
(10,000 draws), graph-minus-sequence AP was **+0.081746** (95% interval
**[+0.073130, +0.090150]**); graph AP was higher for 126/140 AP-defined
participants. Macro Brier difference was **−0.002153** (95% interval
**[−0.002476, −0.001836]**); graph Brier was lower for 126/141 participants.
These intervals quantify participant resampling conditional on these fitted
models, not retraining or fold uncertainty.

The direction is consistent with the outer-0 pair on the same seed and
hardware, so the graph-generic advantage has now appeared in two patient
folds. This is still **not a seed replication**: both folds share seed
`20261003`; each uses a one-epoch exploratory fit, and the graph and sequence
architectures are not identical except for parameter count and data/training
contract. The evidence supports only this tested graph parameterization over
this matched sequence control. Relation-shuffle, endpoint/time reconstruction,
event-order controls and broader seed replication remain necessary before
attributing the advantage to clinical relation semantics or making a novelty
claim. Event availability remains retrospective occurrence-time replay with
immediate availability assumed, not measured.

The participant-paired result is
[`audit/loop_mps_outer1_graph_vs_sequence_paired_20261019.json`](../audit/loop_mps_outer1_graph_vs_sequence_paired_20261019.json);
the run directories and checkpoints are protected under
`private/mps_research/outer1_seed20261003_{graph_generic,sequence_mps}/`.

## Outer-2 MPS paired replication — 19 October 2026

The same graph-generic versus non-graph sequence comparison completed on
outer-2, still using seed `20261003`, one epoch, batch size 4096, and the
36,883-parameter matched budget. Both models verified predictions on the same
8,395,597 validation windows, 124 participants and 229,814 positive labels;
their prediction identity digests match. The locked holdout was not used.

Graph-generic scored participant-macro AP **0.453164** and macro Brier
**0.019544**; the sequence model scored AP **0.379705** and macro Brier
**0.021474**. The paired 10,000-draw participant-bootstrap AP difference was
**+0.073460** (95% interval **[+0.064308, +0.082407]**), with graph AP higher
for 111/124 participants. Macro-Brier difference was **−0.001930** (95%
interval **[−0.002230, −0.001638]**), with graph Brier lower for 114/124.
The interval conditions on these fitted predictions.

Across the three completed MPS folds at seed `20261003`, the paired
graph-minus-sequence AP differences are +0.080620 (outer-0), +0.081746
(outer-1), and +0.073460 (outer-2), a descriptive unweighted mean of
**+0.078609**. Corresponding macro-Brier differences are −0.001953,
−0.002153, and −0.001930 (descriptive mean **−0.002012**). These are three
patient-disjoint validation folds but only one seed and one epoch; they do not
measure model-seed or training-budget uncertainty. Do not treat the three
folds or their participant bootstrap intervals as independent seed
replications. The consistent direction strengthens evidence for this
parameterization over this capacity-matched sequence implementation, but
does not establish that clinical relation semantics caused the advantage.
Additional prespecified seeds, folds 3–4, and relation-shuffle,
endpoint/time-reconstruction and event-order controls remain necessary.

The outer-2 paired audit is
[`audit/loop_mps_outer2_graph_vs_sequence_paired_20261019.json`](../audit/loop_mps_outer2_graph_vs_sequence_paired_20261019.json);
model artifacts are protected under
`private/mps_research/outer2_seed20261003_{graph_generic,sequence_mps}/`.
The machine-readable three-fold summary, including per-fold intervals and
identity digests, is
[`audit/loop_mps_graph_vs_sequence_three_fold_summary_20261019.json`](../audit/loop_mps_graph_vs_sequence_three_fold_summary_20261019.json).

## Outer-3 MPS paired replication — 19 October 2026

Outer-3 completed under the same development-only contract: seed `20261003`,
one epoch, batch size 4096, AdamW, and 36,883 parameters per model. The graph
and sequence models verified identical prediction-window identity across
9,167,239 validation windows, 130 participants and 264,561 positive labels;
129 participants had defined AP. The locked holdout was not used.

Graph-generic scored macro AP **0.471442** and macro Brier **0.019757**;
sequence control scored AP **0.360977** and Brier **0.022319**. The paired
10,000-draw participant-bootstrap AP difference was **+0.110465** (95%
interval **[+0.103420, +0.117004]**), graph AP higher for 128/129 AP-defined
participants. Macro-Brier difference was **−0.002562** (95% interval
**[−0.002933, −0.002200]**), graph Brier lower for 125/130 participants.
These intervals condition on fixed predictions.

This is the fourth fold with the same direction at the same seed. It strengthens
fold robustness for this particular graph parameterization versus this
parameter-matched sequence model. It still provides no seed replication, uses
only one epoch, and does not isolate whether graph-message-passing, event
position encoding, or another architecture-specific difference explains the
advantage. The relation-shuffle, endpoint/time reconstruction and event-order
controls remain essential before any relation-specific novelty claim.

The outer-3 audit is
[`audit/loop_mps_outer3_graph_vs_sequence_paired_20261019.json`](../audit/loop_mps_outer3_graph_vs_sequence_paired_20261019.json),
and the four-fold machine-readable summary is
[`audit/loop_mps_graph_vs_sequence_four_fold_summary_20261019.json`](../audit/loop_mps_graph_vs_sequence_four_fold_summary_20261019.json).

## Outer-4 MPS paired replication — 19 October 2026

Outer-4 completed with the same frozen development contract: seed `20261003`,
one epoch, batch size 4096, AdamW, and 36,883 parameters in each model. The
graph-generic and capacity-matched sequence models produced identity-matched
predictions for 127 validation participants, 8,193,251 windows, and 257,379
positive labels. The locked holdout was not used.

Graph-generic scored participant-macro AP **0.474226** and macro Brier
**0.022488**; the sequence control scored AP **0.387856** and Brier
**0.024452**. The paired 10,000-draw participant bootstrap found AP difference
**+0.086370** (95% interval **[+0.077628, +0.094814]**), with higher graph AP
for 118/127 participants. Macro-Brier difference was **−0.001964** (95%
interval **[−0.002228, −0.001717]**), with lower graph Brier for 123/127
participants. These intervals condition on the fitted models.

Across all five patient-disjoint outer folds, still at just one seed and one
epoch, graph-generic has higher participant-macro AP and lower macro Brier in
each fold. The descriptive unweighted means of paired differences are
**+0.086532 AP** and **−0.002113 macro Brier**. This is five-fold coverage,
not seed replication; the bootstrap intervals do not include refitting
uncertainty. The result supports only these tested model implementations and
does not show that clinical relation semantics cause the advantage. The
relation-shuffle, endpoint/time-reconstruction and event-order controls, plus
additional seeds and explanation-fidelity evaluation, remain necessary.
Occurrence-time replay still assumes immediate event availability, which was
not measured.

The outer-4 paired audit is
[`audit/loop_mps_outer4_graph_vs_sequence_paired_20261019.json`](../audit/loop_mps_outer4_graph_vs_sequence_paired_20261019.json); its checkpoint and
prediction archives are protected under
`private/mps_research/outer4_seed20261003_{graph_generic,sequence_mps}/`.
The machine-readable five-fold aggregate is
[`audit/loop_mps_graph_vs_sequence_five_fold_summary_20261019.json`](../audit/loop_mps_graph_vs_sequence_five_fold_summary_20261019.json).

## Outer-0 second-seed paired replication — 20 October 2026

The frozen one-epoch graph-generic versus parameter-matched sequence
comparison was repeated with seed `20261004` on outer-0. Both fits passed
identity checks on the same 130 participants, 8,885,621 windows and 274,044
positive labels; each model has 36,883 trainable parameters. Graph-generic
scored participant-macro AP 0.473152 versus 0.394613 for the sequence model,
for a paired difference of **+0.078540** (10,000-draw participant-bootstrap
95% interval **[+0.069529, +0.087102]**). Macro Brier was 0.022039 versus
0.024217, difference **−0.002178** (interval **[−0.002464, −0.001901]**).
Graph AP was higher for 114/130 participants and Brier lower for 128/130.

On outer-0, seed `20261003` yielded AP difference +0.080620 and macro-Brier
difference −0.001953; seed `20261004` yielded +0.078540 and −0.002178. The
descriptive two-seed means are +0.079580 AP and −0.002066 macro Brier. There
is no confidence interval over fitted seeds; each participant-bootstrap
interval conditions on that seed's fixed predictions. Thus the result is
initial same-fold seed replication, not cross-fold seed replication or proof
of clinical relation semantics. Both fits use one epoch, and the compared
architectures differ in more than graph topology. The evidence supports only
the tested graph-generic implementation against this capacity-matched sequence
control. Relation shuffle, endpoint/time reconstruction, event-order
perturbations, and additional seeds on other folds remain required.

The seed-20261004 paired audit is
[`audit/loop_mps_outer0_seed20261004_graph_vs_sequence_paired_20261020.json`](../audit/loop_mps_outer0_seed20261004_graph_vs_sequence_paired_20261020.json); the two-seed summary is
[`audit/loop_mps_outer0_graph_sequence_two_seed_summary_20261020.json`](../audit/loop_mps_outer0_graph_sequence_two_seed_summary_20261020.json).

The second seed was also completed on outer-1. Graph-generic scored macro AP
0.459892 versus 0.369684 for the non-graph sequence control, paired difference
**+0.090208** (95% participant-bootstrap interval **[+0.081627, +0.098271]**);
macro-Brier difference was **−0.002430** (interval **[−0.002807, −0.002070]**).
Both runs matched across all 9,386,356 windows from 141 participants (140 AP-
defined), and their prediction identity digests matched. The descriptive mean
AP difference over the two completed folds is +0.081183 for seed 20261003 and
+0.084374 for seed 20261004. These are descriptive fold summaries only. The
two-seed/two-fold coverage is still partial; it does not provide a valid
training-seed uncertainty interval, multi-epoch convergence check, or evidence
that relation semantics explain the graph model's advantage. The second-seed
outer-1 audit is
[`audit/loop_mps_outer1_seed20261004_graph_vs_sequence_paired_20261020.json`](../audit/loop_mps_outer1_seed20261004_graph_vs_sequence_paired_20261020.json); see also the interim aggregate
[`audit/loop_mps_graph_sequence_two_seed_two_fold_summary_20261020.json`](../audit/loop_mps_graph_sequence_two_seed_two_fold_summary_20261020.json).

The second seed (`20261004`) has since been completed on outer-2, outer-3, and
outer-4. The paired AP differences are +0.070275 (95% participant-bootstrap
interval [+0.061924, +0.078368]), +0.106387 ([+0.099619, +0.112682]), and
+0.087463 ([+0.079215, +0.095616]), respectively. Macro-Brier differences
are −0.001721 (interval [−0.001970, −0.001469]), −0.002504
([−0.002872, −0.002147]), and −0.002267 ([−0.002577, −0.001964]). Each pair
has identical validation-window identity, 36,883 parameters per model, and
the frozen manifest/input/training contract; the locked holdout was not used.

This completes a two-seed, five-fold development screen for the graph-generic
versus capacity-matched sequence contrast. The graph has higher participant-
macro AP and lower macro Brier in all ten fold-seed pairs. Descriptive mean AP
differences are +0.086532 for seed `20261003` and +0.086575 for seed
`20261004`; descriptive mean macro-Brier differences are −0.002113 and
−0.002220. The five folds are patient-disjoint, but their participant sets
share the same study and data-generation setting; these averages are not a
confidence interval over independent studies or training seeds. Per-fold
bootstrap intervals condition on fitted predictions. The one-epoch fits and
the multiple architecture differences mean this result establishes an
advantage for the tested graph implementation over this comparator, not that
relation semantics caused that advantage. Event-disabled and relation-
perturbation controls, longer-training stability, and explanation-fidelity
tests remain necessary before making a knowledge-graph or explanation claim.
See the complete [two-seed/five-fold audit summary](../audit/loop_mps_graph_sequence_two_seed_five_fold_summary_20261020.json).

## Five-fold modality-typed routing comparison — 20 October 2026

The modality-typed expert-routing model was compared with the parameter-matched
generic-edge graph on all five patient-disjoint development validation folds
for seed `20261004`. Across 652 validation participants and 44,028,064 windows,
typed routing had higher participant-macro AP on two folds and generic routing
on three. The unweighted mean fold difference (typed minus generic) was
−0.000476 (range −0.002015 to +0.001902). Macro-Brier differences were also
mixed; the unweighted fold mean was −0.00000683. Each fold used 10,000 paired
participant-bootstrap draws, which quantify participant variation conditional
on the fitted models, not refitting or seed uncertainty. The fold means are
descriptive and are not an inferential interval.

This does not support a reliable benefit from the current modality-specific
routing rule. It also does not show that clinical KG relations are useless:
the relation IDs are derived from event modality and the constructed
event-to-CGM endpoints, not independently annotated clinical assertions. The
result does not test all graph topologies, relation types, training budgets,
or datasets. No locked-holdout data were used. See the [five-fold relation
summary](../audit/loop_relation_typed_vs_generic_seed20261004_five_fold_summary_20261020.json)
and the [experiment record](loop_temporal_relation_pilot.md).

The most informative next test is a matched event-disabled branch against the
generic graph, followed by a preregistered perturbation of event-to-CGM
endpoints that preserves the same event and CGM records, causal timing rules,
model size, and training budget. These distinguish event-content value from
the value of the chosen temporal connectivity. Explanation fidelity remains
a separate required experiment.

## Event-input ablation — 25 October 2026

On outer-0, seed `20261004`, the generic graph was compared with the same
architecture after all event features were zeroed before edge construction.
The two complete fits used identical source, seed, split, optimizer, declared
parameter count (36,883), and prediction windows; the paired comparison passed
the per-participant identity contract over 130 participants and 8,885,621
windows. Generic-minus-disabled participant-macro AP was **+0.002800** (10,000-
draw paired participant-bootstrap interval **[+0.001996, +0.003609]**), and
macro-Brier was **−0.0002003** (interval **[−0.0002411, −0.0001597]**). This
offers one-fold preliminary evidence that event inputs help this model.

The control removes event content and all event edges together. The disabled
branch retains the same declared parameter count, but its event encoder and
edge experts receive no event-derived gradients, so effective model capacity
is not matched. It does not identify the value of relation semantics. It is a
single seed and fold, and event availability remains assumed from occurrence
time. Replication remains required. See the
[event-ablation report](loop_event_ablation_result_2026_10_25.md) and
[paired audit](../audit/loop_relation_event_ablation_outer0_seed20261004_paired_20261025.json).

## Causal endpoint perturbation — five-fold update, 26 October 2026

At seed `20261004`, the generic graph using nearest observed later CGM
endpoints was compared with the same model using second-nearest observed later
endpoints when available and nearest fallback otherwise. Each of the five
outer-fold pairs used the same 36,883-parameter architecture, one-epoch budget,
optimizer, event records, CGM inputs, fold membership, and validation windows.
Manifest/input/source digests and prediction identities matched within each
pair. Across folds this totals 44,028,064 validation windows and 1,296,297
positive labels (participant counts recur across folds). The locked holdout
was not used.

Nearest-minus-second-nearest participant-macro AP differences on outer-0
through outer-4 were **−0.000631, +0.006681, −0.000183, +0.001618, and
+0.004350**. The corresponding macro-Brier differences were **+0.0000509,
−0.0002618, −0.0000686, −0.0000571, and −0.0001664**. Thus AP favors nearest
on three folds and second-nearest on two; Brier favors nearest on four folds.
The unweighted fold means (+0.002367 AP and −0.0001006 macro Brier) are
strictly descriptive. The per-fold paired intervals condition on fixed model
predictions and do not measure variability from retraining, seed, or cohort.

The first-seed screen showed mixed fold directions. The second one-epoch seed
(`20261005`) is now complete on all five outer folds. Its nearest-minus-second-
nearest AP differences are **+0.001615, +0.003555, +0.001039, +0.001413, and
+0.000907**; the outer-2 paired interval includes zero. Its macro-Brier
differences are **+0.0000189, −0.0001642, −0.0000620, −0.0000215, and
−0.0000179**; the outer-4 interval includes zero. Across the two seeds, nearest
endpoints have higher AP and lower macro-Brier in **8/10 seed-fold pairs**.
Unweighted mean differences are **+0.002036 AP** and **−0.0000750 macro-Brier**.
This supports the narrow finding that the chosen causal endpoint assignment
can affect predictions and often favors nearest in this screen. A participant-
cluster bootstrap of participant-level differences averaged over both fixed
seeds estimated AP difference **+0.002097** (95% interval **[+0.001761,
+0.002443]**) and macro-Brier difference **−0.0000773** (**[−0.0000957,
−0.0000594]**). This interval handles participant repetition across seeds but
still conditions on the two trained seeds; it does not estimate refit or seed
variability. The ten seed-fold evaluations reuse the same participant
partition scheme, and this is only one endpoint perturbation. Event
availability at occurrence time is assumed immediate and
has not been measured. Do not open the locked holdout during development. See
the [endpoint result](loop_endpoint_perturbation_result_2026_10_25.md),
[five-fold summary](../audit/loop_relation_endpoint_perturbation_seed20261004_five_fold_summary_20261026.json),
[second-seed five-fold summary](../audit/loop_relation_endpoint_perturbation_seed20261005_five_fold_summary_20261028.json),
[combined two-seed summary](../audit/loop_relation_endpoint_perturbation_two_seed_five_fold_summary_20261028.json),
[participant-cluster bootstrap](../audit/loop_relation_endpoint_perturbation_two_seed_participant_cluster_bootstrap_20261028.json),
[outer-4 second-seed paired audit](../audit/loop_relation_endpoint_perturbation_outer4_seed20261005_paired_20261028.json),
[outer-4 paired audit](../audit/loop_relation_endpoint_perturbation_outer4_seed20261004_paired_20261026.json),
and prior [outer-0](../audit/loop_relation_endpoint_perturbation_outer0_seed20261004_paired_20261025.json) and [outer-3](../audit/loop_relation_endpoint_perturbation_outer3_seed20261004_paired_20261026.json) paired audits.
