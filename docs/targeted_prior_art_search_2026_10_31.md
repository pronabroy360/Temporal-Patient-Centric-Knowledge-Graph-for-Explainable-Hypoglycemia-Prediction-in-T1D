# Targeted prior-art search update — 31 October 2026

## Scope and method

This is a focused follow-up to the project’s earlier prior-art review, aimed at
three claims: whether T1D hypoglycemia forecasting with multimodal event inputs
is new; whether explicitly modeling event availability/timing in a sequence is
new; and whether event-instance graph relations have already been compared
against a matched non-graph representation. Queries were run on 31 October 2026
using title/phrase, PubMed, publisher, conference, and code-repository searches
for combinations of *type 1 diabetes*, *hypoglycemia*, *graph neural network*,
*meal*, *insulin*, *event*, *temporal relation*, and *matched graph/sequence*.
Primary publisher, PubMed, author-hosted full-text, and author-linked code
records were inspected where available. This is not a systematic review: no
native Scopus/Web of Science export, deduplicated screening flow, or exhaustive
citation search was completed.

## Directly relevant general temporal-event-graph precedent

Chen et al.’s IJCAI 2024 paper *Predictive Modeling with Temporal Graphical
Representation on Electronic Health Records* (TRANS) represents each patient’s
EHR with medication, procedure, diagnosis-code nodes and timestamped visit
nodes. It links medical-code nodes to visits and adds chronological edges
between visits, applies temporal heterogeneous message passing and structural
encodings, and includes a patient graph explainer. It evaluates next-visit
diagnosis prediction on MIMIC-III, MIMIC-IV, and MarketScan CCAE.

TRANS means the generic idea of connecting clinical event nodes to
time-indexed patient/visit nodes, propagating messages over temporal relations,
and explaining predictions with a subgraph is established. Its events are
coded diagnoses, procedures, and medications organized by clinical visits;
the study is not T1D CGM forecasting and does not test raw timestamped pump or
meal transaction instances, an incident-low-within-horizon endpoint, or a
same-information/timing/capacity-matched graph-versus-non-graph comparison.
Accordingly, the defensible distinction is a narrowly scoped empirical test
of raw insulin/meal event-instance alignment in a CGM prediction benchmark,
not the invention of temporal event graphs or patient-centered graph
explanations.

