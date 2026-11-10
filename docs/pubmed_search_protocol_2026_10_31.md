# PubMed search protocol and screening ledger — 31 October 2026

**Status:** reproducibility protocol and targeted indexed-result check; not a completed systematic review or PRISMA flow. The web search interface returned PubMed-indexed records for source verification, but did not expose native PubMed query yields/exports. A local NCBI E-utilities request was attempted and failed because DNS resolution was unavailable. No total records retrieved, deduplication count, or exclusion count is claimed. Do not treat the 64/66/69 historical curated-matrix sizes as search yield.

## Search boundary

Question: among people with T1D and short-horizon CGM hypoglycemia prediction, has a study compared explicit relations among timestamped individual insulin/meal event instances against non-graph models given the same information, event timing, model capacity, and patient-disjoint evaluation? Adjacent temporal clinical-event KGs and event-context prediction studies are included to constrain the claim, not as exact matches. Search date/cutoff: 31 October 2026. Language: English titles/abstracts/full texts surfaced in PubMed/web-indexed searches.

## Reproducible PubMed query links

The linked URLs execute these searches live in PubMed; their future hit counts can change. They are recorded here as intended database syntax, not as an exported result set.
### Q1 - T1D hypoglycemia graph prediction

`(("Diabetes Mellitus, Type 1"[Mesh] OR "type 1 diabetes"[tiab] OR T1D[tiab]) AND (hypoglyc*[tiab] OR "low glucose"[tiab]) AND (predict*[tiab] OR forecast*[tiab]) AND (graph[tiab] OR "knowledge graph"[tiab] OR temporal[tiab] OR relational[tiab])) AND ("2000/01/01"[Date - Publication] : "2026/10/31"[Date - Publication])`

