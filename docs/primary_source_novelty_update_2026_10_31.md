# Targeted primary-source novelty update (31 October 2026)

## Scope and search record

This is a focused addendum to the [31 October primary-source novelty check](primary_source_novelty_check_2026_10_31.md), not a systematic review. The target claim was narrowed to: *whether timestamped clinical event-instance relations in a temporal graph improve short-horizon hypoglycemia prediction over non-graph controls with the same input records, information cutoff, temporal alignment, prediction windows, and comparable capacity, in T1D.*

Searches run on 31 October 2026 included:

- `2026 hypoglycemia forecasting Loop Study MT-HypoNet temporal graph event instance graph T1D`
- `site:pmc.ncbi.nlm.nih.gov T1D hypoglycemia graph event nodes relations CGM prediction 2025 2026`
- `site:academic.oup.com/jamia 2026 hypoglycemia temporal graph insulin meal event nodes`
- `"same information" graph neural network clinical time series hypoglycemia`
- Exact-title checks for `"Subject-Independent Hypoglycemia Warnings via Multi-Horizon Transformers and Causal Hysteresis"` against official PMLR/OpenReview records.

I followed promising records to the original open-access article or publisher/proceedings record when available. Search coverage and access were limited; absence from these results is not proof of absence.

## Newly verified close comparator: MT-HypoNet (iScience, 2026)

Fang et al. report MT-HypoNet, a multitask model for BG forecasts and 30-minute hypoglycemia forewarning. The study includes seven retrospective public datasets (1,662 participants total); Loop is the largest source and contains 844 participants. Their Loop evaluation is inter-patient five-fold cross-validation, and they also report applying the Loop-trained model to external datasets without fine-tuning. Its input window is two hours, sampled onto a five-minute sequence; it predicts future BG at 5–30 minute steps and hypoglycemia risk in the next 30 minutes. The article defines a hypoglycemia event as three consecutive CGM readings below 70 mg/dL and additionally evaluates a soft-label risk strategy near the threshold. These endpoint details differ from this project's binary label of any future reading below 70 mg/dL in its horizon. [Open-access full article and methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC13019577/) · [Publisher record](https://doi.org/10.1016/j.isci.2026.115294)

The paper's method description says insulin delivery, carbohydrate intake, and time-of-day can be aligned to the CGM grid, with events assigned to the nearest timestamp and empty time points set to zero. The architecture description calls carbohydrate, basal insulin, bolus insulin, and time-of-day optional inputs. Because this wording does not identify clearly which optional channels were enabled in each principal experiment, this review does **not** assert that the reported headline model used all of them. The article reports a 71,426-parameter encoder / bidirectional-LSTM / decoder model and ablations for multitask versus single-task learning and augmentation. These comparisons address task formulation and training, not graph relations versus a same-information, same-timing, capacity-matched non-graph model. [Methods, preprocessing, and ablation sections](https://pmc.ncbi.nlm.nih.gov/articles/PMC13019577/)

**Verified implication:** the project cannot claim to be the first Loop-trained short-horizon hypoglycemia forewarning model, first Loop inter-patient validation, or first model to combine BG prediction and near-term hypo risk. MT-HypoNet establishes all of those broader ingredients. Its distinct endpoint, architecture, and unresolved optional-channel configuration leave the specific event-relation comparison open in this source; that is a bounded reading of this paper, not a field-wide novelty proof.

## Other relevant 2025–2026 evidence