Source: [official IJCAI 2024 version of record](https://ijcai.org/proceedings/2024/637),
[DOI](https://doi.org/10.24963/ijcai.2024/637),
[official paper PDF](https://www.ijcai.org/proceedings/2024/0637.pdf).

## Related T1D event forecasting and temporal decision-support precedents

Oviedo et al. (2019) developed patient-personalized supervised models for
insulin-induced postprandial hypoglycemia after a meal/bolus. The study used
retrospective sensor-augmented pump data from 10 people with T1D and evaluated
risk over 240 minutes using 70 and 54 mg/dL thresholds. This establishes that
meal/bolus-indexed hypoglycemia forecasting predates the present project. Its
small, personalized cohort and postprandial trigger/horizon differ from a
patient-disjoint rolling 30-minute incident-low task; the inspected record
does not describe an event-instance graph or matched relation ablation.

Zhang et al.'s IDMVis (2018) is an earlier T1D temporal event-sequence
visualization and treatment decision-support system. It organizes
multidimensional records along a timeline and was evaluated qualitatively with
six clinicians. The authors report that clinicians could inspect patterns
and identify missing or conflicting data. This rules out a broad claim to be
the first temporal event-sequence representation or visualization for T1D
care. IDMVis is a clinical visualization, not a predictive graph model or a
hypoglycemia benchmark.

Sources: [Oviedo et al. PubMed record](https://pubmed.ncbi.nlm.nih.gov/31029250/),
[IDMVis PubMed record](https://pubmed.ncbi.nlm.nih.gov/30136981/),
[IDMVis DOI](https://doi.org/10.1109/TVCG.2018.2865076).

## Recent methodological precedents for physiology and explanation evaluation

Ibrahim et al. (published 14 October 2026) evaluate patient-specific neural
glucose forecasting models on two multimodal cohorts: Manchester T1D-UOM
(13 participants) and OhioT1DM (12). Their inputs align CGM, basal insulin,
bolus and meal events on a five-minute grid and derive insulin-on-board and
carbohydrate-on-board exposure proxies. They compare patient-level results
across five seeds, model/input ablations, and counterfactual insulin and meal
perturbations. Their central result is that glucose forecast error and
directionally plausible response to treatment perturbations are distinct
properties. This is a close precedent for careful matched controls and
physiology/faithfulness evaluation. It remains patient-specific trajectory
forecasting with non-graph models, not held-out-patient incident-low
prediction or event-instance relation testing.

Akrong et al. (2026) compare attention, saliency, integrated gradients, SHAP,
and LIME for BiLSTM glucose forecasts on OhioT1DM's six participants. Their
evaluation includes feature deletion, perturbation stability, and a
scenario-based Clinical Plausibility Score. The latter is a heuristic based
on expected features, and the article explicitly states it does not replace
clinician-in-the-loop validation. This is prior work for quantitative
time-series explanation assessment, not evidence that a graph explanation is
faithful or clinically validated. Its six-person single-dataset design also
limits transfer to larger patient-disjoint benchmarks.

Sources: [Ibrahim et al., Frontiers full text](https://www.frontiersin.org/journals/endocrinology/articles/10.3389/fendo.2026.1958918/full),
[DOI](https://doi.org/10.3389/fendo.2026.1958918);
[Akrong et al., Springer Nature full text](https://link.springer.com/article/10.1007/s44163-026-01328-7),
[DOI](https://doi.org/10.1007/s44163-026-01328-7).

## Patient-level event prediction and post-event interpretation

Fleischer et al. (2022) provide a strong CGM-only comparator precedent: they
trained RUSBoost on one hour of CGM to predict sustained hypoglycemia (below
70 mg/dL for at least 15 minutes) up to 40 minutes ahead in 225 adults with
T1D and 3.7 million readings. The paper reports a 70/30 participant-level
train/test split, within-training cross-validation for tuning, and event-level
lead-time analysis. This rules out novelty for patient-level short-horizon
hypoglycemia event prediction itself and supports requiring a serious CGM-only
baseline. Its sustained 40-minute endpoint and lack of recorded-event inputs
differ from our rolling 30-minute any-low endpoint and event-relation question.

Cederblad et al. (2023) analyzed 449 people with T1D and 42,120 hypoglycemic
events. Clinicians labeled a sample of events; CGM/FGM sequences were used to
classify likely causes, including overestimated bolus, overcorrection, and
excess basal insulin. The study used a patient-separated development
partition and a separate 22-person evaluation with clinician interpretation.
This is prior work for interpreting recorded hypoglycemia events using
insulin/carbohydrate context, but it is retrospective cause classification,
not prospective incident-risk prediction or graph explanation.

Sources: [Fleischer et al., primary Frontiers article](https://www.frontiersin.org/journals/clinical-diabetes-and-healthcare/articles/10.3389/fcdhc.2022.1066744/full),
[PMC full-text record](https://pmc.ncbi.nlm.nih.gov/articles/PMC10012121/);
[Cederblad et al., PubMed](https://pubmed.ncbi.nlm.nih.gov/37052842/),
[Springer article](https://link.springer.com/article/10.1007/s13300-023-01403-7).

## Newly recorded primary-source evidence

### Closest task/evaluation precedent: anchor-based glycemic-risk preprint

Khokhar, Gravino, and Palomba's 26 October 2026 arXiv preprint,
*Reliability-Aware Short-Term Glycemic Risk Prediction Using an Anchor-Based
Comparative Framework of Sequence, Multimodal, and State-Updating Digital-Twin
Models*, is a particularly close methodological comparator. It constructs
5,503,441 anchors from 736 people in T1DiabetesGranada and predicts any observed
future glucose value below 70 mg/dL within 30, 60, or 120 minutes. The input
uses six hours of CGM history sampled every 15 minutes, plus static clinical,
biochemical, diagnostic, and CGM-context/missingness variables. It compares
target-specific sequence models with multimodal/state-updating models under a
five-fold patient-level outer split, and evaluates calibration, explanation
faithfulness/stability, and perturbation behavior. The authors state that no
patients overlap between outer train/development and held-out folds, although
the development training/validation division is chronological at the anchor
level and may place one patient's anchors in both subsets.

This preprint substantially narrows what can be claimed about the project:
the future-window `<70 mg/dL` risk task, 30-minute horizon, patient-disjoint
outer evaluation, multimodal-versus-sequence comparison, and explanation
reliability checks are already represented. It does **not** appear to include
timestamped insulin-delivery or meal transaction instances: its methods list
static/clinical, biochemical, diagnostic, and CGM-context features, and it
explicitly notes insulin and carbohydrate intake as missing contextual
determinants. It does not use a graph or compare event-instance relations with
an information-, timing-, and capacity-matched non-graph control. The
remaining empirical question is therefore narrower still: whether raw,
time-stamped insulin/meal events and their explicit relations add value over
equally available event-aware non-graph representations for this prediction
task. Our current Loop results do not support a graph advantage; this is a
candidate controlled comparison, not a demonstrated contribution yet.

The source is a preprint, not a verified peer-reviewed publication. Its PDF
contains an ACM Transactions on Computing for Healthcare manuscript shell
with placeholder DOI/publication fields. It acknowledges that exact feature
definitions, fold assignments, preprocessing details, hyperparameters, and
evaluation code are not fully specified, and no implementation link was
located in the paper. These limits matter when comparing its numeric results
or attempting reproduction; they do not erase its clear conceptual overlap.

Sources: [arXiv abstract](https://arxiv.org/abs/2610.36363), [full 36-page
preprint](https://arxiv.org/pdf/2610.36363). Relevant method details include
the anchor and endpoint definition (PDF pp. 5–6), input modalities and model
families (pp. 7–8), split protocol (pp. 8–9), and stated reproducibility limits
(p. 10).

### Earlier comparisons using insulin/carbohydrate context

Dave et al. (2021) are a material precedent for evaluating whether treatment
context changes short-horizon hypoglycemia prediction. Their PubMed abstract
describes probabilistic prediction of glucose below 70 mg/dL at 30 and 60
minutes in 112 youth with T1D, and compares a feature-based model with and
without insulin and carbohydrate context. The abstract says those inputs
improved 60-minute but not 30-minute prediction. The article uses engineered
context such as insulin-on-board and carbohydrate-on-board, not an explicit
graph over raw event instances. The accessible abstract and indexed full-text
snippets are not fully consistent on the 30-minute comparison; the effect
direction should therefore not be quoted beyond the abstract unless the tables
are reconciled. This precedent rules out claiming that event-derived context
or an event-versus-CGM feature comparison is itself new.

Other task-adjacent studies reinforce the boundary. Kim et al. (2019) used meal
announcements to define postprandial windows and predicted a <70 mg/dL event
30 minutes ahead from CGM-derived features; meal timing was inferred from
fingerstick/calibration records rather than transaction-level food/insulin
inputs. Jensen et al. (2020) considered CGM, meal, insulin, and demographic
features for bedtime nocturnal risk; the reported final selected feature set
did not retain meal/bolus features. Afentakis et al. (first published online
2023; journal issue 2025) included carbohydrate-on-board, an aggregate of
evening intake, in a bedtime nocturnal classifier. These are distinct from
rolling incident-low prediction and do not compare event-instance relations
against an equally informed and timed non-graph representation.

Sources: [Dave et al., PubMed](https://pubmed.ncbi.nlm.nih.gov/32476492/),
[Dave et al., PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC8258517/);
[Kim et al., primary BMC article](https://link.springer.com/article/10.1186/s12911-019-0943-4);
[Jensen et al., primary publisher article](https://journals.sagepub.com/doi/10.1177/1932296819868727);
[Afentakis et al., primary publisher article](https://journals.sagepub.com/doi/10.1177/19322968231185796),
[PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC11696951/).

### Additional close comparator: attention-augmented TFT abstract

The 2026 *Endocrine Practice* supplement record “Attention-Augmented Temporal
Fusion Transformer for Short-Horizon Hypoglycemia Prediction in Type 1
Diabetes” is verified as a one-page supplement abstract (32(4), S336; DOI
10.1016/j.eprac.2026.03.018). The publisher page returned 403 in this pass.
The author-linked repository identifies T1DiabetesGranada, but the abstract's
reported inputs, endpoint details, split, and metrics could not be checked
against the publisher copy. Treat it as evidence that an attention-based
short-horizon T1D hypoglycemia abstract exists; do not rely on its reported
performance figures or claim a verified methods comparison until the official
abstract is accessible. It does not currently establish an event-instance
graph comparison.

Sources: [Crossmark record](https://crossmark.crossref.org/dialog?cm_version=v2.0&doi=10.1016%2Fj.eprac.2026.03.018&domain=www.endocrinepractice.org&uri_scheme=https%3A), [publisher DOI](https://doi.org/10.1016/j.eprac.2026.03.018), [author-linked code](https://github.com/andrewma91/Attention-Augmented-TFT-for-Hypoglycemia-Prediction-in-Type-1-Diabetes) (discovery/context only).

### BG-BERT: multimodal glucose forecasting with low-glucose evaluation

Zheng, Ji, and Wu’s ICASSP 2024 paper *Predicting Adverse Events for Patients
with Type-1 Diabetes via Self-Supervised Learning* presents BG-BERT for glucose
trajectory forecasting on OhioT1DM and DiaTrend. The author-hosted paper says
the model uses historical CGM records and aligned carbohydrate, bolus, and
basal information; it forecasts future glucose values for 30- and 60-minute
horizons, then evaluates detection sensitivity at forecast values below
70 mg/dL. The paper describes 64/16/20 train/validation/test partitions, but
does not establish that partitions are participant-disjoint. It is a
non-graph masked-pretraining plus LSTM/CNN/MLP forecasting approach, not an
incident-within-window event-graph experiment. The author-linked repository
contains data conversion and model-training code for OhioT1DM and DiaTrend.

This is prior art for multimodal insulin/carbohydrate context and forecasting
low glucose on OhioT1DM, but its pointwise forecast-derived endpoint and
unverified split unit differ from this project’s patient-disjoint
incident-within-horizon target. It rules out novelty based only on using
multimodal inputs or forecasting hypoglycemic glucose values.

Sources: [author-hosted full paper](https://sijieji.github.io/pdf/Glucose_Prediction_ICASSP_2024.pdf),
[author-linked implementation](https://github.com/aiot-lab/BG-BERT),
[DOI](https://doi.org/10.1109/ICASSP48485.2024.10446832).

### Future-aware sequence forecasting with privileged event information

Sun, Li, and Yu’s 2026 *Scientific Reports* paper uses an offline Transformer
teacher with historical CGM plus future insulin/carbohydrate disturbances and
distills it into a sequence-to-sequence student that receives historical
inputs only at inference. Its full-text methods describe bolus and meal inputs
through insulin-on-board (IOB) and carbohydrate-on-board (COB) histories,
OhioT1DM and AZT1D evaluation, and glucose trajectory forecasts up to 120
minutes. OhioT1DM uses its supplied train/test files; the article describes
the AZT1D development/test division as first 80% versus remaining 20% of data.
This is a sequence-model knowledge-distillation study, not event-instance
graph modeling or an incident-low classification benchmark.

It is close precedent for modeling timestamp-aligned insulin/meal effects in
sequences and for explicitly testing an availability mismatch between
training-time future disturbances and inference-time inputs. Therefore event
timing, event-aware sequences, and availability-aware training are not
standalone novelty claims. The remaining distinction must concern whether
explicit event-instance relations add value against controls with the same
information and timing, on the project’s stated endpoint.

Sources: [publisher full text](https://www.nature.com/articles/s41598-026-41787-7),
[PubMed record](https://pubmed.ncbi.nlm.nih.gov/41764313/).

### PhyNet: physiology and explanation safety checks

Calzavara et al.’s 2026 IEEE TBME paper *PhyNet: A Physiology-Constrained
Monotonic Neural Network for Safe and Explainable Blood Glucose Forecasting*
reports glucose forecasting with CGM, carbohydrate, and insulin inputs on
T1DEXI and MetaboNet (848 participants total). The PubMed abstract describes
comparison with six deep-learning baselines and counterfactual tests of
physiological responses to changing insulin/carbohydrate inputs. At the
30-minute horizon the reported prediction accuracy is similar across models,
while the proposed model produces no unsafe recommendations under the paper’s
physiology-based test compared with up to 64.3% for baselines. The IEEE full
text could not be retrieved in this pass, so detailed protocol and split
mechanics remain unverified.

This paper does not establish event-instance graph novelty. It does strengthen
the requirement to evaluate predictive accuracy separately from physiological
or explanation faithfulness; a plausible graph path or good score alone is
not evidence that an explanation is safe, faithful, or useful.

Sources: [PubMed abstract and DOI](https://pubmed.ncbi.nlm.nih.gov/42685163/),
[IEEE record](https://ieeexplore.ieee.org/abstract/document/11675927/).

## Novelty conclusion after this search

Broad claims are ruled out: temporal graphs for hypoglycemia, clinical-event
nodes linked to time-indexed visits, graph explanations, multimodal meal/insulin
forecasting, event-aware sequence representations, postprandial event
prediction, temporal event visualization, physiological/counterfactual
faithfulness testing, time-series explanation evaluation, patient-level
CGM-only event prediction, and post-event cause interpretation each have prior
art. The remaining defensible candidate is an
implementation- and endpoint-specific empirical question: whether raw,
timestamped insulin/meal event-instance relations
improve incident-within-horizon hypoglycemia prediction beyond models given
the same observed event values, occurrence times, availability cutoff,
prediction windows, participant split, and comparable optimized capacity.
This candidate is **provisional**, not a certified “first” claim. Targeted
search did not identify an exact matched event-instance-relation comparison,
but that is not proof of absence. Current project results have not established
predictive benefit from graph relations; aligned pooling has outperformed the
tested graph branch in the completed two-seed, five-fold development
comparison. Negative or null results therefore remain central evidence, not
an inconvenience to be optimized away.

Before manuscript submission, run a reproducible database search with saved
query syntax and date, screen candidate records and citation trails, and
revisit the full GAT-BiGRU article when its PMC embargo ends (18 June 2027).
Do not claim field-wide novelty unless that broader search supports it.


## Update: additional event-graph and T1D event-context precedents — 31 October 2026

A final targeted pass checked the direct event-time graph and contextual-input
leads in primary sources. This expands the curated matrix to 62 unique records
after correcting the 2019 postprandial-paper author key from Kim to Seo. It
remains a targeted, non-systematic review.

| Source | Primary-source finding | Novelty consequence and boundary |
|---|---|---|
| Zecchin et al. (2016), [proof-of-concept study](https://pmc.ncbi.nlm.nih.gov/articles/PMC5032963/) | In 15 people with T1D, compares CGM-only with CGM+insulin, CGM+carbohydrate, and both for glucose regression. It reports improved accuracy in the two hours after meals for horizons of at least 30 minutes, with carbohydrate contributing more than insulin at longer horizons. | Direct evidence that adding treatment/meal information to CGM has long been tested. Its continuous glucose-regression endpoint, small within-person chronological evaluation, and lack of event-graph comparison differ from this study. It rules out novelty based on contextual input inclusion alone. |
| Li, Ge & Chen (2020), [PVLDB](https://www.vldb.org/pvldb/vol13/p1779-li.pdf) | Represents event-time order as typed relations in a dynamic knowledge graph with stream-state nodes. The diabetes AIM-94 logs include timestamped insulin, glucose, hypoglycemic symptoms, meals, and exercise. The reported precision/recall prediction figures are for mobile-system and oil-well tasks; diabetes data are used for event discovery and graph/training analysis, and no hypoglycemia-risk metrics are reported for that cohort. | Direct precedent for event-time knowledge graphs and a diabetes-stream application. Do not describe it as demonstrated diabetes hypoglycemia prediction. It nevertheless rules out a claim that event-order KG construction itself is new. |
| Apicella et al. (2026), [arXiv preprint](https://arxiv.org/abs/2609.08772) | Uses OhioT1DM to compare prompt-based LLM representations and context levels for postprandial hypo-/hyperglycemia prediction at 30/60/90 minutes. The authors report that more contextual insulin/meal/carbohydrate/activity information does not systematically improve prediction. | Strongly reinforces that representation and context require controlled testing. It is a preprint and patient-specific LLM prompting study, not event-instance graph learning or the proposed patient-disjoint matched relation comparison. |
| Voegeli et al. (2025 workshop), [arXiv record](https://arxiv.org/abs/2504.09299) | Predicts nocturnal hypoglycemia in 16 children using wearable physiology and transfer learning. | Adjacent evidence for non-CGM physiological context; not treatment event relations, a graph, or a large-cohort external validation. Abstract-level detail only. |
| Oviedo et al. (2019), [PubMed record](https://pubmed.ncbi.nlm.nih.gov/31416546/) | Personalized postprandial hypoglycemia prediction and simulated bolus reduction using retrospective data from 10 people with T1D on multiple daily injections. | Confirms patient-specific meal/insulin-triggered hypoglycemia modeling predates this project; not a rolling patient-disjoint event-relation benchmark. Full text was not inspected in this pass. |
| Dave et al. (2021), [JMIR Diabetes full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC8120423/) | Separately from Dave et al. (2021) feature-context paper, this study predicts sustained low events at 30/60 minutes from CGM history in 110 pediatric participants, with repeated patient-based 65/35 and chronological 70/30 validation. | Establishes a large CGM-only sustained-event baseline precedent and underscores patient-held-out evaluation. It does not use treatment-event instances as model inputs and its sustained endpoint differs from the current any-low-within-horizon target. |

The combined evidence narrows the claim further: no novelty should be assigned
to temporal event-order KGs, the use of diabetes event streams in graph
research, adding insulin/meal context, patient-specific postprandial risk, or
context/representation comparisons in general. The remaining candidate is the
result of a specific, auditable comparison of timestamped insulin/meal event
instances and relation structure against same-information, same-timing,
capacity-matched non-graph controls for the prespecified Loop incident-low
endpoint. The review has not established that no equivalent comparison exists.

## PubMed-indexed follow-up results — 31 October 2026

A PubMed-focused search pass also surfaced two records requiring explicit
screening. The query route available in this environment returned indexed
PubMed records through web search; it did **not** produce a native PubMed
search export or reproducible database hit count. Therefore these are search
leads and primary-record checks, not a PRISMA search flow.

| Source | Verified from PubMed record/abstract | Scope effect |
|---|---|---|
| Quader et al. (2026), [systematic review and meta-analysis](https://pubmed.ncbi.nlm.nih.gov/41424951/) | The review reports a PRISMA-guided search, 611 records screened and 20 included, with pooled sensitivity and specificity estimates. It concludes that contextual inputs such as insulin, carbohydrates and activity have been used and may improve prediction. | Confirms contextual inputs are a well-established prediction direction. Its 611/20 flow belongs to that review and must not be represented as our search counts; it does not identify the event-instance graph comparison. Obtain its supplements/full methods and included-study list for citation chaining. |
| Ferstad et al. (2024), [week-ahead CGM hypoglycemia model](https://pubmed.ncbi.nlm.nih.gov/38445628/) | Uses three T1D cohorts (REPLACE-BG, JDRF, Tidepool) and validates across cohorts for next-week clinically significant low risk from a week of CGM. | Establishes large multi-cohort/external-validation work for patient-level risk. Its weekly <54 mg/dL sustained-event target and CGM-only inputs differ substantially from rolling 30-minute event-instance modeling. |
| Tziavaras et al. (2026), [attention-LSTM nocturnal risk model](https://pubmed.ncbi.nlm.nih.gov/42224311/) | The abstract describes 24-hour CGM, meal and insulin inputs, OhioT1DM development and SMARTDIAB external evaluation, up to 12-hour nocturnal risk, scheduled basal insulin, and attention mapped back to the original inputs. | Rules out broad novelty for interpreting temporal, multimodal CGM/meal/insulin inputs in a T1D hypoglycemia predictor. It is a long-horizon nocturnal physiologically informed LSTM, not an event-instance KG or same-information graph-relation test. Full article methods remain to be inspected. |

The curated matrix now contains 64 unique records. The literature synthesis is
still a targeted evidence review, **not a completed systematic review**: no
native PubMed/Scopus/Web of Science exports, query-level yield table for our
search, deduplicated PRISMA flow, or independent second reviewer screening is
available. The new systematic review's own flow does not repair those gaps.

## Citation-chain check: diabetic event-instance causal graphs — 31 October 2026

A backward-citation and exact-title check identified two further direct
representation precedents. Their implications materially narrow what can be
called novel.

| Source | Verified from primary source | Consequence for the claim |
|---|---|---|
| Acharya & Lee (2014), [Incremental causal network construction over event streams](https://doi.org/10.1016/j.ins.2013.09.022) | Full paper describes timestamped event instances grouped by event type and patient/event-owner attributes, temporal precedence, causal links, and a virtual instance layer. Its diabetic monitoring example includes insulin doses, glucose decreases/increases, meal events, and hypoglycemic symptoms; a physician-vetted diabetic event dataset is used to evaluate causal-network reconstruction. | This rules out novelty for event-instance relations, temporal/causal graphs of diabetic clinical events, or graphing insulin/glucose/hypoglycemia relations in the abstract. The task is causal-network structure recovery, not future CGM risk prediction; it does not test the matched predictive comparison here. |
| Postiglione et al. (2024), [MedTKG](https://discovery.ucl.ac.uk/id/eprint/10191256/) | Accepted manuscript describes temporal knowledge-graph snapshots of patient histories integrated with medical ontologies and future-disorder prediction on MIMIC-III clinical notes. | Temporal patient KGs for clinical outcome prediction are prior work. Its hospital disorder-link-prediction task differs from outpatient T1D event-instance risk prediction. |

With Acharya & Lee and Li et al. included, event-time/instance relation
construction is clearly prior art, including in diabetes streams. The project
must **not** claim a new event-relation or temporal diabetic graph
representation. The remaining candidate is an empirical benchmark result:
what the already-known event-instance relation family adds, if anything, over
information-, timing-, and capacity-matched controls for this Loop endpoint
and split. Current results favor the non-graph pooling comparator. A claim to
novelty for this exact benchmark still requires native database searches and
citation chaining; the present search has not established absence.

## Further citation-chain screen: contextual hypoglycemia prediction

The reference list of Quader et al.'s 2026 systematic review and meta-analysis
was checked as a backward-citation source. Its report of 611 screened and 20
included studies is that review's PRISMA flow, not this project's search yield.
Three cited primary studies were checked because they directly test contextual
inputs or time-localized risk:

| Source | What the primary record supports | Relevance boundary |
|---|---|---|
| Bertachi et al. (2020), [Sensors full text](https://www.mdpi.com/1424-8220/20/6/1705) | Ten adults with T1D used CGM, manually timestamped insulin and meal entries, and a Fitbit over 12 weeks. The study evaluated nocturnal prediction models using CGM/therapy and physical-activity information. A follow-up study describes instance-pool 80/20 evaluation, but does not establish participant-disjoint testing. | Timestamped multimodal context and nocturnal risk prediction predate this work. The small, high-risk MDI cohort, nocturnal endpoint, and lack of a graph-versus-matched-control relation test distinguish it. |
| Cichosz et al. (2015), [PubMed/PMC full text](https://pubmed.ncbi.nlm.nih.gov/25216731/) | In 21 adults and only 12 hypoglycemic events, the authors compare CGM, derived CGM features, and CGM plus heart-rate variability for 20-minute prediction; the abstract reports ROC AUC 0.96 for CGM+HRV versus 0.92 for derived CGM at 100% sensitivity. | Direct incremental-context comparison is established, but the small event count and physiological HRV modality differ from insulin/meal transactions and event relations. |
| Mosquera-Lopez et al. (2023), [PubMed abstract](https://pubmed.ncbi.nlm.nih.gov/36803791/) | Mixed-effects logistic regression and random forest use glucose, insulin exposure, prior glycemic risk and physical-activity data around activity; training/validation use 50 Tidepool participants and the best model is assessed on a separate 20-person T1DEXI pilot set. | Explainable activity-anchored risk prediction with an independent cohort is prior work. It is not a rolling CGM incident-low task or an event-instance graph comparison. |

These checks further rule out broad novelty for contextual data integration,
incremental multimodal hypoglycemia prediction, or explainable patient risk
modeling. They do not answer whether event-instance graph relations improve
the current endpoint over matched non-graph event representations. The
curated matrix now contains 69 unique records; this count is not a database
search yield. The review remains targeted, with no native database exports or
completed PRISMA flow.

## Additional primary-source check: prior-guided asynchronous attention

Yu et al. (2024) propose a multiscale feature-mining and prior-knowledge-guided
dynamic-attention framework for nocturnal hypoglycemia early warning in T1D.
The full text describes OhioT1DM data containing CGM, insulin, physiological
sensors, and self-reported life events. OhioT1DM is partitioned into roughly
40 training days and 10 test days per participant; the analysis retains 10
participant datasets. This supports prior art for asynchronously sampled,
multimodal T1D warning models and clinically guided attention. It does not
establish held-out-patient generalization and is not a patient event-relation
KG or a matched graph-versus-non-graph relation comparison.
[Primary full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC11653906/),
[PubMed](https://pubmed.ncbi.nlm.nih.gov/39696373/),
[DOI](https://doi.org/10.1186/s12911-024-02761-3).

After this check, the curated matrix contains 70 unique records. The added
paper further removes broad claims for multimodal temporal feature fusion or
prior-knowledge-guided attention as novel. It does not change the remaining
candidate: a rigorously controlled empirical test of the predictive value of
event-instance relations under matched information, timing, and model capacity.
