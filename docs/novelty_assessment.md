# Novelty assessment and prior-work comparison

Updated: 31 October 2026. Decision: proceed only with a focused comparative research contribution; do not claim a new algorithm or the first semantic T1D graph. This extends the initial [proposal validation](proposal_validation.md). Search scope and access limits are recorded in the [search log](literature_search_log.md).

**Current evidence synthesis:** see the [31 October novelty evidence report](novelty_evidence_report_2026_10_31.md) for the complete current execution summary, the newly considered hypoglycemia graph-prediction and graph-versus-sequence precedents, and the proposed paper wording. The report supersedes the earlier result-status summary below where its dates or completion counts differ.

## What the additional investigation changed

The original comparison between time-point graphs and semantic patient graphs is too narrow. Relevant work includes patient KGs, patient-similarity graphs, visibility graphs, fixed physiology graphs, continuous-time models and graph explanation diagnostics. The remaining opportunity is a controlled investigation of event-level relations under a clearly defined advance-warning task. The proposed study must explain which aspect produces any gain: more information, individual-event resolution, timing, relational structure, parameter count, or recording assumptions.

This is an inference from the reviewed sources, not evidence that no equivalent study exists. An unreported feature in an abstract is **unknown**, not absent. Published scores below are deliberately not compared across incompatible experiments.

## Empirical update — 28 October 2026

The matched nearest-versus-second-nearest causal edge-target perturbation is
complete over five patient-disjoint outer folds and two fixed training seeds.
Nearest endpoints yielded higher participant-macro AP in 8/10 seed-fold pairs
and lower macro-Brier in 8/10. To avoid counting the same person twice across
seeds, we averaged each participant's paired difference across the two fixed
fits and bootstrapped participants: AP difference +0.002097 (95% interval
[+0.001761, +0.002443]); macro-Brier difference −0.0000773 ([-0.0000957,
-0.0000594]). These intervals condition on only two one-epoch seeds; they do
not estimate training-seed variability. The result establishes sensitivity to
this specific endpoint assignment in this Loop setup, not a general benefit
of clinical relations, a novel KG method, or clinically meaningful utility.

**Event-time reassignment update — 29 October 2026:** an additional fixed-fit
control rotates event ages among active event records, preserving each
window's event and age multisets while breaking record-to-time pairing. It is
complete for five folds and two seeds. Original pairing has higher AP in
10/10 fold-seed fits, but only 3/10 fold-specific participant intervals
exclude zero; Brier direction is split 5/5 and 4/10 intervals exclude zero.
The mean AP difference across the ten fits is +0.0001118. The same 652 people
recur across seeds, so no pooled interval is reported. This is small,
metric-dependent sensitivity to one deterministic perturbation on fixed
epoch-1 models. It does not prove relation validity, relation-level predictive
benefit, causal effects, or explanation faithfulness. Exact original source
digests are not available in the current workspace, but unperturbed replay
reproduced all saved fold metrics and prediction identities within tolerance.
See the [event-age control report](loop_event_age_reassignment_control.md)
and [two-seed summary](../audit/loop_event_age_reassignment_two_seed_five_fold_summary_20261029.json).

The broader evidence remains mixed: the capacity-matched graph-generic versus
sequence comparator favors graph-generic on Loop development folds, while
typed modality routing has not improved over generic edges. Event-disabled
evidence is still limited to one fold. One exploratory deletion/retention
sensitivity audit is now complete, but its top-event comparison is
selection-conditioned and is not an independent faithfulness test. Broader
explanation evaluation and external validation remain unfinished. The new
2026 JAMIA temporal GAT-BiGRU study, IJCAI TRANS general temporal EHR graph,
and MetaboNet-Bench preprint further narrow the novelty claim; their scope and
limits are documented in the [current
evidence report](novelty_evidence_report_2026_10_31.md). See also the
[earlier novelty evidence report](novelty_evidence_report_2026_10_17.md),
[endpoint results](loop_endpoint_perturbation_result_2026_10_25.md), and
[participant-cluster audit](../audit/loop_relation_endpoint_perturbation_two_seed_participant_cluster_bootstrap_20261028.json).

## Closest work

