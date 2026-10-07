# Research plan

Current execution gate (2 October 2026): follow the
[controlled neural experiment specification](loop_controlled_neural_experiments.md)
after the research crosscheck. Infrastructure and CPU checks are complete;
new CGM-neural/event comparisons precede graph claims and holdout evaluation.

Updated: 15 September 2026. The researcher has no fixed deadline and prioritizes the quality of the final output. Progress by completion gates rather than the handbook's original 12-week schedule. Additional complexity must answer a research question; unlimited time does not justify unlimited architectures. The current ordered execution plan is [Next research steps after the recorded-event summary result](next_steps_after_event_summary.md).

The targeted novelty pass is complete: see the [assessment](novelty_assessment.md), [refined proposal](refined_proposal.md), [experiment specification](decisive_experiments.md), and [search log](literature_search_log.md). The literature matrix now contains 21 records, including linked versions/study families. Full-text access and submission-grade systematic screening remain outstanding; novelty is not certified.

## Milestones

| Stage | Work and deliverables | Completion gate |
|---|---|---|
| 1. Establish the research gap | Expand the literature matrix, inspect closest papers and follow-ups, distinguish proposed versus demonstrated methods; write a comparison of schema, timing, task, split and explanation evaluation. | A specific contribution is distinguishable from existing semantic and temporal graph work, or the question is explicitly reframed as a rigorous comparative study. |
| 2. Select, secure and audit data | Apply the [dataset selection gate](dataset_fallback_strategy.md). Screen access-compatible Jaeb public-use releases and T1DEXI; retain OhioT1DM only through an eligible supervising advisor. Record release and use conditions. Build the selected adapter and patient summary tables. | Lawful access is documented; usable chronology, modalities, availability-time assumptions, labelable monitoring and episode counts are known. Assess whether uncertainty is compatible with the intended claim. |
| 3. Freeze the benchmark | Implement labels, causal input extraction, split manifests, alert simulator and leakage checks. Train rule, logistic and boosted-tree baselines. | Boundary/gap tests pass; all models receive the same eligible windows; a versioned protocol and analysis plan are frozen before final evaluation. |
| 4. Establish strong comparators | Implement GRU, selected modern sequence model, event-sequence comparator if needed, and temporal graph. Log tuning budgets and compute. | Non-graph and graph comparators are competitive and information-matched; unexplained failures are resolved. |
| 5. Test relational value | Implement one small semantic model and the prespecified relation, time, topology and modality controls. | Completed paired evaluation with uncertainty; conclusions distinguish semantics, capacity, timing and multimodal features. Negative and inconclusive findings are retained. |
| 6. Validate explanations | Implement masks, evidence paths, random controls, stability and failure-case selection; obtain structured domain review if available. | Computational fidelity is measured; any usability claim has reviewer evidence. |
| 7. Test external transport and adaptation | Map an eligible external dataset, freeze common-feature models, evaluate direct transfer, then a separate adaptation experiment. | External test remains independent; coverage/device/treatment shifts and missing modalities are quantified. If access fails, explicitly limit generalization claims. |
| 8. Produce the paper and reproducibility package | Final tables, figures, limitations, model/data documentation, code and synthetic examples; independent rerun where feasible. | Every abstract claim traces to an experiment or source; no invented results; another researcher can reproduce permitted analyses. |

Stages 1 and 2 should progress together. Data-access waiting time can be used for source review and synthetic software fixtures. Do not train a large model before the benchmark and data audit are sound.

## Immediate work queue

