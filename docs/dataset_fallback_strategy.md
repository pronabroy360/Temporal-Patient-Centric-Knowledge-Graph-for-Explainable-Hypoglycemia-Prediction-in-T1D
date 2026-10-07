# Dataset access and fallback strategy

Updated: 10 September 2026. Status: dataset selection in progress; no patient data have been obtained or audited.

## Access correction

The researcher reports that the OhioT1DM data-use agreement requires the requester to be a current institutional employee and requires a supervising advisor to submit for a student. The researcher does not meet the direct-request requirement. Therefore:

- do not submit an OhioT1DM request in the researcher's own name;
- retain OhioT1DM only as an advisor-mediated candidate if an eligible supervisor is willing to become the requester and accepts the DUA responsibilities;
- do not treat possible advisor support as granted access; and
- do not obtain a copy informally from another researcher or use credentials belonging to another person.

This changes the cohort plan, not the research question. The study can use any lawfully accessible longitudinal T1D cohort that passes the field and sample audit below.

## Candidate routes

| Route | Current role | Access position | Main limitation to resolve |
|---|---|---|---|
| OhioT1DM | Conditional benchmark or later reproduction cohort | Advisor-mediated request only under the reported eligibility rule | Eligible requester, approval, actual release semantics and small participant count |
| Jaeb public-use diabetes datasets | First screening pool for the primary cohort | Several studies have public download/terms pages; eligibility and terms must be checked per release | Raw tables may omit or transform the timestamped insulin, meal, activity or CGM fields needed here |
| AIDE T1D public release | Audited CGM benchmark and possible external-validation source | Local public release is present; retain the Jaeb attribution/disclaimer and release terms | 109 roster records but only 82 analysis-CGM participants; no timestamped meal, activity or insulin-delivery stream; source-order anomalies |
| T1DEXI through Vivli | Controlled-access primary or external candidate | Submit only after reading the study-specific requirements; general Vivli access does not guarantee approval for this contribution | Approval time, secure-environment conditions, available fields and export restrictions |
| D1NAMO | Open feasibility/software pilot | Publicly described as an open dataset | Only nine participants with T1D; insufficient by itself for a strong unseen-participant effectiveness claim |

The Jaeb [diabetes dataset directory](https://public.jaeb.org/datasets/diabetes) is the candidate index and the stated source of the supplied AIDE T1D release. The Loop public-use [request/terms page](https://public.jaeb.org/dataset/560) explicitly permits `none` in the company/institution field, making it a useful access-compatible screening candidate. That form is evidence about requester eligibility, not evidence that its downloadable files contain every required modality. T1DEXI is linked from the Jaeb directory to a controlled-access record and remains conditional. D1NAMO's [project page](https://www.hevs.ch/en/projects/d1namo-nano-tera-snsf-3001) and [repository](https://github.com/PSI-TAMU/D1NAMO) support its use as a small open feasibility source.

The four newly added Jaeb releases are screened in the [candidate comparison](jaeb_candidate_screening.md). Loop is now the provisional full event-relation candidate: 835 participants occur in its CGM, basal, bolus and nonempty-food sets. DCLP3 and DCLP5 have strong CGM–basal–bolus overlap but no nonempty Roche carbohydrate records, so they are insulin–CGM replication candidates. Simultaneous temporal coverage and event timing still require audit.

When additional Jaeb releases are added, record the exact directory study name, download/release name, date obtained, local path, readme/terms version and checksum before opening the data tables. Each release receives its own audit report. Shared field names are not treated as evidence of shared semantics, device clocks, treatment periods, participant eligibility or availability times.

## Dataset selection gate

Complete a documentation and file-structure audit for each candidate before naming a primary cohort. A candidate passes only if all mandatory items are satisfied.

| Requirement | Priority | Evidence to record |
|---|---|---|
| Lawful access for the researcher and intended compute environment | Mandatory | Terms/DUA version, approved user, storage and publication restrictions |
| Stable pseudonymous participant identifier | Mandatory | Dictionary field and uniqueness audit |
| Longitudinal CGM with timestamps and enough observable future samples for 30-minute labels | Mandatory | Sampling cadence, gaps, monitoring days and labelable-window counts |
| Enough independent participants and low episodes for patient-disjoint comparison | Mandatory for the main study | Participant flow, per-person episodes and uncertainty assessment; do not use window count as the independent sample size |
| Timestamped insulin and meal records | Mandatory for the core clinical-relation claim | Raw field names, units, occurrence-time semantics and capture limitations |
| Activity/exercise records | Desirable | Device or self-report source, timestamp semantics and coverage |
| First-usable/entry timestamps | Optional for the core benchmark; required for an empirical reporting-delay claim | Raw metadata and clock semantics |
| Release-stable train/test or sufficient participants for grouped nested validation | Mandatory | Release split or frozen patient-disjoint manifest |

Failure of optional arrival metadata removes the empirical delay claim but does not invalidate the main relation-value experiment. Failure of insulin or meal timing narrows that dataset to a CGM-only or transfer analysis; it cannot serve as evidence for a multimodal clinical-event graph.

## Ordered next steps

1. Screen the public Jaeb candidates' documentation and downloadable file inventories without assuming suitability from the study title.
2. For every release added locally, record provenance and run a release-specific structural audit before ranking candidates.
3. Rank candidates using the selection gate and choose the strongest lawfully accessible cohort as the provisional primary dataset.
4. If T1DEXI fields appear suitable, prepare a Vivli proposal in parallel and record study-specific approval, cost and output-review conditions before submission.
5. If an eligible advisor agrees to sponsor OhioT1DM access, prepare the custodian request through that advisor; otherwise close that route with no effect on the main workflow.
6. Run only the adapter and patient-level audit appropriate to the selected release. Freeze endpoints, folds and model comparisons after the audit, not before it.
7. Use D1NAMO only for adapter/representation feasibility unless its small T1D cohort is explicitly presented as exploratory.

No download, account registration, DUA acceptance or external request is implied by this document.