| Study / evidence inspected | Representation and established overlap | Task / evidence limitations | Consequence for our proposal |
|---|---|---|---|
| Onwuchekwa, Weber & Maleshkova; ESWC 2024 paper and 2025 dissertation chapter | Patient-specific semantic KGs, ontology integration, temporal semantics, clinical-text extraction, and TransE/DistMult/GCN embeddings are proposed. The dissertation describes MIMIC-III structured data and preliminary glucose prediction for one patient. | The dissertation calls the KG/ML work early-stage; the inspected chapter does not report a patient-disjoint, information-matched outpatient CGM benchmark or relation ablation. It is direct conceptual prior work despite its different empirical scope. | Semantic patient-specific hypoglycemia prediction and KG construction are prior work. Our candidate distinction is a controlled test of when event-instance relations add predictive value under matched information, timing and capacity; this remains provisional until relation controls run. [Conference text](https://2024.eswc-conferences.org/wp-content/uploads/2024/05/77770363.pdf), [publisher chapter](https://link.springer.com/chapter/10.1007/978-3-031-78955-7_4), [2025 dissertation, DOI 10.25819/ubsi/10693](https://dspace-backend.ub.uni-siegen.de/server/api/core/bitstreams/1e658634-a368-49e9-93b2-4491e750edb8/content). |
| Rad et al., 2024; publisher methods/application sections | Patient-centric PHKG, FHIR alignment and diabetes applications. | Prediction application does not establish a matched test of our event-relation contribution. | Patient-centricity, semantic integration and interoperability are not standalone novelty. [Paper](https://www.mdpi.com/2075-4426/14/4/359). |
| HETER, 2023; publisher methods/results | CGM subsequences connected using similarity, graph convolution, attention and recurrent temporal learning. | Mixed T1D/T2D cohort; glucose forecasting. “Heterogeneous” here concerns different CGM series, not necessarily typed clinical event nodes. | Distinguish patient/subsequence similarity from within-person event relations. Graph-plus-GRU and temporal heterogeneity already exist. [Paper, section 2.3](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2023.1225638/full). |
| Hüni's 2024 University of Bern thesis; related Hüni, Garcia-Tirado & Riesen S+SSPR 2024 / Springer 2025 chapter | Full thesis methods establish CGM-only natural visibility graphs and an LSTM comparator on 37 people with T1D; any future CGM <70 mg/dL label; exact 120-minute history / 30-minute horizon setting; F2 0.348 LSTM vs 0.409 GNN across patient datasets. | Separate models per patient and chronological 70/30 within-person train/validation split; not patient-disjoint. Parameter matching is not documented. Graph nodes are CGM readings, not treatment/meal event instances. Thesis and final chapter are related author work; do not assume identical. | Broad first graph, graph-versus-sequence, and first matching endpoint/history claims are ruled out. The remaining candidate must be narrowly about timestamped event-instance relations under patient-disjoint, same-input, capacity-matched controls; current project results favor aligned pooling. [Official thesis](https://prg.inf.unibe.ch/wp-content/uploads/2024/08/BA_FabianHuni.pdf), [author repository](https://github.com/fabianHueni/cgm-visibility-graph-dataset), [Springer chapter](https://link.springer.com/chapter/10.1007/978-3-031-80507-3_6). |
| Sarwar et al., SysCon 2026; full author-uploaded manuscript methods/diagnostics reviewed 18 October | BrisT1D; a fixed seven-node physiology graph (glucose, insulin, carbohydrates, heart rate, activity, steps, calories) with directed physiological edges; each time point is a graph instance with rolling-window summary attributes and circadian context; two-layer GATv2; joint future-glucose regression and threshold classification at 5/15/30-minute horizons. The manuscript reports node ablation, attention/top-edge deletion and reinsertion, random-edge-drop comparisons, and correlation of attention with physiology priors. | The classification label is whether a single future glucose value is below 3.9 mmol/L, and rows without that future value are dropped; it is not the same endpoint as any low in a future interval. The accessible split description says stratified train/validation/held-out test, but does not establish participant-disjoint splitting. This is author-uploaded conference content, not a version-checked IEEE copy; no independent reproduction. | Fixed modality-node physiology graphs and edge-faithfulness diagnostics are established prior work. Any remaining distinction must be stated narrowly as a comparison of timestamped individual event instances against modality-summary and event-sequence representations, using identical event information and a patient-disjoint incident-within-horizon endpoint. The current generic-vs-typed pilot tests a modality-derived message-passing inductive bias; it does not establish new clinical facts or a globally novel graph method. [Author-uploaded manuscript](https://www.researchgate.net/publication/404642556_Explainable_Multitask_Graph_Network_for_Blood_Glucose_Forecasting_and_Hypoglycemia_Risk_Classification), DOI 10.1109/SysCon66367.2026.11503533. |
| Chen et al., IJCAI 2024, TRANS | General EHR temporal heterogeneous graph with diagnosis, procedure and medication-code nodes connected to timestamped visit nodes, chronological visit edges, temporal message passing and a patient graph explainer; next-visit diagnosis prediction on MIMIC-III, MIMIC-IV and MarketScan CCAE. | Not T1D CGM forecasting; event nodes are coded medical concepts attached to visits, not raw CGM/pump/meal transactions; no matched relation ablation for incident-low prediction. | The generic temporal clinical-event-node graph and graph-explanation pattern is established. The candidate must be framed as a raw insulin/meal transaction alignment test for this specific CGM endpoint and matched benchmark, not invention of temporal patient event graphs. [IJCAI version of record](https://ijcai.org/proceedings/2024/637), [DOI](https://doi.org/10.24963/ijcai.2024/637). |
| Sarwar et al., JAMIA 2026; PubMed/OUP abstract and OUP supplement | Temporal time-point graph, GAT-BiGRU, multimodal 30/60-minute prediction, GNNExplainer; supplement describes past-to-present k=10 edges and 23-dimensional nodes. | Supplement describes OhioT1DM 80% session training / 20% validation plus held-out temporal segments, leaving participant separation unresolved; BrisT1D uses 15 unseen patients for test. Main article is embargoed in PMC until 18 June 2027. No event-instance relation ablation is described in the inspected abstract/supplement; event node and same-information-control details remain unverified. | Include it as a direct temporal graph comparator; do not infer methodological deficiencies or claim absence beyond the inspected materials. [OUP article and supplementary data](https://academic.oup.com/jamia/article-abstract/33/9/1713/8711207#supplementary-data), [PubMed](https://pubmed.ncbi.nlm.nih.gov/42314749/). |
| Zheng et al., ICASSP 2024, BG-BERT | OhioT1DM and DiaTrend; multimodal past CGM, basal/bolus insulin and carbohydrate inputs; 30/60-minute future glucose forecasts evaluated for <70 mg/dL sensitivity; public author-linked code. | Uses pointwise predicted-glucose thresholds, not incident-within-horizon classification; 64/16/20 split unit is not established as participant-disjoint; non-graph model. | Multimodal glucose prediction and low-glucose forecasting are prior work. Preserve the endpoint and participant-split distinction; do not claim first event-aware sequence forecasting. [Author paper](https://sijieji.github.io/pdf/Glucose_Prediction_ICASSP_2024.pdf), [code](https://github.com/aiot-lab/BG-BERT), [DOI](https://doi.org/10.1109/ICASSP48485.2024.10446832). |
| Sun et al., *Scientific Reports* 2026, future-aware sequence forecasting | OhioT1DM/AZT1D; teacher uses historical CGM plus future insulin/carbohydrate disturbances, summarized as IOB/COB, then distills a history-only sequence student; forecasts trajectories up to 120 minutes. | Continuous glucose forecasting rather than incident-low classification; non-graph model; Ohio uses supplied train/test files and AZT1D uses first-80%/remaining-20% development/test wording. | Time-aligned event-aware sequences and explicit future-event availability controls are prior work. The remaining question is event-instance relation structure under matched information and timing, not event-aware input alone. [Publisher full text](https://www.nature.com/articles/s41598-026-41787-7), [PubMed](https://pubmed.ncbi.nlm.nih.gov/41764313/). |
| Calzavara et al., IEEE TBME 2026, PhyNet | T1DEXI and MetaboNet (848 subjects); CGM, carbohydrate and insulin inputs; compares six deep-learning baselines and evaluates counterfactual physiological responses and unsafe recommendations. | PubMed abstract inspected; IEEE full text and detailed split/protocol not retrieved; continuous BG forecast, not an event-instance graph or incident-low endpoint. | Predictive metrics must be separated from physiological/explanation faithfulness and safety. This does not establish graph-relation novelty. [PubMed abstract](https://pubmed.ncbi.nlm.nih.gov/42685163/), [IEEE record](https://ieeexplore.ieee.org/abstract/document/11675927/). |
| Ibrahim et al., *Frontiers in Endocrinology* 2026, patient-specific safety-oriented digital twins | Full text reports five-seed, participant-level analyses on Manchester and OhioT1DM; aligned CGM, insulin and meal events plus IOB/COB; model/input ablations and counterfactual treatment-response plausibility checks. | Patient-specific glucose trajectory forecasting rather than incident-low prediction on unseen participants; non-graph models, not event-instance relation testing. | Strong precedent for matched input/model controls and separating prediction accuracy from treatment-response plausibility. [Full text](https://doi.org/10.3389/fendo.2026.1958918). |
| Akrong et al., *Discover Artificial Intelligence* 2026, XAI methods for glucose forecasting | OhioT1DM BiLSTM comparison of attention, saliency, integrated gradients, SHAP and LIME; evaluates deletion faithfulness and explanation stability. | Six participants, one forecast architecture; proposed clinical plausibility score is a heuristic, not clinician evaluation; no graph or incident-low endpoint. | Explanation-quality evaluation is prior work. A graph-explanation claim still needs explicit faithfulness and stability evidence; clinical validation must not be inferred from the heuristic. [Full text](https://doi.org/10.1007/s44163-026-01328-7). |
| Fleischer et al., 2022, CGM-only hypoglycemia event prediction | RUSBoost predicts sustained <70 mg/dL (at least 15 minutes) up to 40 minutes ahead from one hour of CGM in 225 adults with T1D; reports patient-level 70/30 train/test split and event-level lead-time analysis. | Strong prior patient-disjoint event-prediction baseline. It has no recorded insulin/meal event inputs and uses a sustained 40-minute outcome rather than this project's rolling 30-minute any-low label. [Frontiers full text](https://www.frontiersin.org/journals/clinical-diabetes-and-healthcare/articles/10.3389/fcdhc.2022.1066744/full). |
| Cederblad et al., 2023, HypoCNN retrospective event-cause classification | CGM/FGM sequences from 449 people and 42,120 lows; clinician-labeled sample; uses insulin/carbohydrate records for cause validation and a separate 22-person clinician evaluation. | Prior interpretation of hypoglycemia causes with treatment context, but classification follows observed episodes; it is not prospective risk forecasting or graph explanation. [PubMed](https://pubmed.ncbi.nlm.nih.gov/37052842/), [publisher](https://link.springer.com/article/10.1007/s13300-023-01403-7). |
| Maqsood et al., IEEE Access 2026; institution-hosted accepted manuscript, methods and robustness sections | Neural CDE, event channels, missingness handling, physiology constraints, calibration/risk analysis and attribution. | Reports patient-wise evaluation and missingness/shift experiments; exact comparability requires reproduction. DOI in acceptance footer is 10.1109/ACCESS.2026.3672553; ignore template DOI at top. | Irregular inputs, calibration, missingness robustness and lead-time analysis cannot independently establish novelty. Add a serious irregular-input non-graph comparator. [Accepted manuscript](https://epubl.ktu.edu/object/elaba%3A279147543/279147543.pdf). |

The SysCon manuscript is primary author content hosted on ResearchGate. Its authorship/upload notice and manuscript text were visible; the IEEE DOI resolver failed in this session. This is a disclosed access route, not an independent replication or a claim that every version is identical. The manuscript's split wording is insufficient to conclude that participants are shared across partitions; record participant-disjointness as unverified, not as a demonstrated flaw.

## Adjacent methods that constrain claims

| Existing idea | Evidence | Implication |
|---|---|---|
| Time-aware graph aggregation and dynamic-event learning | [TGAT](https://arxiv.org/abs/2002.07962), [TGN](https://arxiv.org/abs/2006.10637) | Timestamps, inductive inference and temporal attention are established ingredients. |
| Continuous-time heterogeneous graph learning | [CTRL](https://arxiv.org/abs/2405.08013) | Adding heterogeneity to temporal learning is not automatically a new architecture. |
| Event time versus database knowledge time | [Bitemporal property graphs](https://arxiv.org/abs/2111.13499) | The two-time representation is established database methodology. Prediction availability is also not necessarily identical to ingestion time. |
| Missingness masks and time since observations | [GRU-D](https://arxiv.org/abs/1606.01865) | A baseline must receive these signals; their inclusion is not evidence for KG value. |
| Glucose motifs and graph-based relations | [MotifDisco](https://arxiv.org/abs/2409.15219) | A motif-based pivot would require its own comparison; do not simply rename events as motifs and claim novelty. Preprint abstract inspected. |

## Claims we can and cannot make

| Candidate claim | Current judgment |
|---|---|
| First patient-centric semantic KG for T1D hypoglycemia | Reject. |
| First temporal or heterogeneous GNN for glucose prediction | Reject. |
| First physiology-based graph or graph perturbation explanation | Reject. |
| First use of two timestamps, missingness masks or clinical standards | Reject. |
| A controlled study of raw timestamped insulin/meal transaction alignment versus summaries and sequence encodings for incident-within-horizon hypoglycemia | A defensible *candidate empirical distinction*, not a new generic temporal event-graph method and not yet a certified novelty claim. TRANS already uses temporal EHR graphs with medication/diagnosis/procedure-code nodes attached to time-indexed visits and a graph explainer. SysCon and GAT-BiGRU establish graph prediction/explanation prior art for T1D glucose, while GAT-BiGRU’s supplement is reviewed and the main body remains embargoed. The narrow distinction must be screened against a broader search and demonstrated with same-input, same-timing, capacity-aware, patient-disjoint experiments. |
| Relations add predictive information beyond identical raw inputs | Incorrect when relations are deterministic functions of those inputs. Test inductive bias, sample efficiency or robustness instead. |
| Reported paths faithfully explain a prediction | Requires measured fidelity and provenance integrity; cannot be inferred from a diagram. |
| Clinically useful / deployment-ready | Not established by this retrospective project. |

## Recommended direction and alternatives

**Primary direction:** event-instance versus modality-summary representations, tested on identical information and held-out people. Make representation resolution, relation parameterization, timing and model capacity separate experimental factors. The deliverable is a reproducible scientific answer to when the graph helps, with auditable event explanations. Use a modest existing relation-aware encoder initially.

**Conditional extension:** quantify how delayed recording changes the incremental value of event relations and the validity of explanation evidence. Distinguish measured delays from imposed scenarios. This is an extension of the scientific question, not a claim to have invented bitemporal graphs.

**Deferred direction:** physiologically constrained or motif-bottleneck architecture. The reviewed literature makes a superficial architecture combination weak; adding it now would enlarge the proposal without demonstrated need. Revisit only after the baseline study identifies a specific failure and a testable mechanism.

The [refined proposal](refined_proposal.md) and [decisive experiments](decisive_experiments.md) make the recommended direction concrete. No architecture was selected based on test results, and no paper outcome has been assumed.

## Remaining uncertainty

The accessible evidence supports rejecting the original broad novelty claim and specifying a narrower study. It does not certify novelty. The full Onwuchekwa dissertation has now been retrieved, with its semantic KG chapter and synthesis reviewed; that chapter describes an early-stage framework and preliminary one-patient MIMIC-III glucose prediction, but no inspected matched outpatient relation ablation. The OUP GAT-BiGRU supplement is now inspected, but the article body is listed in PMC as embargoed until 18 June 2027; the Ohio split unit and detailed event representation remain unresolved. The 31 October search also added BG-BERT, future-aware sequence distillation, PhyNet, and IJCAI's TRANS temporal EHR graph as adjacent prior work constraining multimodal inputs, event availability, explanation faithfulness, and generic event-node graph construction. A final source check added Oviedo et al.'s 2019 meal/bolus-indexed postprandial hypoglycemia forecasting and IDMVis, a 2018 temporal event-sequence visualization and decision-support study for T1D. The broader pass also verified a 2026 five-seed, two-cohort study of counterfactual meal/insulin response in patient-specific glucose forecasters and a 2026 study of time-series explanation faithfulness and stability. The latest screen added a 225-person patient-level CGM-only hypoglycemia event predictor and a 449-person retrospective cause-classification study with insulin/carbohydrate validation. These rule out broad novelty claims for patient-level short-horizon prediction, post-event cause interpretation, temporal visualization, physiology/faithfulness evaluation, or explainability evaluation. The final-version methods of the Onwuchekwa Springer chapter and the identity of Hüni's thesis versus the related Springer chapter also remain access-dependent. A further source check added Dave et al.'s direct with/without insulin-carbohydrate feature comparison, meal-anchored 30-minute postprandial prediction, and nocturnal models using candidate event features or aggregate carbohydrate-on-board. These rule out novelty based on including treatment context or on meal-indexed prediction alone; none inspected provides the same-information, same-timing graph-versus-non-graph event-instance comparison. The Dave paper's abstract/body discrepancy on its 30-minute incremental effect remains unresolved. The literature matrix now contains 70 unique records after duplicate removal; it remains a targeted search, not a systematic review. Search did not establish a later completed equivalent study, but incomplete retrieval cannot establish absence. If a directly equivalent benchmark appears, update the question toward reproduction, new data, or a demonstrated limitation rather than defending the original wording.

## 18 October 2026 update

A newer direct competitor materially narrows the novelty space: Sarwar et al.'s [GAT-BiGRU paper in JAMIA](https://doi.org/10.1093/jamia/ocag104), published online 18 June and indexed in PubMed with issue date 1 September 2026, reports a temporal k-neighborhood graph over feature-enriched time-point nodes, graph attention plus BiGRU, multimodal glucose/hypoglycemia prediction at 30 and 60 minutes, OhioT1DM and BrisT1D evaluation, and GNNExplainer. Its OUP supplement specifies directed past-to-present edges with k=10 and 23-dimensional time-point nodes; its BrisT1D test is described as 15 unseen patients, while the OhioT1DM description does not resolve participant separation. PMC lists the article body as embargoed until 18 June 2027. The full author-uploaded [SysCon 2026 manuscript](https://www.researchgate.net/publication/404642556_Explainable_Multitask_Graph_Network_for_Blood_Glucose_Forecasting_and_Hypoglycemia_Risk_Classification) adds a physiology-graph comparator: fixed modality nodes with directed insulin/carbohydrate/activity relations, time-varying window summaries, future point-threshold labels, and edge/node faithfulness diagnostics. Temporal graph learning, multimodal graph prediction, physiology-based edges, and graph explanations for T1D hypoglycemia are therefore clearly prior work. The event-instance-versus-summary/sequence distinction remains an inference from the inspected representations, not proof that no equivalent study exists. The exact SysCon final IEEE text, supplement, and participant-level split remain unverified.

A second 18 October primary-source check adds a direct event-aware comparator: Taku et al.'s [JMIR 2026 OhioT1DM study](https://doi.org/10.2196/79195) combines CGM with pump insulin, discrete self-entered meals/activity and wearable signals; it uses recent-event timing in a two-hour state and presents SHAP/LIME explanations. It is a small-cohort RL/dosing and glucose-forecasting study, not a KG or a matched typed-relation evaluation. Pyatak et al.'s [2026 person-centered temporal-network study](https://doi.org/10.1007/s12529-026-10483-1) links CGM and momentary experiential reports in individualized networks, but it does not forecast hypoglycemia. Fang et al.'s [2026 MT-HypoNet study](https://doi.org/10.1016/j.isci.2026.115294) reports multicenter CGM forecasting/forewarning in 1,662 T1D/T2D patients, but does not test event relations. Together these sources further rule out novelty based on event inclusion, explainability, patient-centered temporal networks, or scale. They do not resolve the narrow relation-ablation question.

Loop first-gate CGM-MLP versus clean-GRU comparisons have repeated in two seeds on the same outer-0 validation cohort, with CGM-only ahead in both. Full-history history-only also exceeded history-plus-events for one seed/fold; event-summary/residual and a heavily truncated 16-event sequence did not improve their CGM references. The matched typed-versus-generic temporal-relation pilot found generic routing slightly ahead on one fold and seed. A subsequent exact-capacity graph-versus-non-graph sequence comparison found a larger graph-generic advantage on the same fold and seed: participant-macro AP 0.47448 vs 0.38990 (paired difference +0.08458, 10,000-draw 95% participant-bootstrap interval [+0.07810, +0.09082]) and Brier 0.02152 vs 0.02421 (10,000-draw 95% interval [−0.00304, −0.00235]). This is preliminary support for the tested graph message-passing parameterization over that sequence architecture; it does not show that typed relations help, and one fixed fold/seed/epoch cannot establish retraining robustness. The full raw archive was downloaded, checksum-verified, and independently recomputed locally. See the [relation pilot result](loop_temporal_relation_pilot.md), [capacity-matched control result](loop_non_graph_capacity_matched_control.md), [paired audit](../audit/loop_graph_vs_capacity_matched_outer0_paired.json), and [10,000-draw sensitivity audit](../audit/loop_graph_vs_capacity_matched_outer0_paired_10000draws_20261019.json).

**19 October focused prior-art update:** Rehman et al. already evaluate meal-indexed postprandial hypoglycemia with timestamped meal and bolus information over a four-hour horizon. A newly published JMIR AI study uses timestamped meal/bolus inputs on a five-minute grid, patient-wise partitions, and an LSTM with aligned inputs for T1D glucose forecasting. A 2024 paper already proposes a patient-centric diabetes personal-health KG/digital twin, and an institutional project page updated in August 2026 describes a semantic T1D graph with short-term hypoglycemia-onset prediction as an ongoing project. A 2024 personalized short-horizon model and a 2026 patient-wise hour-ahead temporal multimodal predictor further confirm that patient-specific hypoglycemia prediction and temporal context are established. These findings rule out novelty based on event inclusion, a patient-centric diabetes KG, or a sequence comparator alone. The candidate contribution remains a controlled test of relations among individual event instances for the project’s rolling low-event label, under matched information, timing, capacity, and relation perturbations. See the [focused source comparison](closest_prior_work_event_graph_addendum_2026_10_19.md) and [literature search log](literature_search_log.md). The search remains targeted and does not establish absence of an equivalent comparison.

**Updated decision — 19 October 2026:** retain the narrow controlled-study framing. The evidence supports a preliminary graph-versus-capacity-matched-sequence result for one Loop development fold, while the generic-versus-typed pilot does not support a benefit from the tested modality-specific routing. The study still cannot claim a new KG method, a replicated graph advantage, typed-relation semantics beyond generic connectivity, faithful graph explanations, measured real-time availability, or external validation. The next decisive work is prespecified fold/seed replication and relation perturbation controls, with the locked holdout kept sealed.

**Empirical decision — 28 October 2026:** the endpoint assignment experiment is
now replicated over two fixed seeds and all five development folds. This
strengthens the candidate contribution from an unreplicated pilot to a
reproducible endpoint-sensitivity result, but does not show that typed clinical
relations improve on models with the same information or establish a novel
graph method. The next discriminating work is relation-shuffle/event-time
controls and explanation-faithfulness evaluation, followed by multi-epoch
stability and only then a single locked-holdout evaluation. The holdout remains
sealed.

## Decision update — 31 October 2026

This update supersedes the earlier preliminary next-step status above. The
controlled graph-versus-time-aligned-pooling comparison is now complete for
two seeds across all five patient-disjoint Loop development folds at two
epochs. Pooling led participant-macro AP in all ten fits and macro-Brier in
nine; the two-seed participant-level graph-minus-pooling AP difference was
−0.009900 (95% fixed-prediction interval [−0.010477, −0.009345]) and
macro-Brier difference +0.0001264 ([+0.0001096, +0.0001429]). One eight-epoch
outer-0 pair at one additional seed showed the same direction with a smaller
difference, but is insufficient to establish convergence or training-seed
uncertainty.

The targeted primary-source review also confirms that MT-HypoNet already
reports Loop-based inter-patient five-fold validation and 30-minute
hypoglycemia forewarning from two-hour histories, using a different sustained
event definition (three consecutive readings below 70 mg/dL). Avoid claims
that this project is the first Loop forewarning model, first patient-disjoint
Loop evaluation, or first two-hour/30-minute setup. The remaining novelty
candidate is a specific empirical comparison of event-instance graph
message-passing against equally timed non-graph event controls. The current
results do **not** support a predictive benefit from the tested graph
relations; the defensible contribution may be the controlled negative finding
and its audit trail, conditional on adequate optimization and full-text review
of close prior work. See the [31 October primary-source update](primary_source_novelty_update_2026_10_31.md)
and [evidence report](novelty_evidence_report_2026_10_31.md).

The five frozen Loop CGM logistic models have now been evaluated without
refitting on DCLP3 and DCLP5 CGM-only targets. All five outperform persistence
on participant-macro AP and Brier in each reported cohort/timestamp policy.
This is limited external CGM transfer evidence, not an insulin-only or graph
replication: the models contain no event inputs, labels are release-local
future CGM thresholds, and timestamp semantics remain unresolved. An
insulin-relation external evaluation still requires a justified clock policy,
basal-state semantics, a frozen common-input adapter, event-availability
policy, and exact transfer parity. See the [five-fold transfer report](frozen_loop_cgm_jaeb_transfer_20261031.md).


**Prior-art update — 31 October 2026:** Ma et al. already mine multidimensional CGM/meal/insulin sequences for T1D hypoglycemia alarms on OhioT1DM; Zhu et al. combine CGM, meal/bolus entries, wearable physiology and recurrent prediction for personalized warnings; Athanasiou et al. report interpretable multimodal T1D hypoglycemia risk models. Therefore event context, multimodal sequences, personalization, interpretation, and deployment are not standalone novelty. The candidate remains a narrowly tested question about whether relations among individual recorded event instances add value beyond matched time-aligned controls. Search coverage is still focused, not systematic; split details for some prior studies remain unverified. See the [primary-source check](primary_source_novelty_check_2026_10_31.md) and [search log](literature_search_log.md).

**Additional close prior art — 31 October 2026:** Khokhar et al.'s full arXiv preprint (26 October) uses an any-observed-future-CGM-<70 endpoint at 30 minutes, patient-disjoint outer folds, multimodal-versus-sequence model comparisons, and explanation/perturbation evaluation. It does not describe raw timestamped insulin/meal events or graph relations, and it is not yet a verified peer-reviewed version. This means endpoint, short horizon, patient-level evaluation, multimodal comparison, and explanation robustness cannot be offered as novel contributions. The remaining distinction is limited to the controlled incremental comparison of raw event-instance relations under matched information, timing, and capacity; current Loop graph-versus-pooling results remain negative. A separate *Endocrine Practice* TFT supplement citation is now included with its methods explicitly marked unverified because the publisher page was inaccessible. The matrix now contains 66 unique records. Dave et al. (2021) already compare 30/60-minute risk prediction with and without insulin/carbohydrate context; the article abstract and body snippets disagree on the 30-minute incremental effect, so no definitive effect claim is made. Meal-anchored postprandial prediction and bedtime models using aggregate carbohydrate context also predate this project; large-scale CGM-only nocturnal forecasting further supports retaining a strong glucose-history baseline. Li, Ge & Chen (2020) already define event-time order as typed relations in a dynamic KG and analyze diabetes event streams including glucose, insulin, meals and hypoglycemic symptoms, although the paper does not report diabetes hypoglycemia prediction metrics. Zecchin et al. (2016) and Apicella et al. (2026) further establish direct input/context and representation comparisons in T1D glucose/glycemic-event prediction. Acharya and Lee (2014) already model temporally ordered diabetic event instances and causal links among insulin, glucose, meal, and hypoglycemic-symptom events; Li et al. (2020) use typed event-order relations in a diabetes-stream KG, and Postiglione et al. (2024) use temporal patient KGs to predict future disorders. Therefore event-instance relations and temporal diabetic graphs themselves are not novel. The remaining question concerns raw event instances and their relations versus the same event content available to non-graph comparators under matched timing and capacity. See the [full focused-source update](targeted_prior_art_search_2026_10_31.md) and [search log](literature_search_log.md); the search is still targeted and cannot certify absence of an equivalent relation test.


**Citation-chain update (31 October 2026):** Backward checking Quader et al.'s
2026 review added primary studies showing timestamped CGM/insulin/meal/activity
inputs for nocturnal risk (Bertachi et al.), a CGM-versus-CGM+HRV incremental
comparison (Cichosz et al.), and explainable glucose/insulin/activity risk
models with independent pilot testing (Mosquera-Lopez et al.). This further
removes contextual-data integration, incremental context testing, and
explainable multimodal risk modeling as broad novelty claims. It does not
resolve novelty of the narrow matched event-instance relation test. The
curated matrix now has 69 unique records; that is not the search yield. The
review remains targeted, not systematic. See the [updated source comparison](targeted_prior_art_search_2026_10_31.md).

**Additional temporal-attention precedent (31 October 2026):** Yu et al. (2024)
use asynchronous multimodal features and prior-knowledge-guided dynamic
attention for nocturnal warning on OhioT1DM, but report only 10 analyzed
participant datasets with within-person temporal test periods. This is another
reason not to claim novelty for temporal multimodal fusion or guided attention;
it is not the same event-instance graph or matched relation experiment. The
curated matrix now has 70 unique records, not 70 search hits.