- [x] Review the handbook and verify central prior-work, clinical and access claims.
- [x] Identify omitted semantic hypoglycemia work and revise the novelty assessment.
- [x] Draft an explicit endpoint, split, graph and evaluation protocol.
- [x] Replace the fixed schedule with quality-based milestones.
- [x] Resolve direct OhioT1DM eligibility: the researcher reports being ineligible to submit personally; an eligible supervising advisor would have to request it.
- [ ] Confirm compute resources, domain collaborator availability and whether an eligible advisor will sponsor an OhioT1DM request.
- [x] Extend the accessible closest-work review and formalize the narrower contribution and matched controls.
- [ ] Resolve remaining final-method/supplement access, complete native database/citation screening, and fill unverified literature fields.
- [ ] Screen access-compatible datasets against the mandatory field/sample gate and select a provisional primary cohort.
- [x] Add a repeatable intake template for each newly supplied release.
- [x] Screen the four newly supplied Jaeb releases and measure modality intersections. Loop has 835 participants present across CGM/basal/bolus/nonempty-food sets. DCLP3 and DCLP5 have pump-event overlap but no nonempty Roche carbohydrate records; FLAIR remains treatment-summary/CGM-only.
- [x] Complete the full Loop raw field/chronology scan across CGM, basal, bolus, food, exercise and wizard tables; record units, missingness, source ordering and repeated timestamps.
- [x] Validate Loop parent-upload linkage: it fails the observed availability-time gate because upload UTC coverage is incomplete and often precedes event time.
- [x] Define conservative Loop canonical keys from the full source-adjacent duplicate profile; preserve conflicting non-CGM records and exclude ambiguous CGM timestamps from primary windows.
- [x] Establish that Loop source files are not participant-contiguous: 850 of 851 CGM participants recur in multiple source runs, so a naïve streaming group-by-patient audit is invalid.
- [x] Measure the complete minimal-column 64-way partition footprint without writing derived clinical data: 9.70 GiB projected against 48 GiB free, allowing a one-modality-at-a-time local audit with a two-copy safety allowance.
- [x] Complete the participant-sorted CGM canonical audit: collapse 19,628,647 exact repeats, exclude 58,403 calibration rows and 2,226,685 conflicting CGM timestamps, retaining 86,977,148 usable timestamps across all 851 participants.
- [x] Complete the participant-sorted basal canonical audit: collapse 108,998 exact repeats and preserve 111,314 differing same-time basal records pending source-specific pump-state interpretation.
- [x] Complete participant-sorted bolus, food and exercise canonical audits: remove 304,614, 13,549 and 4,800 exact repeats respectively while preserving differing same-time non-CGM events.
- [x] Reconcile all five canonical audits against raw-row totals and confirm automatic temporary-partition cleanup before cross-modality coverage analysis.
- [x] Freeze the provisional 835-participant multimodal candidate pool: all have source presence for usable CGM, basal, bolus, and nonempty reported carbohydrate; temporal window eligibility remains unmeasured.
- [x] Freeze Loop's release-specific temporal eligibility contract: exact native 5-minute UTC grid, no timestamp rounding/interpolation, strict converted threshold, complete future labels, and gap-broken episode confirmation.
- [x] Complete the first full canonical CGM cadence and strict-grid temporal audit: 86,977,148 non-conflicting numeric mmol/L timestamps; 13,064,186 strict-grid input-eligible 30-minute indices. Frequent 299/301-second jitter requires a development-frozen one-reading-per-slot tolerance before final cohort selection.
- [x] Create a protected deterministic development/holdout split for tolerance selection: 652 development and 183 holdout participants from the 835-person multimodal candidate pool.
- [x] Select the primary per-interval CGM cadence tolerance on development participants only: 300 seconds ±1 second. Keep exact 300 seconds as a sensitivity analysis.
- [x] Apply the frozen ±1-second cadence rule to the 835-person candidate pool: 61,446,087 protocol-style 30-minute input-eligible CGM indices and 4,139,028 positive future-low labels; subsequent cohort, episode and event-alignment gates are complete.
- [x] Complete patient-level CGM cohort flow: all 835 candidates have at least one logical-grid eligible index at both horizons; 63,027,387 complete 60-minute labels and 5,411,877 positive 60-minute labels are available.
- [x] Complete confirmed/censored episode audit: 250,639 confirmed onsets across 834 candidates, 432,023 boundary-censored low runs, and 68,282 short unconfirmed low runs.
- [x] Confirm raw auxiliary-event presence within CGM spans for all 835 candidates: basal, bolus and nonempty carbohydrate records all have complete UTC parsing. Prediction-index alignment is complete; observed event availability remains unavailable because upload linkage failed its gate.
- [x] Implement a provenance-preserving, line-by-line Loop adapter with protected participant filtering; it does not materialize or silently deduplicate the raw release.
- [x] Build and validate the manifest-driven eligible-window index; retain only protected participant/index metadata and stream or cache event payloads under versioned contracts.
- [x] Define and test the compact JSONL window-index format with byte-level SHA-256 reconciliation; release-backed index generation remains pending the final range policy.
- [x] Add a validation CLI for window-index schema and label invariants before model execution.
- [x] Reject duplicate sample IDs and contradictory patient fold assignments during index validation.
- [x] Add a manifest-to-window-index fold-assignment bridge so comparator models share one validated split.
- [x] Extend the validation CLI to check indexed fold IDs against the validated LOSO manifest.
- [x] Add exact-file SHA-256 verification to prevent post-audit window-index edits.
- [x] Test rejection of a structurally valid index whose fold assignment disagrees with the shared manifest.
- [x] Add a read-only aggregate script for release-backed CGM range-policy sensitivity counts.
- [x] Run the raw Loop range-policy sensitivity scan: the unfiltered policy retains all 111,059,420 numeric rows; bounded policies remain development sensitivities pending canonical/window-level impact.
- [x] Freeze `observed_numeric` as the provisional primary CGM range policy; retain bounded policies for prespecified sensitivity analyses.
- [x] Extend the partitioned CGM audit to emit gzip-compressed, metadata-only eligible/known logical-grid windows and add directory-level index validation.
- [x] Generate and validate the protected primary Loop window index: 56,375,850 eligible/known 30-minute windows, 1,671,803 positives (2.966%), 835 participants, and archived partition digest.
- [x] Implement and test ordered as-of event/window alignment; partitioned raw-event extraction remains next.
- [x] Implement storage-bounded canonical event/window coverage audit for basal, bolus, and food; release-backed execution remains next.
- [x] Complete release-backed 120-minute auxiliary-event alignment: basal coverage 78.193%, bolus 33.520%, and food 25.362% of frozen windows.
- [x] Add a storage-bounded overlap audit for all eight basal/bolus/food recorded-presence patterns; execution remains pending.
- [x] Complete the overlap audit: 12,771,176 windows (22.654%) contain recorded basal, bolus, and food histories; 11,400,398 (20.222%) contain none. Use all windows for primary information-matched models and all-three windows only as a strict sensitivity cohort.
- [x] Implement and freeze a deterministic five-fold development manifest with distinct train, validation, and test groups; retain the 183 tolerance-holdout participants as a locked final evaluation set.
- [x] Add a protected window-index split-coverage audit to verify participant membership and label balance before training.
- [x] Complete split-coverage validation: all 56,375,850 windows map to the frozen 652-person development folds or 183-person locked holdout; prevalence ranges from 2.737% to 3.141% across groups.
- [x] Implement and test development-only release-backed CGM persistence/slope baseline evaluation; execution remains next.
- [x] Recompute the development-only persistence/slope reference with corrected tied-score AP: macro AP 0.209095 over the 650 AP-defined participants and 44,028,064 windows.
- [x] Implement and test a repeatable streaming standardized logistic fitter for storage-bounded fold-local learned baselines.
- [x] Implement a one-fold, validation-only release-backed CGM logistic pilot with locked-holdout exclusion; execution remains next.
- [x] Complete corrected matched outer-0 validation: two-feature logistic macro AP 0.457055 versus 0.210490 for the same-input persistence/slope rule.
- [x] Freeze a two-candidate, validation-only epoch-selection rule for the CGM logistic baseline; candidate-B execution remains next.
- [x] Renew the two-epoch CGM logistic selection using corrected outer-0 validation AP 0.457055 and Brier 0.022880.
- [x] Complete corrected outer-0 development-test evaluation: macro AP 0.457896 and Brier 0.023249.
- [x] Complete corrected five-fold development-only CGM evaluation: macro AP 0.446938 and pooled Brier 0.021590, versus rule AP 0.209095 and Brier 0.055132; the locked holdout remains predictively unevaluated.
- [x] Define and test the compact recorded basal/bolus/food feature contract for the information-matched event-summary comparator.
- [x] Add a Kaggle training notebook for compact prepared features with cuML/scikit-learn fallback; feature-table export is the prerequisite before GPU training.
- [x] Define named primary and sensitivity CGM range policies; no bounded policy is selected without development evidence and domain justification.
- [x] Complete numeric CGM range audit: all values parse, but the observed 1–592 mg/dL range does not justify an undocumented clinical exclusion cutoff. Range sensitivity remains required before model training.
- [ ] Run a participant-sorted duplicate and coverage audit without materializing a second full Loop copy; use simulated auxiliary-event delays for the availability sensitivity study.
- [ ] Complete the selected release's authorized access steps; no request, registration or download has been performed in this session.
- [x] Prepare a release/access register and pre-import audit gate; execution remains blocked until authorization.
- [x] Implement and test the synthetic fixture covering missing futures, threshold boundaries, ongoing lows, delayed entry, and future-event exclusion.
- [x] Implement and test dependency-free metrics, confirmed-episode detection, alert suppression/matching, and the persistence/slope baseline.
- [x] Implement and test the first CGM-only feature extractor, transparent logistic smoke model, and LOSO runner.
- [x] Add a protected development-only CGM feature cache with frozen-window verification; raw and cached pilot paths produce identical synthetic results.
- [x] Build the release-backed development CGM feature cache and reconcile all 44,028,064 cached windows with the frozen index.
- [x] Recompute all five CGM development-test folds with corrected AP, explicit AP denominators, prediction archives, and the verified feature cache.
- [x] Make the recorded-event pilot consume the verified CGM cache; raw and cached event paths produce identical synthetic results.
- [x] Evaluate and pairwise-audit the first recorded-event summary model on outer-0 validation; it underperforms matched CGM logistic and is stopped before test/holdout evaluation.
- [x] Test a nested event contribution on development validation: the selected
  residual improved Brier but reduced participant-macro AP, so it is stopped
  before development-test evaluation. See
  [residual result](loop_event_residual_validation_result.md).