- **GAT-BiGRU (JAMIA, 2026).** The PubMed/OUP abstract describes a temporal k-neighborhood graph whose nodes are feature-enriched CGM time points, with graph attention and BiGRU for 30- and 60-minute hypoglycemia risk, evaluated on OhioT1DM and BrisT1D. The OUP supplementary DOCX was retrieved and inspected. It specifies directed past-to-present k=10 edges and 23 node features, but its split table leaves Ohio test participant separation unclear; the BrisT1D test is described as 15 unseen patients. The PMC page says the article body will be released 18 June 2027. Therefore details beyond the abstract/supplement, including exact Ohio participant split, label construction, and matched-control design, remain **unverified**, not absent. This rules out broad claims to be first in temporal graph-based hypoglycemia prediction or graph explanation. [OUP article and supplementary data](https://academic.oup.com/jamia/article-abstract/33/9/1713/8711207#supplementary-data) · [PubMed record](https://pubmed.ncbi.nlm.nih.gov/42314749/) · [PMC release record](https://pmc.ncbi.nlm.nih.gov/articles/PMC13580734/)
- **DA-CMTL (npj Digital Medicine, 2025).** This work jointly forecasts glucose and classifies hypoglycemia, with simulation-to-real transfer and public-dataset evaluation including DiaTrend, OhioT1DM, and ShanghaiT1DM. It reinforces that multitask hypoglycemia modeling and transfer evaluation are established. The reported study is not an event-instance graph relation experiment. [Publisher article](https://www.nature.com/articles/s41746-025-01994-4)
- **ESWC 2024 semantic KG proposal.** The official proceedings paper explicitly proposes patient-specific, evidence-based KGs and semantic integration for T1D hypoglycemia; it describes the work as early-stage, with real-world validation and generalizability as future work. It rules out novelty of the broad patient-specific KG framing, but does not report the completed matched predictive comparison in this project's narrowed question. [Official proceedings PDF](https://2024.eswc-conferences.org/wp-content/uploads/2024/05/77770363.pdf)

An exact-title search also returned an anonymous OpenReview PDF headed “Proceedings of Machine Learning Research LEAVE UNSET” and “Anonymous Author,” with placeholder affiliation/email, claiming CHIL 2026 publication. No corresponding completed official proceedings record was verified in the searches above. I therefore do **not** treat this document as established prior art or rely on its results. This exclusion is about source verification, not a conclusion that the work is fabricated.

## Bounded novelty conclusion

The most defensible candidate contribution remains an **empirical, implementation-specific test**: whether explicitly typed temporal relations from recorded insulin/meal/basal event instances help short-horizon T1D hypoglycemia prediction when a non-graph comparator receives the same event instances, timestamps, availability cutoff, history, windows, splits, and comparable optimized capacity. The literature checked here establishes semantic KGs for the broad T1D/hypoglycemia framing, glucose-timepoint graphs for hypo risk, and strong non-graph Loop-based 30-minute forecasting/forewarning. It does not verify a prior study that performs this exact controlled event-instance relation test.

That last sentence is an **inference from a targeted search**, not a proven universal negative. Do not write “first” without a reproducible database search and full-text review of the closest records; the GAT-BiGRU supplement is reviewed, but its main article body remains embargoed. Also keep novelty separate from evidence of benefit: this project's own stricter comparison has favored aligned pooling over its tested graph branch, so the current data do not support claiming that the graph relations improve prediction. The appropriate scientific question remains whether and under what controlled conditions such relations add value.


## Additional primary-source check: event-time knowledge graphs and T1D contextual prediction

**Zecchin et al. (2016).** The full primary PMC paper compares four configurations
(CGM; CGM+insulin; CGM+carbohydrate; all three) in 15 people with T1D. It
reports that insulin and carbohydrate information improve short-term glucose
prediction during the two hours after meals for prediction horizons of at
least 30 minutes, with carbohydrate more influential than insulin for longer
horizons. This is continuous glucose regression and a small within-participant
chronological setup, not incident-low prediction in held-out patients or an
event-instance graph comparison. [Primary full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC5032963/).

**Li, Ge & Chen (2020).** The PVLDB paper explicitly models event order as
relationship types in a dynamic knowledge graph and includes AIM-94 diabetes
logs with insulin doses, glucose, hypoglycemic symptoms, meals and exercise.
The paper reports prediction performance on mobile and oil-well streams; its
diabetes section shows event discovery/graph learning analyses but no
hypoglycemia prediction metrics for that cohort. This is direct graph-method
prior art, but not a diabetes predictor result. [Primary PVLDB paper](https://www.vldb.org/pvldb/vol13/p1779-li.pdf).

**Apicella et al. (2026).** The arXiv preprint evaluates OhioT1DM
postprandial hypo-/hyperglycemia prediction at 30/60/90 minutes across LLM
input representations and context levels. Its abstract reports no systematic
benefit from adding contextual insulin, meal, carbohydrate and activity
information. Its task/model and patient-specific setup differ from our
patient-disjoint learned event-relation comparison. [Primary preprint](https://arxiv.org/abs/2609.08772).

**Other close event-context studies.** Zecchin et al. are distinct from Dave et
al.'s engineered IOB/COB comparison: Zecchin directly ablates CGM, insulin and
meal-carbohydrate inputs for glucose regression. The 2019 Oviedo CMPB paper
adds an older personalized postprandial prediction precedent (10 participants;
abstract/bibliographic evidence inspected). Dave et al.'s separate 2021
sustained-event model uses 110 pediatric participants and patient-based plus
chronological validation, but is CGM-feature-based. Voegeli et al.'s 2025
workshop abstract uses wearable physiology in 16 children. These sources
further weaken broad novelty for contextual prediction while leaving the exact
matched event-instance relation comparison unresolved. [Oviedo PubMed](https://pubmed.ncbi.nlm.nih.gov/31416546/), [Dave full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC8120423/), [Voegeli arXiv](https://arxiv.org/abs/2504.09299).

## PubMed-indexed follow-up: recent synthesis and close T1D multimodal comparator

**Quader et al. (2026).** The PubMed record reports a PRISMA-guided systematic
review/meta-analysis that screened 611 records and included 20 T1D
CGM-based hypoglycemia prediction studies. It synthesizes diagnostic
performance and notes use of insulin, carbohydrate, and activity inputs. These
are counts for Quader et al.'s review, not the present project search. The
review does not settle the event-instance graph versus matched non-graph
question; its supplements and included-study list should be used for citation
chaining in a future formal review. [PubMed record](https://pubmed.ncbi.nlm.nih.gov/41424951/), [DOI](https://doi.org/10.1007/s40200-025-01820-4).

**Tziavaras et al. (2026).** The PubMed abstract describes an attention-LSTM
model for up to 12-hour nocturnal hypoglycemia risk, developed on OhioT1DM and
externally evaluated on SMARTDIAB. The abstract says its 24-hour inputs include
CGM, meals, and insulin and that attention is mapped back to these inputs;
it also mentions scheduled basal insulin and a physiological model. This
establishes multimodal temporal prediction and input-level interpretability
as prior work. It is not an event-instance KG or an information-/capacity-
matched relation experiment. Full-text methods and data splits still need
independent inspection. [PubMed record](https://pubmed.ncbi.nlm.nih.gov/42224311/), [DOI](https://doi.org/10.1109/TBME.2026.3698300).

**Ferstad et al. (2024).** A three-cohort CGM-only model predicts next-week
clinically significant hypoglycemia and reports external validation across
REPLACE-BG, JDRF, and Tidepool. This is a useful large-cohort risk-prediction
precedent but differs in time scale and endpoint; it is not event-aware.
[PubMed record](https://pubmed.ncbi.nlm.nih.gov/38445628/), [DOI](https://doi.org/10.1177/19322968241236208).

## Citation-chain result: a 2014 diabetic event-instance causal network

Acharya and Lee's 2014 primary paper is a close representation precedent. It
models timestamped event instances in diabetic monitoring streams, groups
them into event types, links event instances through shared patient/event-owner
attributes, and uses temporal precedence and causal relations. Its running
example includes insulin administration, falling/rising glucose, meals, and
hypoglycemic symptoms; its real-data evaluation reconstructs a physician-
vetted causal network. This predates the current project by more than a decade
and means neither event-instance relations nor temporally ordered diabetic
event graphs are novel by themselves. The paper does not train a future-CGM
risk classifier or perform an information/timing/capacity-matched predictive
ablation. [Full paper](https://bslee.w3.uvm.edu/papers/ICNC_published.pdf),
[DOI](https://doi.org/10.1016/j.ins.2013.09.022).

Postiglione et al.'s 2024 MedTKG paper similarly establishes temporal patient
KGs integrated with medical ontologies for future-disorder prediction from
MIMIC-III clinical notes. It is not a T1D CGM event-forecast benchmark.
[Institutional accepted manuscript](https://discovery.ucl.ac.uk/id/eprint/10191256/).

## Backward citation check: three T1D contextual predictors

Quader et al.'s publisher-hosted 2026 review was used as a backward-citation
source. Its 611-screened/20-included flow belongs to that review and is not a
search count for this project.

**Bertachi et al. (2020).** Ten adults with T1D used CGM and a Fitbit for 12
weeks, with manually entered timestamped insulin doses and carbohydrate intake.
The study evaluates nocturnal prediction using the collected glucose,
therapy, and activity/sleep data. A follow-up paper describes an 80/20 split
of pooled instances; the inspected text does not establish participant-level
disjointness. This is a direct precedent for multimodal, time-stamped context
in hypoglycemia prediction, though it is small, nocturnal, and not graph based.
[Full paper](https://www.mdpi.com/1424-8220/20/6/1705).

**Cichosz et al. (2015).** In 21 adults with T1D, the paper compares raw CGM,
derived CGM features, and derived CGM plus heart-rate variability for
20-minute spontaneous hypoglycemia prediction. The abstract reports 12 low
events and 237 euglycemic measurements; at 100% sensitivity the reported
specificity rises from 71% for derived CGM to 91% for CGM+HRV. This shows that
incremental-context comparisons predate this project, but the event count is
small and HRV is not insulin/meal transaction data.
[PubMed with full-text link](https://pubmed.ncbi.nlm.nih.gov/25216731/).

**Mosquera-Lopez et al. (2023).** The study models hypoglycemia during and up
to 24 hours after physical activity using glucose, insulin-dose/exposure and
activity information. It trains/validates on 50 Tidepool participants and
reports an independent T1DEXI pilot test set of 20 participants. It establishes
activity-anchored explainable multimodal risk prediction and external pilot
testing, but is not a rolling incident-low task or event-instance graph test.
[PubMed abstract](https://pubmed.ncbi.nlm.nih.gov/36803791/).

## Additional close model: prior-guided asynchronous attention

Yu et al. (2024) present a multiscale feature-mining and prior-knowledge-guided
dynamic-attention method for nocturnal hypoglycemia warnings in T1D. Their
OhioT1DM inputs include CGM, insulin, physiological sensors and self-reported
life events. They analyze 10 patient datasets after excluding insufficient
records, using the original temporal training/test periods (about 40 versus 10
days) rather than a held-out-patient split. The abstract reports a 94.91%
warning rate and F1 of 96.35%; these numbers should not be directly compared
to our endpoint or participant-level metrics. This paper establishes prior
art for asynchronous multimodal feature fusion and clinically guided temporal
attention, but not event-instance KGs or a matched relation ablation.
[Primary full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC11653906/),
[PubMed](https://pubmed.ncbi.nlm.nih.gov/39696373/).
