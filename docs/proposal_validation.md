# Proposal validation

Reviewed: 10 September 2026. Scope: initial critical review of the 69-section startup handbook, targeted literature checks, dataset access, and experimental design. This is not a systematic review or a completed feasibility study.

## Subsequent novelty review

The [expanded novelty assessment](novelty_assessment.md) adds earlier graph models and a 2026 physiology-graph manuscript, verifies the semantic study's January 2025 proceedings publication, and revises the contribution to a controlled event-representation study. The [refined proposal](refined_proposal.md) supersedes the tentative novelty recommendation below. Actual availability timestamps remain unverified, so delay studies are conditional or explicitly simulated.

## Assessment

Proceed with protocol development and a data audit. The research question is defensible, but neither novelty nor improved prediction has been established. A patient-centric semantic graph, temporal representation, and explainability are each already represented in prior work. The contribution must be a precisely specified method and a controlled evaluation of the value of its relations.

Recommended framing:

> Under matched information and patient-disjoint evaluation, do explicit clinical event relations and their timing improve incident CGM-defined hypoglycemia prediction, calibration, and explanation fidelity beyond strong sequence and graph comparators?

Do not promise a new state of the art, publication, clinical benefit, or superiority before experiments. An inconclusive or negative result should remain reportable under the same protocol.

## Evidence checks