[Run this query in PubMed](https://pubmed.ncbi.nlm.nih.gov/?term=%28%28%22Diabetes%20Mellitus%2C%20Type%201%22%5BMesh%5D%20OR%20%22type%201%20diabetes%22%5Btiab%5D%20OR%20T1D%5Btiab%5D%29%20AND%20%28hypoglyc%2A%5Btiab%5D%20OR%20%22low%20glucose%22%5Btiab%5D%29%20AND%20%28predict%2A%5Btiab%5D%20OR%20forecast%2A%5Btiab%5D%29%20AND%20%28graph%5Btiab%5D%20OR%20%22knowledge%20graph%22%5Btiab%5D%20OR%20temporal%5Btiab%5D%20OR%20relational%5Btiab%5D%29%29%20AND%20%28%222000%2F01%2F01%22%5BDate%20-%20Publication%5D%20%3A%20%222026%2F10%2F31%22%5BDate%20-%20Publication%5D%29)

### Q2 - event streams, instances, causal graphs

`((diabetes[tiab] OR diabetic[tiab] OR "Diabetes Mellitus, Type 1"[Mesh]) AND ("event instance"[tiab] OR "event stream"[tiab] OR "temporal graph"[tiab] OR "causal network"[tiab]) AND (glucose[tiab] OR hypoglyc*[tiab] OR insulin[tiab])) AND ("2000/01/01"[Date - Publication] : "2026/10/31"[Date - Publication])`

[Run this query in PubMed](https://pubmed.ncbi.nlm.nih.gov/?term=%28%28diabetes%5Btiab%5D%20OR%20diabetic%5Btiab%5D%20OR%20%22Diabetes%20Mellitus%2C%20Type%201%22%5BMesh%5D%29%20AND%20%28%22event%20instance%22%5Btiab%5D%20OR%20%22event%20stream%22%5Btiab%5D%20OR%20%22temporal%20graph%22%5Btiab%5D%20OR%20%22causal%20network%22%5Btiab%5D%29%20AND%20%28glucose%5Btiab%5D%20OR%20hypoglyc%2A%5Btiab%5D%20OR%20insulin%5Btiab%5D%29%29%20AND%20%28%222000%2F01%2F01%22%5BDate%20-%20Publication%5D%20%3A%20%222026%2F10%2F31%22%5BDate%20-%20Publication%5D%29)

### Q3 - context inputs in T1D risk prediction

`(("Diabetes Mellitus, Type 1"[Mesh] OR "type 1 diabetes"[tiab] OR T1D[tiab]) AND (hypoglyc*[tiab] OR "low glucose"[tiab]) AND (predict*[tiab] OR forecast*[tiab]) AND (insulin[tiab] OR meal[tiab] OR carbohydrate[tiab] OR nutrition[tiab])) AND ("2000/01/01"[Date - Publication] : "2026/10/31"[Date - Publication])`

[Run this query in PubMed](https://pubmed.ncbi.nlm.nih.gov/?term=%28%28%22Diabetes%20Mellitus%2C%20Type%201%22%5BMesh%5D%20OR%20%22type%201%20diabetes%22%5Btiab%5D%20OR%20T1D%5Btiab%5D%29%20AND%20%28hypoglyc%2A%5Btiab%5D%20OR%20%22low%20glucose%22%5Btiab%5D%29%20AND%20%28predict%2A%5Btiab%5D%20OR%20forecast%2A%5Btiab%5D%29%20AND%20%28insulin%5Btiab%5D%20OR%20meal%5Btiab%5D%20OR%20carbohydrate%5Btiab%5D%20OR%20nutrition%5Btiab%5D%29%29%20AND%20%28%222000%2F01%2F01%22%5BDate%20-%20Publication%5D%20%3A%20%222026%2F10%2F31%22%5BDate%20-%20Publication%5D%29)

### Q4 - multimodal temporal models and relations

`(("type 1 diabetes"[tiab] OR T1D[tiab]) AND (CGM[tiab] OR "continuous glucose monitoring"[tiab]) AND (hypoglyc*[tiab] OR "glycemic event"[tiab]) AND (sequence[tiab] OR graph[tiab] OR relation*[tiab] OR representation[tiab]) AND (meal[tiab] OR insulin[tiab] OR event*[tiab])) AND ("2000/01/01"[Date - Publication] : "2026/10/31"[Date - Publication])`

[Run this query in PubMed](https://pubmed.ncbi.nlm.nih.gov/?term=%28%28%22type%201%20diabetes%22%5Btiab%5D%20OR%20T1D%5Btiab%5D%29%20AND%20%28CGM%5Btiab%5D%20OR%20%22continuous%20glucose%20monitoring%22%5Btiab%5D%29%20AND%20%28hypoglyc%2A%5Btiab%5D%20OR%20%22glycemic%20event%22%5Btiab%5D%29%20AND%20%28sequence%5Btiab%5D%20OR%20graph%5Btiab%5D%20OR%20relation%2A%5Btiab%5D%20OR%20representation%5Btiab%5D%29%20AND%20%28meal%5Btiab%5D%20OR%20insulin%5Btiab%5D%20OR%20event%2A%5Btiab%5D%29%29%20AND%20%28%222000%2F01%2F01%22%5BDate%20-%20Publication%5D%20%3A%20%222026%2F10%2F31%22%5BDate%20-%20Publication%5D%29)

## Screening rules

Include: (1) T1D studies predicting near-term hypoglycemia/glycemic events; (2) studies adding insulin, meal, carbohydrate, activity, or wearable context to glucose prediction; (3) temporal/event graphs, KGs, or event-stream relation models in diabetes or general clinical prediction that constrain representation novelty; and (4) directly relevant benchmark/control methods. Label each record as direct T1D predictor, representation-method precedent, adjacent prediction, or review.

Exclude from the core comparator set: molecular/drug-target KGs, T2D-only long-term diagnosis models, unrelated EHR outcomes, general temporal graph methods without clinical/event-stream relevance, and non-predictive management tools. Keep an adjacent-work note where a source still constrains the broad novelty claim.

## Screened evidence status

| Evidence class | Representative records | Current interpretation |
|---|---|---|
| Event-instance / event-time graph precedent | Acharya & Lee 2014; Li, Ge & Chen 2020 | Temporal/causal relations over diabetic event streams are prior art, including insulin, glucose and hypoglycemic symptoms. Tasks are causal-network reconstruction/event-timing, not the current incident-low prediction benchmark. |
| Temporal patient KGs for clinical prediction | Postiglione et al. 2024 MedTKG; Onwuchekwa et al. ESWC 2024/dissertation; Chen et al. 2024 TRANS | Patient temporal KGs and graph-based clinical prediction/explanation are established. The clinical outcomes and event granularity differ. |
| T1D event/context prediction | Zecchin 2016; Dave 2021; Apicella 2026; Oviedo 2019; Athanasiou 2024; Tziavaras 2026; Rehman 2025 | Context, representation, patient-specific postprandial risk, and multimodal event-aware prediction are established. No inspected source provides the exact matched event-instance relation contrast. |
| Close endpoint / evaluation precedents | Hüni thesis; Sarwar JAMIA 2026; Fang et al. MT-HypoNet 2026; Khokhar arXiv 2026 | Graph-based T1D hypoglycemia, 30-minute forewarning, patient-disjoint evaluation and explanation perturbation are not individually novel. Each differs in target, event representation, access, or evaluation details. |
| Systematic synthesis | Quader et al. 2026 meta-analysis; Tsichlaki et al. 2022 review | Useful backward-citation and scope sources. Quader reports its own 611-screened/20-included flow; those are not counts for this project search. |

## Candidate conclusion and missing evidence

The only defensible remaining candidate is an empirical, task-specific result: the effect of already-known event-instance/temporal relation mechanisms under matched information, timing, and capacity on this Loop endpoint and participant split. Current two-seed/five-fold evidence favors time-aligned non-graph pooling, so the contribution may be a controlled negative result. This is not proof that no equivalent study exists.

To complete a submission-grade search, rerun the four queries directly in PubMed and export the records; search Scopus, Web of Science, IEEE Xplore, and ACM DL where access permits; deduplicate by DOI and study family; screen title/abstract then full text with a second reviewer; inspect Quader et al. supplementary/included-study list; and perform backward/forward citation chaining from Acharya & Lee, Li et al., Tziavaras, GAT-BiGRU, MT-HypoNet, and the 2026 any-low patient-disjoint preprint. Until that is done, report this as a targeted novelty assessment, not a systematic review or “first” claim.


## Backward citation screening update

On 31 October 2026, the reference list of Quader et al.'s publisher-hosted
2026 systematic review was screened as a citation-chain source. Three cited
primary studies were added after source checks: Bertachi et al. (2020), Cichosz
et al. (2015), and Mosquera-Lopez et al. (2023). This supplements the targeted
search and does not change its status: native database exports, reproducible
search yields, complete deduplication, and full PRISMA screening are still
missing. The curated literature matrix contains 70 unique records as of this
update; it is not a search-yield count.

A further exact-title primary-source check added Yu et al. (2024), an
asynchronous multimodal and prior-knowledge-guided attention model for
nocturnal T1D hypoglycemia warning on OhioT1DM. The paper uses within-person
time partitions rather than held-out patients and does not test KG relations.
This is a source-chain addition, not a new database-query yield.