- [ ] Test the individual-event timing representation on development validation
  to distinguish summary/optimization failure from lack of recorded-event signal.
- [x] Add matched captured-event and individual-event sequence smoke comparators with the same as-of information contract.
- [x] Extend the audit to report coverage bounds, longest CGM gap, duplicate timestamps, arrival-metadata categories, and confirmed episode counts without silently resolving duplicates.
- [x] Implement deterministic paired participant-cluster bootstrap utilities for fixed out-of-fold AP/Brier contrasts; application to patient predictions remains pending data.
- [x] Add opt-in participant-keyed out-of-fold prediction archives to the LOSO runners for reproducible paired analysis.
- [x] Implement fold-local Platt calibration and reliability/ECE diagnostics; application to patient predictions remains pending data.
- [x] Implement alert-stream simulation and validation-only threshold selection with refractory suppression, one-to-one episode matching, and an explicit alert-burden budget.
- [x] Add a transparent as-of graph-summary smoke comparator with typed, generic-relation, and no-relation controls; learned temporal GNN implementation remains pending the data audit.
- [x] Add deterministic patient-disjoint fold manifests with validation and checksums so all model families share an auditable split.
- [x] Add provenance-safe evidence records and graph masks for later explanation fidelity experiments; model-specific attribution remains pending the learned graph.
- [x] Add canonical-event collection validation to surface release anomalies before window construction; source-specific policies remain pending the authorized audit.
- [x] Add an end-to-end synthetic artifact runner covering audit, manifest, baseline metrics, predictions, and paired bootstrap output.
- [x] Validate archived out-of-fold predictions against the shared manifest before uncertainty analysis.
- [x] Make all LOSO runners consume the validated shared manifest when supplied.
- [x] Record protocol parameters as a validated versioned configuration in benchmark artifacts.
- [x] Obtain a candidate AIDE T1D release and generate an initial structural/chronology audit; sorted coverage, duplicate policy and event-source limitations remain before window construction.
- [x] Freeze and unit-test conservative Loop exact-repeat and conflicting-CGM canonicalization rules without materializing a second raw-data copy.

