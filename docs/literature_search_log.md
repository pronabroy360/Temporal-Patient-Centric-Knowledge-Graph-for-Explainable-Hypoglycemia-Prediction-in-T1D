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

## Inclusion and exclusion decisions

Include direct T1D hypoglycemia KGs/GNNs; graph-based glucose forecasts that overlap in representation; patient-centric diabetes KGs; and adjacent temporal/missingness methods that constrain algorithmic novelty. Include preliminary work, but distinguish it from validated systems. Do not use a conference date, online publication date and dissertation year to count the same study multiple times.

Exclude molecular/drug-target KGs, generic nutritional recommenders, unrelated T2D comorbidity graphs, product pages and patents from the core predictive comparator set. These are not evidence about our exact outpatient CGM prediction task. Do not conclude they are irrelevant to every possible future extension.

Author-uploaded SysCon manuscript: included as primary author content; final IEEE version was not retrieved. Dynamic Partitioning of Graphs: publisher-indexed abstract inspected, direct full-text retrieval failed; retain as an adjacent record rather than assert detailed methods. GlucoNet-MM and some handbook sequence references remain leads requiring full extraction.

## Version and access ledger

- Semantic study: public ESWC 2024 manuscript plus Springer chapter published 28 January 2025, DOI 10.1007/978-3-031-78955-7_4. Final chapter methods were not accessible; do not assume perfect identity with the conference manuscript.
- Visibility-graph study: S+SSPR 2024, chapter online 31 January 2025, DOI 10.1007/978-3-031-80507-3_6; author repository and related thesis available. The final chapter full text was not retrieved.
- GAT-BiGRU: publisher full-text attempt redirected to the abstract. No supplements or exact implementation were obtained. Primary abstract verified through PubMed.
- SysCon graph paper: author manuscript visible on ResearchGate, DOI 10.1109/SysCon66367.2026.11503533; DOI retrieval failed. No authors were contacted.
- Physio-CDE: institution-hosted accepted manuscript inspected. Use the actual acceptance-footer DOI 10.1109/ACCESS.2026.3672553, not the unfilled template header.
- Dataset access: documentation only; no patient files downloaded, account action taken, custodian request sent, or DUA signed. The researcher reports that the OhioT1DM DUA's employee/advisor eligibility rule prevents a direct student request; the cohort plan now follows the [fallback strategy](dataset_fallback_strategy.md).

## Next completion steps

For a submission-grade review, run native database searches with saved queries and exports, deduplicate by DOI/study family, and screen full texts with explicit inclusion reasons. Expand backward and forward citation tracing and inspect final accessible versions. Retain the inaccessible-method flags until resolved. Do not represent this log as a PRISMA flow or invent screening counts: only the curated matrix row count is available.

No paid access, account action or external correspondence was performed. These access limits do not prevent the current revision: the confirmed overlap is already sufficient to withdraw the original broad novelty claim.
