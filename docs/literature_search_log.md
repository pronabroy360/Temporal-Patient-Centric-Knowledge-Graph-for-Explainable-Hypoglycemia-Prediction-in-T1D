# Targeted novelty search log

Date: 10 September 2026. Purpose: test the proposal's novelty and identify necessary comparators. This is a targeted scoping search using web search and direct primary-source retrieval, not a systematic review, native database export, patentability assessment or exhaustive citation census.

## Search execution

Queries below were run through the web search tool. Domain-restricted searches are search-engine queries, not proof of comprehensive PubMed/IEEE/arXiv coverage. Returned results were inspected for relevant primary papers, author manuscripts, publisher records and repositories. Aggregator records were used as discovery leads rather than primary technical evidence.

| Query or exact-title search | Action / useful outcome |
|---|---|
| `"Onwuchekwa" "knowledge graph" hypoglycemia` | Found formal proceedings DOI and dissertation. |
| `"hypoglycemia" "temporal" "knowledge graph" prediction` | Revisited direct semantic prior work; many irrelevant results. |
| `"GAT-BiGRU" "ocag104"` | Verified publisher route and related graph-paper lead. |
| `"hypoglycemia" "semantic" "2025" "2026"` | Follow-up leads; no definitive equivalent completed benchmark established. |
| `"glucose" "graph" "hypoglycemia" "availability"` | Tested availability-specific framing. No reliable absence inference. |
| `"hypoglycemia" "knowledge graph" -site:researchgate.net -site:eurekamag.com -site:patents.google.com -site:bioportal.bioontology.org` | Broader primary-source discovery. |
| `"GAT-BiGRU" github code` | No verified matching code release established. This does not prove none exists. |
| `"Explainable Multitask Graph Network" glucose` | Located author-uploaded SysCon manuscript. |
| `"Explainable Multitask Graph Network" site:ktu.edu` | Institutional source search. |
| `"GlucoNet-MM" PubMed` | Located bibliographic lead; this pass did not complete full extraction. |
| `"hypoglycemia" "graph neural" -site:researchgate.net -site:eurekamag.com -site:patents.google.com` | Located visibility-graph work and related graphs. |
| `"glucose" "graph" "interpretable" "motif"` | Located MotifDisco; motif pivot is not automatically novel. |
| `"MotifDisco" arxiv` | Verified primary preprint record. |
| `"hypoglycemia" "delayed" "meal" prediction machine learning` | Distinguished meal detection/physiological delays from recording delays. |
| `"temporal graph" "bitemporal" prediction healthcare` | Located established bitemporal graph literature. |
| `"glucose" "graph" "reporting delay"` | Tested narrow topic; no equivalent study confirmed from retrieval. |
| `"hypoglycemia" "knowledge graph" "availability time"` | Narrow check; not evidence of absence. |
| `"glucose prediction" "late" "logged" meals` | Inspected logging-related leads. |
| `"Inductive Representation Learning on Temporal Graphs" arxiv` | TGAT and adjacent temporal graph methods. |
| `"Recurrent Neural Networks for Multivariate Time Series with Missing Values" nature` | GRU-D primary preprint located after publisher retrieval failed. |
| `site:pubmed.ncbi.nlm.nih.gov (hypoglycemia OR hypoglycaemia) ("knowledge graph" OR "graph neural" OR "semantic")` | Returned substantial unrelated material; insufficient for native database screening. |
| `site:arxiv.org ("hypoglycemia" OR "hypoglycaemia") ("graph" OR "semantic")` | Additional scoped discovery; no exhaustive export. |
| `"Onwuchekwa" "hypoglycemia" "2025" "2026" -site:bioportal.bioontology.org` | Institutional dissertation-year corroboration and follow-up leads. |
| `"Explainable Multitask Graph Network for Blood Glucose" site:epubl.ktu.edu` | Additional institutional manuscript search; author-upload route retained. |

Direct retrieval also covered HETER; the visibility-graph chapter and repository; Dynamic Partitioning of Graphs; the accepted Physio-CDE manuscript; the semantic conference PDF and Springer record; TGN; CTRL; bitemporal graphs; the OhioT1DM schema; and relevant sections/records reviewed in the first pass.

## Follow-up literature check — 18 October 2026

| Query / source | Action and finding |
|---|---|
| `type 1 diabetes hypoglycemia prediction temporal graph neural network knowledge graph 2025 2026` | Rechecked recent graph and multimodal hypoglycemia literature. JAMIA's GAT-BiGRU is indexed in PubMed as PMID 42314749; the abstract describes a feature-enriched time-point neighborhood graph, multimodal 30/60-minute prediction, GNNExplainer and counterfactual insulin adjustment. Fine-grained method comparisons still require the full article/supplement. |
| `"hypoglycemia" "temporal" "knowledge graph" prediction` and the University of Siegen repository record | Retrieved and inspected the full 2025 dissertation *Advancing Personalized Hypoglycemia Prediction* (DOI 10.25819/ubsi/10693), including its Chapter 2 semantic KG methods and results. It describes ontology integration, temporal semantics (including TimeML), clinical-text extraction, TransE/DistMult/GCN embeddings, and preliminary MIMIC-III glucose prediction for one patient. The dissertation characterizes the semantic KG research as early-stage; the inspected chapter does not establish a patient-disjoint outpatient benchmark or a relation-ablation result. It is direct conceptual prior work, so novelty cannot rest on proposing a patient-specific semantic KG. |
| `site:pubmed.ncbi.nlm.nih.gov hypoglycemia graph T1D` | Confirmed the GAT-BiGRU PubMed record and issue date. The publisher abstract's time-point graph differs from the event-instance relation question, but it rules out broad novelty claims about temporal graph hypoglycemia prediction. |