| Handbook claim | Assessment | Consequence |
|---|---|---|
| Sarwar et al. 2026 is close prior work | Verified at abstract level: temporal neighborhood graph, GAT-BiGRU, 30/60-minute tasks, OhioT1DM and BrisT1D, GNNExplainer. Full methods and supplements were not reviewed. [PubMed](https://pubmed.ncbi.nlm.nih.gov/42314749/) | Include as a comparator family. Its reported scores are not directly comparable until endpoint, preprocessing and split are matched. |
| A semantic patient graph supplies the novelty | Incomplete: Daniel Onwuchekwa et al. explicitly proposed patient-specific KGs, embeddings and temporal ontology for T1D hypoglycemia. The ESWC 2024 PhD Symposium paper reports preliminary work, not a definitive matched CGM benchmark. [Conference paper, sections 4–7](https://2024.eswc-conferences.org/wp-content/uploads/2024/05/77770363.pdf) | Add to the closest-prior-work set. A narrow temporal method and stronger evaluation may distinguish this project; generic semantic integration does not. |
| Rad et al. supports patient-centric KG design | Verified: the paper describes PHKGs, FHIR-aligned representation, and diabetes prediction applications. This is conceptual/methodological overlap, not proof of this proposal's incremental benefit. [Publisher](https://www.mdpi.com/2075-4426/14/4/359) | Explain exactly which relations and evaluation elements are new. |
| OhioT1DM has 12 participants and roughly eight weeks each | Verified in the dataset paper. It has separate development/training and testing XML files and includes wearable and reported event data. [Author-hosted paper](https://webpages.charlotte.edu/rbunescu/data/ohiot1dm/bglp/OhioT1DM-dataset-paper.pdf) | Distinguish participant count from thousands of correlated windows; audit actual modality and event availability. |
| OhioT1DM can be obtained through a DUA | The custodian page directs researchers to complete a DUA and email the signed form to the coordinator. The researcher subsequently reported that the DUA requires the requester to be a current institutional employee and requires a supervising advisor to submit for a student. [Access instructions](https://webpages.charlotte.edu/rbunescu/ohiot1dm.html) | Direct application is unavailable to this researcher. Retain only an eligible advisor-mediated route and apply the [dataset fallback strategy](dataset_fallback_strategy.md). No DUA has been signed or email sent in this review. |
| T1DEXI has 497 adults | Verified for the published analysis cohort, not guaranteed as the count in an accessible, usable release. [Study abstract](https://repository.lsu.edu/clinical_research_pubs/218/) | Record enrolled, released, eligible and analyzed counts separately. |
| T1DEXI is a ready external dataset | Conditional: the Jaeb directory links adult T1DEXI to DOI 10.25934/PR00008428, which resolves to Vivli. Release documentation and access terms were not readable in the retrieved landing page. [Jaeb directory](https://public.jaeb.org/datasets/diabetes), [study record](https://doi.org/10.25934/PR00008428) | Start access and dictionary verification early. Do not assume a direct download or complete insulin/meal coverage. |
| D1NAMO has 29 participants, 9 with T1D | Supported by the dataset publication record. [Record](https://zenodo.org/records/5651217) | Optional modality study; audit label coverage before selecting it. |
| BrisT1D is suitable for within-horizon hypoglycemia | Not established from the material checked; the processing repository exists. [Repository](https://github.com/SamAJames/brist1d_processing) | A single future glucose target at +60 minutes cannot identify every low within the preceding hour. Require actual intervening trajectories and chronology before use. |
| CGM <70 mg/dL is “Level 1” | Incorrect shorthand. Level 1 is 54 to <70; <54 is Level 2. Level 3 requires clinical information about assistance and cannot be inferred from CGM alone. [ADA 2026](https://diabetesjournals.org/care/article/49/Supplement_1/S132/163927/6-Glycemic-Goals-Hypoglycemia-and-Hyperglycemic) | Name the primary target “CGM-defined hypoglycemia <70 mg/dL,” including Level 2 values. |
| LOINC 97510-2 can represent a CGM reading | It represents a proportion of glucose measurements in range, not an individual glucose concentration. [LOINC record](https://loinc.org/97510-2) | Use only for a correctly defined aggregate. Individual-reading mapping needs its own terminology review. |

The [Siegen dissertation](https://dspace-backend.ub.uni-siegen.de/server/api/core/bitstreams/1e658634-a368-49e9-93b2-4491e750edb8/content) contains the semantic hypoglycemia work and additional temporal/personalization chapters. Only relevant passages were inspected; a full dissertation review and forward-citation search remain necessary. Do not count the dissertation and its embedded conference paper as independent evidence.

## Required methodological changes

These are review recommendations and design judgments, not findings demonstrated by the sources above.

1. **Forecast onset separately from persistence.** The original label includes patients already below 70 at prediction time. A model can score well by recognizing an ongoing low. Define eligible prediction times using only current/past CGM; retain the original all-state task as a secondary comparison.
2. **Represent unobservable labels explicitly.** “No observed low” is not a valid negative when the future is missing. Do not interpolate labels or use an unqualified `else 0`. Specify coverage for positive and negative samples consistently.
3. **Separate outcome storage from model inputs.** The proposed `HypoglycemiaEvent`, `precedes` edges to future lows, and `PredictionWindow.label` must never be traversable or encoded by the input graph. Historical episodes also need as-of-time completion rules; v1 excludes episode nodes entirely.
4. **Use availability time as well as occurrence time.** An exercise end time, completed-session heart-rate average, or meal entered retrospectively might not have been known at the prediction index. If availability time is absent, report this as an assumption and perform delayed-entry sensitivity analysis.
5. **Control patient-node leakage.** A patient node shared across a full timeline can expose future events through message passing. Build independent, as-of-time window graphs. Fit learned graph representations within each training fold.
6. **Treat “semantics” ablation cautiously.** Collapsing relation types changes capacity, and source/target node types can reveal relations anyway. Add capacity controls, document redundant relation types, and compare temporal-only topology, generic relations, and an event-sequence comparator. A stable renaming of relation IDs is not an ablation.
7. **Separate zero-shot transfer and adaptation.** A learned patient ID cannot represent a new patient meaningfully. Any adaptation must use an explicitly earlier block, with labels available before the adaptation cutoff and later evaluation data kept separate.
8. **Specify alert behavior.** Thresholds, suppression, episode matching, observable follow-up, and false alerts per monitored day need definitions. Window-level recall does not measure episode detection.
9. **Strengthen uncertainty analysis.** Resample participants, retaining their windows together, rather than treating windows as independent trials. Twelve participants can leave large uncertainty even with many observations. Bootstrap intervals on fixed out-of-fold predictions do not capture every training uncertainty.
10. **Evaluate explanations as model evidence.** A plausible graph path is not automatically faithful or causal. Compare deletion and retention against matched random masks, track invalid graph perturbations, and evaluate stability. Clinical review assesses plausibility/usability, not predictive effectiveness.
11. **Reconcile historical support.** A 120-minute sequence contains 24 samples only with an explicit half-open interval. Insulin action or exercise history may extend beyond that interval. Give every model identical extra historical summaries if introduced; do not assume a two-hour bolus sum is measured insulin-on-board.
12. **Make schema mappings accurate.** Pin a FHIR release rather than mixing R4 and unversioned resources. In PROV-O, a processing activity generates an entity and a device can be an agent; a simple device-to-`wasGeneratedBy` example needs type correction. [FHIR R5 NutritionIntake](https://hl7.org/fhir/R5/nutritionintake.html), [PROV-O](https://www.w3.org/TR/prov-o/).

## Novelty decision

The best current candidate is an availability-aware, typed temporal event model with a controlled demonstration of relational value and faithful evidence extraction. This is a proposed distinction, not an established gap. First compare the detailed schema, time encoding, readout, task, splits, and explanations against the three closest works above and relevant follow-ups.

If clinical relations are fully determined by node types and time, describe the gain as relational inductive bias rather than new patient information. Demonstrating an interoperable schema additionally requires mapping validation and meaningful queries, not only a list of FHIR names.

## Search coverage and outstanding evidence

Targeted web searches on 10 September 2026 included:

```text
"type 1 diabetes" "knowledge graph" hypoglycemia prediction
"Enhancing Hypoglycemia Prediction" "Semantic"
"hypoglycemia" "knowledge graph" "temporal"
"type 1 diabetes" "heterogeneous graph" prediction
```

The review also opened the handbook's main clinical, dataset, and closest-method references. Some PMC pages returned access challenges; publisher, PubMed or author-hosted sources were used where available. No Scopus/Web of Science export, exhaustive screening, full bibliography verification, dataset audit, or reproduction has been completed. Remaining handbook references should not be treated as fully validated merely because they appear there.

Next evidence work: record reproducible database queries and dates; screen abstracts and full texts; follow citations in both directions; inspect GAT-BiGRU supplements/code and semantic-KG follow-ups; add recent strong non-graph models; record exclusions and evidence level. Reassess novelty before freezing the architecture.