## First empirical deliverable

One row per participant, plus a documented cohort flow:

```text
dataset/release, participant, source split, valid monitoring days,
CGM coverage, longest gap, duplicate/time anomalies,
confirmed episodes <70 and <54, censored episodes,
input-eligible indices, valid 30m labels, valid 60m labels,
unknown future labels, prevalence, observed insulin/meal/activity counts,
modality capture status, availability-time metadata status
```

Do not equate absent meal records with verified fasting or absent bolus records with zero delivered insulin. For reported events, calculate record density and capture status rather than an unsupported percentage of all true events recorded.

## Decisions to revisit with evidence

| Decision | Current default | Evidence needed |
|---|---|---|
| Main cohort | Loop provisionally | Timestamp validity, cross-shard duplicates, simultaneous modality coverage, future-CGM windows and episode audit |
| Insulin–CGM replication | DCLP3 and DCLP5 provisionally | Timestamp alignment, source overlap, usable windows and release-specific treatment periods |
| AIDE T1D role | CGM benchmark/validation candidate; not sufficient alone for the clinical-event relation claim | Sorted coverage, duplicate policy, participant-level windows, and explicit CGM-only scope |
| OhioT1DM role | Conditional advisor-mediated benchmark/reproduction cohort | Eligible advisor request, approval and release audit |
| External cohort | A distinct eligible cohort; T1DEXI remains a candidate | Release dictionary, access, comparable future CGM and modalities |
| Main horizon | 30 minutes; 60 secondary | Domain review and enough evaluable episodes |
| Main model | Small relation-aware encoder plus GRU | Novelty review, development-only checks and compute audit |
| Added physiology / long history | Secondary | Capture quality and matched comparator inputs |
| Personalization | Secondary, separate from unseen-patient evaluation | Enough earlier adaptation data and later independent outcomes |
| Clinician usability claims | Deferred | Blinded structured reviewer study |

If the graph adds no measurable value, analyze why and report the comparison. Do not redefine success after seeing test outcomes. If event counts are too sparse, obtain a more appropriate cohort or explicitly narrow the claim before further model selection.