Primary sources: [2025 dissertation PDF](https://dspace-backend.ub.uni-siegen.de/server/api/core/bitstreams/1e658634-a368-49e9-93b2-4491e750edb8/content), [JAMIA GAT-BiGRU article](https://doi.org/10.1093/jamia/ocag104), [PubMed record](https://pubmed.ncbi.nlm.nih.gov/42314749/). This was a targeted follow-up, not an exhaustive systematic search; it narrows what can be claimed but cannot prove absence of equivalent studies.

## Inclusion and exclusion decisions

Include direct T1D hypoglycemia KGs/GNNs; graph-based glucose forecasts that overlap in representation; patient-centric diabetes KGs; and adjacent temporal/missingness methods that constrain algorithmic novelty. Include preliminary work, but distinguish it from validated systems. Do not use a conference date, online publication date and dissertation year to count the same study multiple times.

Exclude molecular/drug-target KGs, generic nutritional recommenders, unrelated T2D comorbidity graphs, product pages and patents from the core predictive comparator set. These are not evidence about our exact outpatient CGM prediction task. Do not conclude they are irrelevant to every possible future extension.

Author-uploaded SysCon manuscript: included as primary author content; final IEEE version was not retrieved. Dynamic Partitioning of Graphs: publisher-indexed abstract inspected, direct full-text retrieval failed; retain as an adjacent record rather than assert detailed methods. GlucoNet-MM and some handbook sequence references remain leads requiring full extraction.

## Version and access ledger

- Semantic study: public ESWC 2024 manuscript plus Springer chapter published 28 January 2025, DOI 10.1007/978-3-031-78955-7_4. Final chapter methods were not accessible; do not assume perfect identity with the conference manuscript.
- Visibility-graph study: the University of Bern hosts Hüni's 2024 bachelor thesis, which provides full methods and results for a related author-work predecessor to the S+SSPR 2024 / Springer 2025 chapter (DOI 10.1007/978-3-031-80507-3_6). The thesis verifies a CGM-only natural visibility GNN versus LSTM comparison, an any-future-value-below-70 label, the 120-minute-history/30-minute-horizon setting, and chronological 70/30 within-person validation. The final chapter full text remains unavailable; do not assume it is identical to the thesis.
- GAT-BiGRU: publisher full-text attempt redirected to the abstract. No supplements or exact implementation were obtained. Primary abstract verified through PubMed.
- SysCon graph paper: author manuscript visible on ResearchGate, DOI 10.1109/SysCon66367.2026.11503533; DOI retrieval failed. No authors were contacted.
- Physio-CDE: institution-hosted accepted manuscript inspected. Use the actual acceptance-footer DOI 10.1109/ACCESS.2026.3672553, not the unfilled template header.
- Dataset access: documentation only; no patient files downloaded, account action taken, custodian request sent, or DUA signed. The researcher reports that the OhioT1DM DUA's employee/advisor eligibility rule prevents a direct student request; the cohort plan now follows the [fallback strategy](dataset_fallback_strategy.md).

## Next completion steps

For a submission-grade review, run native database searches with saved queries and exports, deduplicate by DOI/study family, and screen full texts with explicit inclusion reasons. Expand backward and forward citation tracing and inspect final accessible versions. Retain the inaccessible-method flags until resolved. Do not represent this log as a PRISMA flow or invent screening counts: only the curated matrix row count is available.

No paid access, account action or external correspondence was performed. These access limits do not prevent the current revision: the confirmed overlap is already sufficient to withdraw the original broad novelty claim.

## Update: 17 October 2026

This targeted update checked the status and details of close work after the 10 September search. It is not a systematic review.

| Source | Verified from primary or publisher source | Effect on novelty |
|---|---|---|
| Sarwar et al., “GAT-BiGRU: explainable multi-task temporal graph learning for glucose forecasting, hypoglycemia risk, and counterfactual insulin adjustment,” JAMIA 33(9), 1713–1725; [publisher DOI](https://doi.org/10.1093/jamia/ocag104) | Publisher record says published 18 June 2026. Abstract describes feature-enriched time-point nodes connected as a temporal k-neighborhood graph, graph attention plus attention-based BiGRU, 30/60-minute hypoglycemia risk, OhioT1DM and BrisT1D, and GNNExplainer. Supplementary data are linked. Direct full text redirected to a publisher CDN that this search tool could not retrieve. | Stronger prior-art overlap than the earlier abstract-only note reflected. Eliminate any claim that temporal graphs, multimodal graph prediction, or graph explanations for T1D hypoglycemia are first. Full methods/supplement review is required before asserting the event-instance-relations comparison is absent. |
| Piao et al., “GARNN: An Interpretable Graph Attentive Recurrent Neural Network for Predicting Blood Glucose Levels via Multivariate Time Series,” [arXiv record and full text](https://arxiv.org/abs/2402.16230) | The primary preprint describes graph attention over per-time-step multivariate variables, recurrent prediction, CGM plus event variables including meal and insulin, and temporal variable explanations across four data sets. | Graph attention + recurrence, multimodal event features, and explanation are established; novelty must be in controlled event-relation evidence, not the architecture combination. |
| Aboye et al., “SparGlu: A sparse-data evaluation framework for gated recurrent unit-based blood glucose prediction across varying monitoring intervals,” [Wiley DOI](https://doi.org/10.1002/jim4.70055) | The publisher record describes OhioT1DM, CGM/insulin/meal variables, and evaluation after progressively reducing sampling frequency; published in 2026. | Sparse observation and multimodal sequence evaluation are adjacent prior work, not evidence that clinical-event KG relations are novel. |

The [current novelty evidence report](novelty_evidence_report_2026_10_17.md) integrates these leads with the verified Loop pilot results. The search still lacks native database export, formal screening, and full-text review of GAT-BiGRU supplementary methods; no absence claim is justified.

## Update: 18 October 2026 — SysCon full-manuscript methods review

The author-uploaded [SysCon 2026 manuscript](https://www.researchgate.net/publication/404642556_Explainable_Multitask_Graph_Network_for_Blood_Glucose_Forecasting_and_Hypoglycemia_Risk_Classification), DOI 10.1109/SysCon66367.2026.11503533, was re-opened and its graph construction, label, split description, training configuration, and diagnostics were checked in the full text. This is primary author content, not a version-verified IEEE copy.

The manuscript uses BrisT1D and a stable seven-node graph for glucose, insulin, carbohydrates, heart rate, activity, steps, and calories, with directed edges including insulin→glucose, carbohydrates→glucose, heart-rate→glucose, activity→heart-rate, and steps/calories→activity. Each patient/time point is represented by a graph with rolling-window summary features and circadian context. It trains a two-layer GATv2 multitask model for glucose regression and future-point threshold classification at 5/15/30-minute forecast steps. The classification label is a single future glucose value below 3.9 mmol/L, and rows missing that future value are removed; this is not the current project’s incident-any-low-in-horizon label.

The authors report node ablation, top-attended-edge deletion/reinsertion, random edge-drop comparisons, and correlation between attention and physiology priors. Thus physiology-typed multimodal graph edges and graph-structure faithfulness analyses are confirmed prior work. The accessible split text describes stratified train/validation/held-out test sets but does not establish participant-disjoint assignment. Record that property as unverified rather than claiming leakage. Final IEEE text, supplements, and independent reproduction were not obtained.

This finding narrows our candidate distinction to timestamped individual event instances versus fixed modality-summary nodes and event-sequence encodings, under the same event ledger, prediction-time admissibility, patient-disjoint partitions, and incident-within-horizon labels. That distinction is inferred from the inspected representations and does not establish that no equivalent benchmark exists. The relation pilot currently prepared in this repository tests modality-derived message routing; it must not be described as novel clinical knowledge or as a new physiological relation taxonomy.

## Update: 18 October 2026 — event-aware prediction and individualized temporal networks

This targeted search checked primary publisher/full-text sources for recent T1D work that could narrow the proposed event-relation claim. It remains a focused update, not a systematic review.

| Source | Verified from primary source | Effect on novelty |
|---|---|---|
| Taku, Gupta and Singhal, [JMIR Diabetes 2026, e79195](https://doi.org/10.2196/79195) | The full paper uses OhioT1DM 2018/2020 data from 12 participants, including five-minute CGM, pump insulin, discrete self-entered meal/activity and other events, and wearable measurements. Its two-hour state has lag/rolling/time features, including time since insulin dose and meal; it forecasts glucose at 30/60 minutes and uses SHAP/LIME for dose recommendations. | Event-aware T1D forecasting and explanation are prior work. It is not a KG or a matched incident-hypoglycemia relation ablation. A contribution cannot rest on adding meal/insulin events to an explainable T1D model. |
| Pyatak et al., [International Journal of Behavioral Medicine 2026](https://doi.org/10.1007/s12529-026-10483-1) | The publisher record describes person-specific temporal networks from 14 days of blinded CGM and ecological momentary assessment in 158 adults with T1D, relating glucose, experiential variables, and retrospective well-being. | Individualized temporal networks are an established T1D approach, but this is not a near-term hypoglycemia predictor or treatment-event KG. It does not evaluate typed event-relation utility. |
| Fang et al., [iScience 2026, 115294](https://doi.org/10.1016/j.isci.2026.115294); [full text in PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13019577/) | Full text checked 31 October: 1,662 retrospective participants from seven centers; Loop is the primary training source and has 844 participants. The authors report inter-patient five-fold cross-validation, two-hour histories, 5–30-minute BG forecasts, and 30-minute hypoglycemia forewarning using three consecutive readings <70 mg/dL. A separate prospective cohort has 36 perioperative T2D participants. Insulin/carbohydrate/time channels are described as optional, but the main Loop configuration is unclear. | Rules out novelty for first Loop-based 30-minute forewarning, first inter-patient Loop evaluation, or first two-hour input. Prospective validation does not establish T1D clinical validation. The inspected methods do not report an event-instance graph versus matched non-graph relation control; this finding is limited to this source. |

These sources sharpen the safe claim to an empirical question about a specific relation parameterization over individual recorded event instances, compared against equally informed sequence and endpoint/time controls. They do not establish that this exact study has or has not been done elsewhere. A subsequent 19 October development experiment found that graph-generic outperformed an equal-parameter non-graph sequence control on one fold, seed, and epoch; see the dated [paired result](loop_non_graph_capacity_matched_control.md). That pilot does not settle novelty or establish a general graph-relation benefit; replication and relation-specific controls remain necessary.

## Update: 19 October 2026 — event-instance and matched-control boundary

This focused primary-source follow-up checked studies that most directly overlap timestamped meal/insulin events, patient-disjoint prediction, temporal graphs, and hypoglycemia outcomes. It is a targeted update, not a systematic search or evidence of absence. The source-by-source comparison and limitations are recorded in the [event-graph prior-work addendum](closest_prior_work_event_graph_addendum_2026_10_19.md).

| Source | Verified from primary source | Effect on novelty |
|---|---|---|
| Rehman et al., [PLOS Digital Health 2025](https://doi.org/10.1371/journal.pdig.0000996) | Predicts postprandial hypo- and hyperglycemia over four hours after meal onset (the carbohydrate-ingestion timestamp), using a six-hour pre-meal history, carbohydrate intake/time, and meal insulin bolus. Hypoglycemia is ≤70 mg/dL sustained for at least 15 minutes. | Meal-indexed hypoglycemia prediction with meal and bolus information is prior work. The distinction is the rolling incident-low target and controlled event-representation comparison, not merely inclusion of treatment events. |
| *Interpretable Multihorizon Glucose Forecasting…*, [JMIR AI 2026](https://ai.jmir.org/2026/1/e105049) | Uses timestamped meal and bolus records encoded on a five-minute grid, a six-hour history, and an 80/10/10 patient-wise split in 351 adults with T1D; compares TFT and LSTM with matched inputs, partitions, preprocessing, and forecast horizon. The target is continuous glucose. Each configuration was trained once with a fixed seed. | Close prior work for event inputs, patient-disjoint evaluation, and recurrent comparator. Its contrast is nutritional detail and forecasting architecture, not event-instance graph relations for incident hypoglycemia. |
| Aboye et al., [SparGlu 2026](https://doi.org/10.1002/jim4.70055) and Piao et al., [GARNN](https://arxiv.org/abs/2402.16230) | Establish recurrent sparse-data and graph-attentive multivariate time-series treatments of CGM with insulin/meal variables. | These works reinforce that combining graph or sequence models with diabetes event covariates is not itself novel. |

The candidate contribution therefore remains an empirical test of **explicit relations among timestamped individual recorded events versus information-matched event sequences and summaries**, under a prespecified incident-low endpoint, patient-disjoint folds, matched timing and capacity, and relation-structure perturbations. The focused search did not identify a primary report of this complete comparison in the sources screened; this is a bounded search result, not proof that no equivalent exists. This paragraph records the state at the time of the initial search; the Loop experiments have since expanded to two seeds, five folds, and two epochs for the aligned-pooling comparison. The current result and remaining limitations are consolidated in the [31 October evidence report](novelty_evidence_report_2026_10_31.md).

## Update: 19 October 2026 — patient-centric diabetes KGs and additional hypo predictors

The expanded search adds a material ongoing-project lead and two more empirical comparators. This is a targeted extension; it does not convert the search into a systematic review.

| Source | Verified from primary/institutional source | Effect on novelty |
|---|---|---|
| Sarani Rad et al., [patient-centric diabetes PHKG/digital twin, 2024](https://doi.org/10.3390/jpm14040359) | The PubMed record describes a patient-centric personal-health-KG digital twin integrated with HL7 and several diabetes-management applications, including glucose prediction and insulin optimization. The article is conceptually close but does not report the current rolling low-event relation benchmark. | Patient-centric diabetes KG and prediction framing is published prior work; do not claim novelty for that broad combination. |
| Helmut-Schmidt-Universität, [Digital Twins for Diabetes Management project](https://www.hsu-hh.de/dataeng/en/research/current-projects/digital-twins-for-diabetes-management/) | The university project page, updated 6 August 2026, describes a graph-based semantic DiaData representation for a T1D digital twin and short-term hypoglycemia-onset prediction as a primary use case. | This is directly overlapping ongoing work and materially increases uncertainty about broad-concept novelty. It is a project page, not a completed peer-reviewed evaluation; no exact event-instance relation methods or results are provided. |
| Athanasiou et al., [EMBC 2024](https://doi.org/10.1109/EMBC53108.2024.10781638) | PubMed abstract describes personalized, interpretable 0–30- and 30–60-minute hypoglycemia risk models using CGM, insulin, and meal information from 12 T1D patients. | Personalized short-horizon T1D hypoglycemia prediction with meal/insulin context and explanation predates this work; the inspected abstract does not indicate a KG or matched event-representation experiment. |
| Alkhateeb et al., [hour-ahead Ramadan hypoglycemia model, 2026](https://pmc.ncbi.nlm.nih.gov/articles/PMC13119999/) | The primary article uses hourly CGM/wearable aggregates and 36-hour sequences from 33 adults with T1D; its next-hour any-≤70 mg/dL endpoint uses patient-wise splits. | Patient-wise temporal multimodal hypoglycemia prediction is established. The Ramadan-specific aggregated sequence representation does not test treatment-event relations. |
| Rad et al., [JMIR Diabetes digital-twin scoping review, 2026](https://doi.org/10.2196/83059) | The review used PRISMA-ScR/JBI methods, searched PubMed, IEEE Xplore, Scopus, and Web of Science through 23 June 2025, and included 28 empirical diabetes digital-twin studies; it discusses the 2024 PHKG work. | Useful broad field context, but the cutoff predates the HSU project's 2026 update and the review does not specifically settle the clinical-event relation benchmark. |

Together these sources rule out broader claims such as “first patient-centric T1D knowledge graph,” “first KG for hypoglycemia,” or “first patient-wise multimodal hypoglycemia model.” The candidate claim remains narrowly about an information-, timing-, and capacity-controlled evaluation of individual recorded-event relations for a rolling incident-low outcome. Both novelty and benefit remain **provisional** until focused full-text screening is extended and the relation perturbations and cross-fold/seed model fits are completed.

## Update: 30 October 2026 — primary-source verification

The official ESWC proceedings PDF, OUP JAMIA article, and HSU project page
were reopened and checked against the claims in this log. An author-uploaded
full SysCon 2026 manuscript was also examined, with the final publisher text
still not available in the reviewed sources. The JAMIA and SysCon records have
overlapping authors and subject matter; treat them as closely related outputs
from one research line, not independent replications, until their data and
experiment overlap is resolved. The findings and source-specific limits are
recorded in [`primary_source_novelty_check_2026_10_31.md`](primary_source_novelty_check_2026_10_31.md).

This focused verification does not convert the literature search to a
systematic review and does not justify a global absence or “first” claim.

## Update: 31 October 2026 — direct graph-hypoglycemia and event-cause precedents

Fresh primary-source checks added three records with consequences for claim
scope:

| Source | Primary-source finding | Consequence |
|---|---|---|
| Cakiroglu et al., [Scientific Reports 2024](https://www.nature.com/articles/s41598-024-82649-4) | Extended de Bruijn graph forecasts pediatric T1D hypoglycemia within about 30 minutes; 15 children; leave-one-out evaluation reported. | Graph-based short-horizon hypoglycemia prediction is prior work. The graph is over discretized glucose patterns rather than timestamped treatment-event instances. |
| Hüni, Garcia-Tirado & Riesen, [S+SSPR chapter](https://link.springer.com/chapter/10.1007/978-3-031-80507-3_6), plus Hüni's [2024 University of Bern thesis](https://prg.inf.unibe.ch/wp-content/uploads/2024/08/BA_FabianHuni.pdf) and [author dataset repository](https://github.com/fabianHueni/cgm-visibility-graph-dataset) | The thesis evaluates CGM-only LSTM and natural-visibility GNNs on 37 people with T1D; labels any future <70 mg/dL and includes 120-minute input / 30-minute horizon. It reports mean F2 0.348 vs 0.409 at that setting. | The thesis fits separate models per patient and chronologically splits each person's ordered samples 70/30; this is not patient-disjoint. Parameter matching is not documented. The final chapter may differ from the thesis. A broad first graph, graph-vs-sequence, or first matching history/endpoint claim is untenable; event-instance relations under patient-disjoint matched controls remain distinct but provisional. |
| Zaitcev et al., [Frontiers 2023](https://www.frontiersin.org/journals/clinical-diabetes-and-healthcare/articles/10.3389/fcdhc.2023.1095859/full) | Retrospective classification of patient-labeled hypoglycemia causes using time context, insulin, food, activity, and self-care from 54 people with T1D. | Context-aware cause interpretation is prior work, but the task is after-episode cause classification rather than prospective incident-low risk. |

The review remains a focused, source-linked novelty assessment, not a
systematic review. These findings narrow the candidate contribution to the
specific controlled comparison of timestamped event-relation message passing
against time-aligned pooling under identical inputs, timing, capacity, splits,
and incident-low labels. The experiments currently favor pooling; that result
is bounded to the tested Loop release, folds, models, and two-epoch budget.

## Update: 31 October 2026 — focused follow-up query set

The following exact-topic queries checked whether less obvious graph/event
precedents changed the novelty boundary. Search-engine results were treated
as leads and claims were retained only when traceable to publisher, PubMed,
or primary full-text records.

| Query | Result and handling |
|---|---|
| `site:pubmed.ncbi.nlm.nih.gov (hypoglycemia OR glucose) temporal graph type 1 diabetes prediction event graph` | Returned the already-screened Sarwar et al. JAMIA temporal GAT-BiGRU paper; the PubMed abstract directly describes time-point feature nodes, temporal graph message passing, and 30/60-minute hypoglycemia risk. No transaction-level event-instance relation ablation is established by the abstract. |
| `"event graph" hypoglycemia prediction diabetes knowledge graph CGM` | No new verifiable clinical event-instance KG benchmark was found among the returned results; unrelated and low-quality pages were excluded. This is not evidence of absence. |
| `"LSTM Networks and Graph Neural Networks for Predicting Events of Hypoglycemia" citation` | Confirmed authors and S+SSPR 2024 bibliographic record, DOI, and closed-access chapter. Followed the author and dataset repository to the University of Bern's 2024 bachelor thesis; inspected its CGM-only features, visibility-graph construction, horizon labels, patient-level chronological split, and F2 table. The thesis is related author work, not proof that the Springer chapter is identical. [Official thesis](https://prg.inf.unibe.ch/wp-content/uploads/2024/08/BA_FabianHuni.pdf), [publisher chapter](https://link.springer.com/chapter/10.1007/978-3-031-80507-3_6), [dataset repository](https://github.com/fabianHueni/cgm-visibility-graph-dataset). |
| `type 1 diabetes hypoglycemia prediction graph neural network insulin meal event relations temporal` | Surfaced adjacent CGM/meal/insulin predictors and established graph-hypoglycemia records, but no validated same-information, same-timing, capacity-matched event-relation study in the returned source set. Relevant primary records were added or retained in the matrix; the query does not certify novelty. |

This follow-up is query-documented but is still not a database search with
reproducible export, duplicate screening, and full-text eligibility review.
A genuine systematic review remains an open task if the paper will make any
field-wide novelty claim.

During this pass, a direct methods check of the JAMIA GAT-BiGRU article was
attempted through the OUP page, its PubMed Central record (PMCID PMC13580734),
and Europe PMC full-text endpoint. Those retrieval attempts failed in this
research interface; the PubMed abstract remains the verified evidence. This
does not establish that the article is unavailable or paywalled. Its event
node construction and participant split must therefore stay marked unknown
until the full text or supplement is reviewed.

## Update: 31 October 2026 — event-aware and interpretable model check

| Query / source | Primary-source finding | Novelty consequence / limit |
|---|---|---|
| `"nocturnal hypoglycemia" "attention-LSTM" T1D 2026` and exact-title search | PubMed PMID 42224311 identifies Tziavaras, Athanasiou and Nikita, *IEEE Transactions on Biomedical Engineering* (ahead of print, 1 June 2026), DOI 10.1109/TBME.2026.3698300. The abstract describes an autoencoder-guided attention-LSTM using 24-hour CGM/meal/insulin inputs for nocturnal-hypoglycemia risk up to 12 hours ahead, trained/tested with OhioT1DM and externally evaluated on SMARTDIAB. | Temporal event-aware inputs, physiology-guided prediction, attention-based interpretation, and external validation are established prior work. It is not an event-instance graph comparison. Full text and detailed split mechanics were not inspected. [PubMed](https://pubmed.ncbi.nlm.nih.gov/42224311/). |
| `"in-hospital hypoglycemia" T1DM interpretable multicenter 2026` | Full Frontiers article by Zhang et al., DOI 10.3389/fendo.2026.1816599, reviewed. It studies 1,498 inpatients across five Chinese hospitals, 65 demographic/clinical/comorbidity/laboratory predictors, capillary glucose <3.9 mmol/L, and random 70/30 development/held-out division with internal five-fold tuning. | Interpretable T1D hypoglycemia-risk models and within-cohort held-out prediction are established broadly, but this encounter-level inpatient task does not test rolling CGM prediction or event-graph relations. [Full article](https://www.frontiersin.org/journals/endocrinology/articles/10.3389/fendo.2026.1816599/full). |

These sources do not change the candidate distinction: a narrowly scoped,
information/timing/capacity-matched test of event-instance graph relations
versus non-graph event controls. They further rule out broad claims based on
temporal context, explainability, multimodal insulin/meal inputs, or external
validation alone. Search coverage remains targeted, not systematic.


## Update: 31 October 2026 — multimodal sequence and event-aware T1D models

Exact follow-up queries:

- `site:pubmed.ncbi.nlm.nih.gov type 1 diabetes hypoglycemia prediction graph neural network temporal graph insulin meal events CGM`
- `"hypoglycemia prediction" "event graph" insulin meal diabetes CGM`
- `"clinical event relations" graph hypoglycemia prediction diabetes`
- `site:arxiv.org T1D hypoglycemia prediction event graph insulin meal relations`
- `A hypoglycemia early alarm method for patients with type 1 diabetes based on multi-dimensional sequential pattern mining authors DOI`
- `Enhancing self-management in type 1 diabetes with wearables and deep learning CGM meal bolus 60-minute hypoglycemia`

| Primary source | Verified finding | Handling in the novelty assessment |
|---|---|---|
| Ma et al., [PubMed/Heliyon 2022](https://pubmed.ncbi.nlm.nih.gov/36387535/) | Uses glucose, meal, and insulin time series in a multidimensional sequence database, UniSeq pattern mining, and OhioT1DM early-alarm evaluation; abstract reports 75.76% sensitivity, 75% precision, 75.38% F1 and 25.17-minute mean warning. | Added as direct prior art for event-informed sequence-pattern alarms. It is not a graph-relation ablation; exact split mechanics and label comparability remain unverified.
| Zhu et al., [npj Digital Medicine 2022](https://www.nature.com/articles/s41746-022-00626-5) | ARISES combines CGM, meal/bolus diary inputs and wearable physiology for glucose forecasts and hypo-/hyperglycemia warnings in a six-week, 12-adult study; attention-RNN and 60-minute performance are reported. | Added as prior art for multimodal personalized prediction and real-time warnings. Proprietary small cohort; not a transaction-event graph test.
| Athanasiou et al., [PubMed/EMBC 2024](https://pubmed.ncbi.nlm.nih.gov/40039236/) | Abstract reports CGM, insulin and meal records from 12 people with T1D, an insulin-signaling model, tree ML, TreeSHAP, and 0–30 / 30–60 minute risk windows. | Existing matrix record retained and promoted into the primary-source note/report. Detailed splits and availability remain unverified from the abstract.

This search is targeted and source-linked, not a systematic review. Search-result text was treated as a discovery route; claims were retained only where traceable to primary PubMed, publisher, or full-text records. These findings rule out novelty based on event context, multimodal glucose/meal/insulin sequences, personalized warning, or real-time deployment alone. They do not resolve the narrow matched event-instance-relation question.

### Update: 31 October 2026 — publisher and PubMed cross-search

Additional searches used exact-title and combined concept queries across
PubMed, IEEE Xplore, Oxford Academic, Springer Nature, and publisher records:

- `site:pubmed.ncbi.nlm.nih.gov ("knowledge graph" OR "graph neural network") type 1 diabetes hypoglycemia prediction`
- `site:ieeexplore.ieee.org type 1 diabetes hypoglycemia graph neural network CGM insulin meal prediction`
- `site:academic.oup.com diabetes temporal graph hypoglycemia prediction insulin meal events`
- `"hypoglycemia" "event-level" graph type 1 diabetes prediction`
- `"GAT-BiGRU" "OhioT1DM" "BrisT1D" 2026`
- `"Glucose forecasting and hypoglycemia forewarning" MT-HypoNet 2026`
- `"Glycemic-aware and architecture-agnostic training framework" AZT1D`

| Primary source | Verified finding | Novelty consequence and boundary |
|---|---|---|
| Sarwar et al., [JAMIA 2026](https://academic.oup.com/jamia/article/33/9/1713/8711207), [PubMed](https://pubmed.ncbi.nlm.nih.gov/42314749/) | Temporal k-neighborhood graph over feature-enriched CGM time points; GAT plus BiGRU; multimodal 30/60-minute risk; OhioT1DM/BrisT1D and GNNExplainer. Publisher abstract verified; full text/supplement retrieval remained incomplete in this browser pass. | Rules out broad temporal-graph hypoglycemia/explainability claims. Event-instance relation comparison remains unverified, not absent. |
| Khamesian et al., [GLIMMER full article](https://doi.org/10.1186/s44398-026-00032-x) | Springer full text confirms CGM, basal, bolus and carbohydrate features; OhioT1DM and AZT1D (25 people, 26,707 hours); AZT1D splits are within-person chronological; dysglycemia-weighted forecasting; model/dataset resources are linked. | Multimodal features and public event-rich datasets are not novel. It does not test event-instance graph relations or same-input graph controls. |
| Fang et al., [iScience 2026](https://doi.org/10.1016/j.isci.2026.115294), [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC13019577/), [PubMed](https://pubmed.ncbi.nlm.nih.gov/41907406/) | Full text confirms 844 Loop participants and inter-patient five-fold evaluation; two-hour input, 30-minute hypoglycemia forewarning, sustained-low label, and separate 36-person perioperative T2D prospective cohort. Optional event-channel configuration remains unclear. | Establishes a very close Loop task/cohort precedent; it does not test event-instance relation utility. Prospective T2D findings do not establish prospective T1D transfer. |

This remains a targeted cross-search, not a systematic review: database
exports, independent title/abstract screening, and full-text access checks for
every candidate have not been completed. Matrix records were added for GLIMMER
and MT-HypoNet; the duplicate MT-HypoNet entry was merged after source
re-verification. At that update snapshot the matrix contained 39 unique papers; the latest
31 October addendum below raises it to 42. No “first” or absence claim
follows from this pass.

### Additional PubMed-indexed graph/event queries — 31 October 2026

The following additional web-indexed searches were run to stress-test the
narrow event-instance/relation claim. They are discovery searches and do not
replace native PubMed, IEEE Xplore, or ACM database exports.

| Query | Sources/findings checked | Handling |
|---|---|---|
| `type 1 diabetes hypoglycemia prediction event graph insulin meal event nodes temporal relations` | Returned Sarwar et al.'s JAMIA GAT-BiGRU, MT-HypoNet, and adjacent graph/context work. | PubMed/OUP abstracts confirm temporal feature-time-point graph nodes. The OUP supplement was separately obtained and reviewed; it adds k=10 past-to-present edges, 23-dimensional time-point nodes, and split descriptions, but does not settle the detailed event-node or matched-control question. |
| `glucose forecasting graph neural network insulin bolus meal events relation edges T1D hypoglycemia` | Returned GAT-BiGRU, GARNN and graph-attention glucose forecasting records. | These establish graph-based multimodal/time-series prediction and explanation; no returned primary source established the same-input, same-timing, capacity-matched event-instance relation experiment. This is not a claim of absence. |
| `"event graph" "hypoglycemia" "type 1 diabetes" prediction` | No new verified direct event-instance hypoglycemia graph benchmark in the returned results. | Excluded unrelated event graphs and non-primary/low-quality pages; no absence inference. |
| `"clinical event" knowledge graph hypoglycemia prediction insulin meal graph neural network diabetes` | Returned general clinical event-KG methods and the existing T1D semantic-KG / graph-prediction sources. | General EKG methods do not themselves establish a T1D predictive benchmark; broad KG novelty remains ruled out by direct T1D KG precedents. |
| `site:pubmed.ncbi.nlm.nih.gov type 1 diabetes hypoglycemia prediction graph neural network glucose prediction` | Reconfirmed PubMed records for GAT-BiGRU, MT-HypoNet, and static/inpatient T1D risk studies. | PubMed abstracts and linked primary articles were treated separately; static clinical risk models were not treated as direct rolling-CGM comparators. |
| `site:ieeexplore.ieee.org T1D hypoglycemia graph neural network glucose prediction event` and `site:dl.acm.org type 1 diabetes hypoglycemia graph event prediction glucose` | Search-engine indexing yielded no newly verified equivalent study. | These domain-restricted web searches are not native index exports and cannot support an absence claim. |

The PubMed record for Sarwar et al. lists PMCID PMC13580734. Through the
WebBridge, the PMC record was inspected and reports that the main article will
be publicly available there on 18 June 2027. The OUP page provides only its
abstract in this session, but the linked supplementary DOCX was accessible and
was inspected. The supplement's relevant details and unresolved split/event
questions are recorded in the source note and novelty matrix. The matrix marks
the main-article embargo separately from the available supplement. The
retrieved DOCX was 1,042,073 bytes, passed ZIP integrity validation, and had
SHA-256 `b766614b2eaffbe46335f37db4b9709b78adf623483f0e439f85a8ea7fb1e3d8`;
it was kept in temporary storage rather than added to the project archive.

### Update: 31 October 2026 — multimodal/event-availability and safety comparators

Additional targeted searches surfaced adjacent primary studies not previously represented in the matrix. Their full source-bounded implications are captured in [the focused update](targeted_prior_art_search_2026_10_31.md).

| Query / source | Primary-source finding | Novelty consequence / limit |
|---|---|---|
| `"Predicting Adverse Events for Patients with Type-1 Diabetes Via Self-Supervised Learning" DOI`; author paper and repository | Zheng et al., BG-BERT (ICASSP 2024), forecasts glucose on OhioT1DM and DiaTrend with aligned CGM, basal/bolus insulin and carbohydrate data; evaluates forecast-point low-glucose sensitivity at 30/60 minutes; author-linked code is public. | Multimodal context and low-glucose detection from glucose forecasts are prior work. It is non-graph; outcome is not incident-within-horizon and the 64/16/20 split unit is unverified. [Author paper](https://sijieji.github.io/pdf/Glucose_Prediction_ICASSP_2024.pdf), [code](https://github.com/aiot-lab/BG-BERT), [DOI](https://doi.org/10.1109/ICASSP48485.2024.10446832). |
| `"Future-aware blood glucose forecasting" insulin meal knowledge distillation` | Sun et al. (Scientific Reports 2026) use future insulin/carbohydrate disturbances for a teacher and distill to a history-only sequence student; OhioT1DM and AZT1D; trajectory forecasts up to 120 minutes. | Event-aware sequence modeling and deployment-availability constraints are not new. This is continuous glucose forecasting, not event-instance graph relations or incident-low classification. [Publisher full text](https://www.nature.com/articles/s41598-026-41787-7), [PubMed](https://pubmed.ncbi.nlm.nih.gov/41764313/). |
| `"PhyNet" safe explainable blood glucose forecasting insulin carbohydrate` | PubMed abstract for Calzavara et al. (IEEE TBME 2026) reports T1DEXI/MetaboNet, 848 subjects, six deep-learning baselines and counterfactual physiological response tests; IEEE full text was inaccessible in this pass. | Supports evaluating physiological/explanation faithfulness separately from predictive accuracy; does not test event-instance graphs. [PubMed](https://pubmed.ncbi.nlm.nih.gov/42685163/), [IEEE](https://ieeexplore.ieee.org/abstract/document/11675927/). |
| `type 1 diabetes hypoglycemia prediction event graph insulin meal event nodes temporal relations`; `glucose hypoglycemia prediction event graph insulin bolus meal graph neural network diabetes`; `T1D hypoglycemia graph sequence model same information graph ablation temporal events`; `"event-instance" graph hypoglycemia diabetes prediction` | Targeted graph/event searches re-found established graph and patient-centric predecessors and did not surface a verified exact same-input, same-timing, capacity-matched event-instance relation benchmark. | Treat as scoped search evidence only; no universal absence or “first” claim follows. Native bibliographic database exports and citation-trail screening remain outstanding. |
| `clinical event nodes timestamped visits temporal heterogeneous graph prediction medical events IJCAI 2024` | Official IJCAI TRANS paper models diagnosis, procedure and medication-code nodes attached to time-indexed visit nodes, with chronological visit edges, temporal heterogeneous message passing, and a patient graph explainer for next-visit diagnosis prediction on MIMIC-III, MIMIC-IV and CCAE. | Establishes generic temporal event-node patient graphs and graph explanations as prior methods. It is not a T1D/CGM transaction-level low-risk study; retain only the narrower raw insulin/meal event-to-CGM benchmark distinction. [IJCAI version of record](https://ijcai.org/proceedings/2024/637), [DOI](https://doi.org/10.24963/ijcai.2024/637). |
| `"Risk-based postprandial hypoglycemia forecasting using supervised learning"` | Oviedo et al. (2019) report individualized post-meal/bolus risk models from sensor-augmented pump records for 10 participants, with 240-minute windows and 70/54 mg/dL thresholds. | Meal-triggered hypoglycemia prediction predates this work; cohort and horizon differ, and the abstract reports no graph relation test. [PubMed](https://pubmed.ncbi.nlm.nih.gov/31029250/). |
| `"IDMVis: Temporal Event Sequence Visualization"` | Zhang et al. (2018) describe a T1D clinical design study for a temporal event-sequence visualization; six clinicians qualitatively assessed decision-support workflow, including missing/conflicting record inspection. | Temporal event visualization for T1D is prior art; this is not predictive graph learning. [PubMed](https://pubmed.ncbi.nlm.nih.gov/30136981/). |
| `"Forecasting accuracy is not enough" neural digital twins insulin carbohydrate intervention type 1 diabetes` | Ibrahim et al. (2026) align CGM, basal/bolus and meal inputs, compare patient-specific models across five seeds in Manchester and OhioT1DM, and evaluate counterfactual treatment-response direction separately from forecast error. | Closely relevant control and physiology-evaluation practice, but trajectory forecasts rather than held-out-patient incident-low classification; no event-instance graph relation comparison. [Full text](https://doi.org/10.3389/fendo.2026.1958918). |
| `"A comparative study of explainability methods" blood glucose time-series` | Akrong et al. (2026) evaluate attention, saliency, integrated gradients, SHAP and LIME on six OhioT1DM participants using feature deletion, stability and a scenario-based plausibility heuristic. | Time-series explanation evaluation is prior art; the plausibility score is not clinician validation and the study does not explain graph relations. [Full text](https://doi.org/10.1007/s44163-026-01328-7). |
| `"Hypoglycemia event prediction from CGM using ensemble learning"` | Fleischer et al. (2022) use RUSBoost with one hour of CGM to predict sustained hypoglycemia within 40 minutes in 225 adults; train/test is split by participant, and they include event-based lead time. | Establishes a large patient-level CGM-only early-warning baseline. Its sustained 40-minute label differs from the Loop 30-minute any-low label and it has no event-instance inputs. [Full text](https://www.frontiersin.org/journals/clinical-diabetes-and-healthcare/articles/10.3389/fcdhc.2022.1066744/full). |
| `"Classification of Hypoglycemic Events in Type 1 Diabetes Using Machine Learning Algorithms"` | Cederblad et al. (2023) analyze 449 people and 42,120 events; CGM/FGM models classify likely causes with insulin/carbohydrate validation and a separate clinician-interpretation cohort. | Cause explanation after a detected event is prior work; it is not forward prediction or graph explanation. [PubMed](https://pubmed.ncbi.nlm.nih.gov/37052842/), [publisher](https://link.springer.com/article/10.1007/s13300-023-01403-7). |

The matrix contained 49 unique records at this stage. The 31 October closing check also includes prior work on patient-level CGM-only early warning and retrospective event-cause interpretation, in addition to the meal/bolus-triggered, temporal visualization, physiology-response, and explanation-faithfulness precedents. None is the same rolling incident-low, held-out-patient event-relation comparison. The search is still targeted rather than systematic; absence of an exact hit cannot establish that no equivalent study exists.

### Additional close-source check — 31 October 2026

| Source/query | Primary-source finding | Handling and effect on claim |
|---|---|---|
| [Khokhar et al., arXiv:2610.36363](https://arxiv.org/abs/2610.36363); full PDF reviewed after query `"Reliability-Aware Short-Term Glycemic Risk Prediction"` | 36-page v1 preprint dated 26 October. Uses T1DiabetesGranada (736 people; 5,503,441 anchors), six-hour CGM windows, static/clinical, biochemical, diagnostic, and CGM-context inputs; target is any future observed value <70 mg/dL within 30/60/120 minutes. Compares sequence and multimodal/state-updating models, five patient-disjoint outer folds, and explanation/perturbation checks. It says insulin and carbohydrate intake are missing contextual determinants. Internal train/validation uses chronological anchor split, potentially with patient overlap; exact features/folds/hyperparameters/code are incompletely reported. | Close prior work for task, endpoint, 30-minute horizon, patient-level outer evaluation, multimodal-versus-sequence comparisons, and explanation-reliability evaluation. It does not establish timestamped insulin/meal transaction instances or graph relations. Treat as a preprint; its overlap requires removing novelty claims for the task or general evaluation design and sharpening the study to event-instance relations under matched controls. |
| [Chennareddy and Ma, Endocrine Practice supplement, DOI 10.1016/j.eprac.2026.03.018](https://doi.org/10.1016/j.eprac.2026.03.018); query `"Attention-Augmented Temporal Fusion Transformer for Short-Horizon Hypoglycemia Prediction in Type 1 Diabetes"` | Crossmark verifies title/journal/DOI; the record is 32(4) supplement p. S336. Publisher page returned 403, preventing independent review of its one-page abstract methods. | Added as a bibliographic close comparator only. Dataset, endpoint, split, metrics, and inputs remain unverified from the publisher copy; abstract-transcription details and reported performance are not treated as established evidence. No event-instance graph comparison can be inferred. |

At this stage the matrix contained 51 unique records after duplicate removal (up from 49). This remained a targeted search rather than a systematic review; the newly identified preprint was close in prediction formulation but did not answer the narrow event-instance relation question.

### Follow-up query: insulin/carbohydrate context and meal-anchored prediction (31 October 2026)

Queries: PubMed search for `feature-based real-time hypoglycemia prediction insulin carbohydrate 30 60 minutes`, exact-title searches for `A machine-learning approach to predict postprandial hypoglycemia`, `Prediction of Nocturnal Hypoglycemia From Continuous Glucose Monitoring Data in People With Type 1 Diabetes`, and `Development and Validation of Binary Classifiers to Predict Nocturnal Hypoglycemia in Adults With Type 1 Diabetes`; primary publisher/full-text checks at PubMed/PMC, Springer Nature, and SAGE.

| Record | Finding | Consequence |
|---|---|---|
| Dave et al. (2021), [PubMed](https://pubmed.ncbi.nlm.nih.gov/32476492/), [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8258517/) | Compares short-horizon T1D risk prediction with/without insulin/carbohydrate context, using engineered IOB/COB features; source review notes event fields were available for only a subset and the abstract/body conflict on the 30-minute incremental effect. | Event-derived context and the event-versus-CGM feature question are not novel. This does not test raw event-instance relations versus matched non-graph inputs. Avoid a definitive claim about 30-minute benefit until tables are reconciled. |
| Seo et al. (2019), [primary article](https://link.springer.com/article/10.1186/s12911-019-0943-4) | Meal-anchored postprandial event prediction from CGM-derived glucose trends, with a 30-minute prediction horizon; meal time inferred from calibration/fingerstick timing. | Meal-indexed risk prediction predates this project, but individual meal/insulin event representations were not tested. |
| Jensen et al. (2020), [primary article](https://journals.sagepub.com/doi/10.1177/1932296819868727) | Bedtime nocturnal prediction considered meal/bolus candidate features; the paper reports a participant-level holdout and a stricter nocturnal endpoint. | Contextual records have been considered in hypoglycemia models; retained feature effects and rolling 30-minute comparability are limited. |
| Afentakis et al. (first online 2023; issue 2025), [publisher](https://journals.sagepub.com/doi/10.1177/19322968231185796), [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11696951/) | Bedtime nocturnal classifier uses evening carbohydrate-on-board as an aggregate feature alongside CGM/activity measures. | Aggregate carbohydrate context is prior art; this is not transaction-level event relation modeling. |

The addition of these four records brought the matrix to 55 unique entries at that point. Primary-source notes: [event-context source check](primary_source_event_context_2026_10_31.md). The key remaining candidate remains a controlled comparison of event-instance relations against same-information, same-timing non-graph controls, not the use of insulin/carbohydrate context itself.


### CGM-only nocturnal comparator source note (31 October 2026)

Vu et al. (2020) was added as an adjacent large-scale comparator after checking the primary PubMed/PMC records. Their six-hour overnight model uses CGM-derived features only; the paper says user-uploaded meal/bolus data were inconsistent, and the explored holdout was chronological by stream time rather than demonstrated patient-disjoint. This does not alter the event-relation novelty boundary, but it reinforces the need for a serious CGM-only benchmark. See [primary PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC7153099/) and [PubMed](https://pubmed.ncbi.nlm.nih.gov/32308884/). The matrix contained 56 unique records at this dated update.


## Update: final targeted primary-source check — 31 October 2026

Queries included the exact title/phrase for dynamic event timing knowledge
graphs, T1D glucose prediction with insulin/meal content, OhioT1DM glycemic
event prediction and representation, postprandial hypoglycemia, sustained
low-glucose alerts, and wearable nocturnal prediction. Primary full text was
checked for Zecchin et al. (2016), Li et al. (2020), and Dave et al. (2021);
primary abstract/record-level evidence was checked for Apicella et al. (2026),
Voegeli et al. (2025 workshop), and Oviedo et al. (2019). The relevant records
and conservative interpretation are in the [focused search addendum](targeted_prior_art_search_2026_10_31.md).

This pass found that typed temporal event-order knowledge graphs and diabetes
event streams are already combined in general stream-prediction research,
although the inspected PVLDB paper reports no diabetes hypoglycemia-risk
performance. Direct CGM versus CGM-plus-insulin/meal comparison also dates to
2016 for glucose regression; later work tests contextual inputs for
hypoglycemia risk and OhioT1DM representation choices. These findings withdraw
novelty for event-order graph construction, context inclusion, and
representation comparison in general. They do not resolve whether the exact
same-information/timing/capacity-matched event-instance relation comparison
for the present endpoint has been published elsewhere. The literature matrix
now has 62 unique records after correcting Seo et al. (2019)'s author-key
label; no systematic screening flow is claimed.


## PubMed-focused indexed-result update — 31 October 2026

The title/phrase search identified (a) Quader et al.'s 2026 PRISMA-guided
hypoglycemia-prediction meta-analysis (its own 611-record/20-study flow),
(b) Tziavaras et al.'s OhioT1DM/SMARTDIAB attention-LSTM nocturnal model with
CGM/meal/insulin inputs and mapped attention, and (c) Ferstad et al.'s
three-cohort next-week CGM-only risk model. The records and scope limits are
entered in the matrix and source notes. The web-indexed retrieval did not
produce a native PubMed export or exact yield for our own queries; the
meta-analysis PRISMA count is not ours. Its included-study appendix remains a
backward-citation source to inspect. Matrix count: 64 unique records.


## Backward citation check — event-instance relation prior art

The citation-chain pass located Acharya and Lee (2014), whose primary paper
describes a temporal causal network with an event-instance layer and diabetic
monitoring examples/data involving insulin, glucose, meal events and
hypoglycemic symptoms. It evaluates causal-network reconstruction rather
than future hypoglycemia prediction. Postiglione et al. (2024) provide a
separate temporal patient-KG precedent for future-disorder prediction in
MIMIC-III. These records materially narrow the novelty language: the
representation family is established, while the specific matched predictive
comparison remains the empirical candidate. Matrix count: 66 unique records.


A query-by-query protocol and search-boundary ledger is now available at
[PubMed search protocol](pubmed_search_protocol_2026_10_31.md). It makes
explicit that 66 is the curated matrix size, not the number of records
retrieved, and that no PRISMA screening counts are available for this search.


**Backward citation check — Quader et al. review references (31 October 2026):**
The review's publisher reference list was screened for additional T1D contextual
prediction precedents. Primary checks added Bertachi et al. 2020 (timestamped
CGM, meals, insulin and activity for nocturnal risk), Cichosz et al. 2015
(CGM versus CGM+HRV prediction), and Mosquera-Lopez et al. 2023 (activity-risk
prediction with glucose, insulin and activity, including an independent pilot
test). Matrix count: 69 unique records. This is backward citation screening,
not a systematic search, and does not constitute this project's PRISMA yield.

**Exact-title follow-up — Yu et al. (2024):** Checked the full BMC paper and
PubMed record for a prior-knowledge-guided dynamic-attention nocturnal warning
model. It uses asynchronous multiscale features on OhioT1DM and analyzes 10
participant datasets with within-person temporal train/test intervals. Added
to the matrix as a precedent for multimodal temporal fusion and guided
attention, while noting it is neither held-out-patient evaluation nor an
 event-instance graph ablation. Matrix count: 70 unique records.
