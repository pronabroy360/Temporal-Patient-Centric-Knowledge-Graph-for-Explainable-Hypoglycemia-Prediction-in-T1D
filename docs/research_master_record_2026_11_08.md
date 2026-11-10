# Complete research record: temporal event representations for T1D hypoglycemia prediction

Documentation revision: 8 November 2026. Empirical and literature evidence cutoff: 31 October 2026. This record synthesizes the research files available in the current workspace. It describes the executed work, its corrections, the interpretation supported by saved evidence, and the requirements that remain unresolved. It is a research record for the authors and reviewers; it is not a registered protocol or certification of journal acceptance.

## 1. Reading order and authority

The current [manuscript](../manuscript/manuscript.md) provides the journal-style argument; the [supplementary methods](../manuscript/supplementary_methods.md) give the technical contracts, development history, and interpretation boundaries. This master record explains the complete sequence of work. The [document inventory](../manuscript/research_document_inventory.csv) indexes every research document and top-level aggregate audit found in the defined inventory scope, with SHA-256 fingerprints. Three independent AI-assisted reviews and the revision response are in [the review directory](../manuscript/reviews/). These reviews are internal quality control, not independent human peer review.

For numerical claims, the authoritative sources are the saved paired prediction audits and their recomputation receipts, not an earlier chat message, screenshot, notebook display, or historical prose. The [manuscript evidence map](../manuscript/evidence_map.json), [numerical snapshot](../manuscript/results_snapshot.csv), and [verification record](../manuscript/verification.json) identify those sources. The current build verifies 21 central pairs: ten graph-versus-sequence, ten graph-versus-pooling, and one eight-epoch pair. That count excludes many earlier pilots and perturbation studies.

The [original startup handbook](../T1D_Temporal_Patient_Centric_Knowledge_Graph_Research_Starter.md) preserves the initial semantic-KG proposal. Historical documents are retained for provenance. Their statements such as “next computation” or “not yet built” describe their own dated state; they do not supersede this record. The early research protocol remains a proposed design, while the executed methods and deviations are specified here and in the supplement. The empirical cutoff has not been advanced merely by revising the writing on 8 November.

## 2. Scientific question and evolution

The initial project proposed a temporal patient-centric knowledge graph for explainable hypoglycemia prediction in T1D. Prior-art review showed that semantic patient KGs, graph glucose forecasting, graph hypoglycemia prediction, event-context integration, and temporal clinical-event graphs already exist. The scientific question therefore became: what predictive value, if any, does a specified event-relation implementation add when the comparator receives the same information and event timing?

The executed model is a temporal event graph, not a validated clinical knowledge base. Its edges are deterministic associations between recorded basal, bolus, or food instances and observed CGM history slots. Modality-derived expert routing does not supply independent medical assertions. No treatment effect, causal mechanism, insulin recommendation, clinically validated explanation, or prospective benefit is inferred.

The current paper is an exploratory retrospective development comparison. The most informative completed contrast compares a graph with time-aligned event pooling. It matches data membership, labels, timing assignment, optimizer, schedule within each pair, and parameter count. It still changes the nonlinear fusion and CGM processing path; it cannot isolate graph messages as the sole mechanism. This newly explicit limitation is important to interpreting the negative graph comparison.

Sources: [refined proposal](refined_proposal.md), [novelty assessment](novelty_assessment.md), [current novelty report](novelty_evidence_report_2026_10_31.md), and [architecture source](../kaggle_event_sequence_gru/train_history_relations.py).

## 3. Step-by-step execution history

| Stage | Completed action and decision | Authoritative record |
|---|---|---|
| 1. Scope and access | Refined the broad KG idea into a controlled representation question; recorded OhioT1DM advisor/employee access restriction. | proposal_validation.md; dataset_fallback_strategy.md |
| 2. Candidate intake | Screened five supplied Jaeb releases for CGM, treatment records, meals, timestamps, and suitable event granularity. | jaeb_candidate_screening.md; aide_t 1d_release_audit.md |
| 3. Primary release audit | Selected Loop for event-level analysis and inspected chronology, units, raw modality presence and export duplication. | loop_release_audit.md |
| 4. Availability gate | Tested parent-upload linkage; rejected upload time as a valid first-usable timestamp for the shared modalities. | loop_upload_linkage_audit.md |
| 5. Canonicalization | Sorted by participant/UTC, collapsed exact re-exports, excluded conflicting same-time CGM from the grid, retained distinct auxiliary records. | loop_canonical_audit_validation.md |
| 6. Temporal contract | Studied device-clock jitter and logical-grid coverage, froze one-second cadence tolerance and causal history/future eligibility. | loop_tolerance_selection.md; loop_temporal_eligibility_spec.md |
| 7. Frozen windows | Materialized and validated a shared 56,375,850-window index for 835 candidates. | loop_window_index_validation.md |
| 8. Protected partitions | Defined 652 development participants and 183 reserved final-performance participants; audited split membership and coverage. | loop_model_split.md; loop_model_split_coverage.md |
| 9. Baselines and metric correction | Ran rule/logistic baselines; identified tied-score AP defect; corrected metrics and renewed affected development comparisons. | corrected_pilot_recovery.md |
| 10. Event diagnostics | Ran event-summary, frozen-CGM residual, and individual-event sequence models. Summary/residual ranking gains were absent under tested settings. | next_steps_after_event_summary.md |
| 11. Event budget | Audited truncation; replaced a 16-event cap with a shared 64-event contract. | loop_event_sequence_truncation_result.md |
| 12. Remote execution recovery | Corrected compressed/expanded input discovery, preserved completed checkpoints and predictions, and verified downloaded bundles. | loop_gru_completed_validation.md; kaggle_completed_bundle_recovery.md |
| 13. Controlled neural gates | Compared neural CGM controls with event GRUs, recovered epoch checkpoints, and introduced full masked CGM history. | loop_controlled_epoch 1_replay_result_2026_10_11.md; loop_full_history_result_2026_10_17.md |
| 14. Graph and relation studies | Completed graph/sequence, typed/generic routing, event-disabled, endpoint and event-age studies; bounded explanation sensitivity. | loop_temporal_relation_pilot.md; loop_event_age_reassignment_control.md |
| 15. Stricter control | Completed graph versus time-aligned pooling across five folds/two seeds; excluded and reran a mismatched source pair. | loop_time_aligned_nongraph_control.md |
| 16. Schedule and transfer | Completed one eight-epoch CPU pair; audited DCLP clocks/eligibility and transferred frozen CGM-only logistic models. | loop_extended_schedule_protocol_2026_10_31.md; frozen_loop_cgm_jaeb_transfer_20261031.md |
| 17. Synthesis and review | Consolidated prior art, reconstructed numerical summaries, revised the manuscript, and performed three internal reviews. | manuscript/evidence_map.json; manuscript/reviews/ |

The order is broadly defensible as iterative development. It was not error-free: the AP correction, stale notebook input discovery, archive recovery, mixed source fingerprints, and later comparator redesign are material parts of the record. They are retained explicitly rather than recast as a pristine prospective experiment.

## 4. Dataset selection and what each release contributed

| Release | Supplied roster size | Actual role and limits |
|---|---|---|
| Loop public release, 2023-01-31 | 919 | Main event-graph development cohort. CGM, basal, bolus and food transactions were available; 835 had all four modality presences and 652 entered modeling development. |
| AIDE T1D | 109 | Release inventory and CGM chronology screening. No suitable timestamped insulin-delivery, meal, or activity stream was identified. It did not train the reported event models. |
| DCLP3 release 3 | 170 | CGM/pump feasibility and frozen CGM-only transfer. 168 had CGM; selected basal/bolus records were present for 125. No usable meal-carbohydrate column was found. |
| DCLP5 | 101 | CGM/pump feasibility, raw-versus-adjusted-clock sensitivity, frozen CGM-only transfer. 100 had the selected CGM/basal/bolus tables; no usable meals in screened Roche records. |
| FLAIR | 126 | Structural screening for CGM and daily treatment context. Daily insulin summaries do not establish individual delivery events. It did not train the reported event graph. |

These are released-file roster counts, not harmonized clinical recruitment denominators. The original Loop effectiveness publication concerned 558 new users; it must not replace the current release roster or analytic count. The exact released observation-date range and analytic demographic distributions remain unverified in the aggregate model evidence. Original source-study demographics cannot be copied into the present cohort table.

The original published study enrolled U.S.-resident participants during January–August 2019, with collection ending April 2020. Those dates characterize that publication's new-user study, not proven bounds for every record in the broader release. See the [primary original-study article](https://journals.sagepub.com/doi/full/10.1089/dia.2020.0535) and [candidate screening](jaeb_candidate_screening.md).

## 5. Source data, duplicates and occurrence-time replay

The raw Loop CGM scan covered 111,118,148 rows. The sorted canonical audit reports 19,628,647 exact duplicates removed and 91,489,501 canonical rows, with 2,226,685 ambiguous CGM timestamps and 58,403 canonical calibration rows. These categories are generated by the release-specific canonicalizer; they should not be interpreted as a simple mutually exclusive clinical flow diagram without its exact grouping rules. After the documented exclusions, 86,977,148 numeric mmol/L CGM timestamps were usable for temporal auditing. The source values were converted to mg/dL with factor 18.0182 after canonicalization.

Exact duplicates collapse to the lowest source record identifier as a deterministic provenance choice. Conflicting CGM measurements at one patient/UTC time are excluded from the primary grid; conflicting non-CGM records are preserved as distinct recorded instances rather than asserted to be unique physiological events. Calibration records are not outcomes. Auxiliary amounts retain explicit value-known flags. Only validated normal-bolus components contribute known model amounts; basal entries remain recorded pump state, not reconstructed exposure, and the models do not calculate insulin-on-board or carbohydrate-on-board.

The primary numeric-range policy retains numeric CGM readings without claiming a device-validity cutoff. A raw-row sensitivity retained 111,059,420 numeric rows; a 20–600 mg/dL filter retained 111,059,418 and a 40–400 filter 110,685,276. Those are raw-row retention diagnostics, not alternate trained-model results or a justification that extreme readings are valid. The completed graph results were not established to be robust under those alternate model-level policies.

Upload-time linkage failed the arrival-time gate: the majority of key records lack usable upload UTC, and some upload times precede event occurrence. The predictors therefore use retrospective occurrence-time replay with immediate availability assumed. No output establishes measured data-arrival latency. Missing food or insulin records mean absent retained records, not verified absence of eating or delivery.

Sources: [canonical audit](loop_cgm_canonical_audit.md), [canonicalization contract](loop_canonicalization_spec.md), [range policy](loop_cgm_range_policy.md), [range audit](../audit/loop_cgm_range_sensitivity.json), [upload linkage](loop_upload_linkage_audit.md).

## 6. Logical time, eligibility and label construction

The final adapter preserves source observations and uses a logical five-minute grid with a one-second per-interval tolerance for common 299/301-second jitter. Early exact-cadence and contiguous-run counts are diagnostics; they are not the final shared-window counts. The executed contract uses 24 history slots covering (t−120 minutes,t], with nominal slots t−115 through t, at least 22 observed slots, no more than two consecutive missing, and the final three slots observed at glucose >=70 mg/dL. This recent-non-low criterion is a modeling eligibility rule, not a clinical recovery diagnosis.

The primary target is positive if any of the six future observed slots at nominal +5 through +30 minutes is strictly below 70 mg/dL. Exactly 70 is negative at that reading. All six slots must be observed to label either class. Incomplete futures, including those with an observed low, are excluded rather than forced negative. This avoids asymmetric outcome ascertainment but selects well-observed periods. It does not establish a sustained, symptomatic, severe, or preventable hypoglycemic episode. A future low at+5 makes a 30-minute-window label positive, so the horizon is not guaranteed warning lead time.

Full-history neural inputs use zero payload plus an observation mask for a missing glucose slot, with no forward or backward filling. This supersedes an imputation option in the early proposed protocol. Source timestamps and source values remain distinct from grid coordinates. The shared index validates schema, ordering, patient/window identity and labels; it does not validate clinical meaning.

The shared index contains 56,375,850 windows and 1,671,803 positives across 835 participants. Development contributes 44,028,064 windows and 1,296,297 positives. Two development people have no positive windows; AP therefore uses 650 people, while Brier and coverage use 652. Windows overlap within participants and should never be reported as independent patients or independent low episodes.

Sources: [final eligibility](loop_final_cgm_temporal_eligibility.md), [index validation](loop_window_index_validation.md), [history cache](loop_full_cgm_history_gate.md), [history verifier](../audit/loop_cgm_history_cache_validation.json).

## 7. Event capture, cache construction and truncation

All 835 candidates have at least one record from the required modalities at some point, but history-level event capture is incomplete. Of the 56,375,850 shared windows,11,400,398 have no retained basal/bolus/food record in the lookback,24,676,750 have basal alone, and 12,771,176 have all three modalities. These counts describe recorded event presence, not completeness of clinical care or a development-only causal subgroup comparison. All windows remain in the main comparison, including event-empty windows.

The development canonical event cache contains 40,473,171 records:40,459,304 have known permitted model values and 13,867 unknown model values. It collapses 352,188 exact duplicates and retains 124,350 same-time variant events under the stated policy. The cache is bound to the model manifest and CGM-window checksum.

The active event-count distribution has median 13, 90th percentile 28, 95th 36, 99th 45 and maximum 306. A 16-event cap truncated 17,290,614 of 44,028,064 development histories (39.272%);32 truncated 3,039,710;64 truncated 17,720 (about 0.040%);128 truncated 130. The final budget is the newest 64 admissible instances in the two-hour lookback, with newest-first sequence ordering. Basal entries dominate counts, but no modality-specific deletion rule was justified solely by their frequency.

Each event has 17 token channels: validity; three modality flags; eight stable hashed subtype buckets; age/120 minutes; numeric value; value-known; and two export-provenance channels. Both provenance channels are zeroed in the neural runs. Hash buckets can collide. Fixed basal/bolus/food scaling divisors are 10/25/150; CGM is divided by 100. No patient-specific physiological calibration is implied.

Sources: [event cache](loop_event_instance_cache.md), [overlap audit](loop_multimodal_overlap_audit.md), [truncation decision](loop_event_sequence_truncation_result.md), and [event-sequence contract](loop_event_sequence_contract.md).

## 8. Cohort split and development reuse

The model manifest reserves 183 participants for later final-performance evaluation and assigns 652 to development. Aggregate raw-data, eligibility and label-coverage audits included the reserved group. Its predictive model performance is not reported; describing it as wholly unseen data would be inaccurate. Staged neural inputs exclude that group.

Each of five development configurations has mutually exclusive training, validation and internal development-test patients. Across configurations, every development person appears once in a validation set, while training groups overlap. Historical “outer-k” coverage labels sometimes denote the development-test group; neural validation folds use a rotated assignment. The manuscript Table 1 follows actual paired-run validation membership, not a mislabeled historical coverage table.

The early protocol proposed nested patient-level evaluation. Repeated development inspection influenced architecture, input representation, schedules and controls. The completed experiment is therefore exploratory patient-disjoint development evaluation; it is not untouched nested cross-validation. More accurate language does not undo selection effects. A future confirmatory analysis would need frozen model-selection rules and a genuinely protected performance evaluation.

The canonical model-manifest SHA-256 is 69b41e4acfae7d2afc990c8cd15d8fc3f969784d4e5f6534a9263033d341ad52. The development window-identity SHA-256 is 26036d7d3d27c21a4407d15aacd916b98ba598dfded5da319288a74b54a592aa. These identify artifacts; they are not evidence of clinical validity.

## 9. Simple models, AP repair and early negative diagnostics

A transparent persistence/slope score and a two-feature logistic predictor provided initial references. A 15 September review found that tied-score AP had been calculated incorrectly. Threshold-grouped AP version 2 was implemented, AP-defined patient denominators made explicit, affected comparisons superseded, and corrected outputs re-evaluated. Historical JSON remains available for provenance. The main paper uses the corrected version, not a mixture of old and new AP results.

The corrected five-fold logistic reference reports participant-macro AP 0.446938 over 650 people and pooled Brier 0.021590 over 44,028,064 windows; persistence reports 0.209095 and 0.055132. On outer-0 validation, the logistic reference AP is 0.457055 and pooled Brier 0.022880. The event-summary logistic model has 14 total features: two CGM plus 12 event-summary variables. Its AP is 0.425768 and pooled Brier 0.023462. The paired event-minus-CGM AP difference is−0.031288, with fixed-prediction participant interval[−0.037799,−0.025438]. The previous manuscript erroneously called these 14 added event features; this revision corrects that statement.

A 12-candidate frozen-CGM additive-residual diagnostic varied presence/quality versus value summaries, three L2 settings, and one/two epochs. The selected presence/quality residual atL 2=0.01 and two epochs had AP 0.444091 and pooled Brier 0.022503. AP fell by 0.012965 while Brier improved. This establishes neither a general absence of event information nor a contradiction: ranking and probabilistic error are distinct. The tested linear summary branches were stopped without opening final-performance data.

Sources: [metric correction](corrected_pilot_recovery.md), [corrected five-fold result](loop_cgm_corrected_development_result.md), [event summary](loop_event_summary_validation_result.md), [residual result](loop_event_residual_validation_result.md).

## 10. Remote training, recovery and full-history controls

The initial 64-event GRU was run on Kaggle with two T4 GPUs, two epochs, batch 4096, hidden 64 and three producers. Its recovered outer-0 validation AP was 0.471797 and participant-macro Brier 0.021461 across 130 people and 8,885,621 windows. It exceeded the two-feature logistic reference, but this comparison changes both information and model capacity. It cannot isolate event value.

The original notebook repeatedly found zero partitions because a stale script searched compressed suffixes while the mounted data were expanded. IndexError and a later missing-PID diagnostic were consequences of invalid input discovery; idle GPUs alone were not proof of training. Later work repaired discovery/preflight behavior, moved CPU preparation to parallel producers, retained per-epoch checkpoints and participant predictions, and verified the recovered archive. The notebook draft ConcurrencyViolation and stale browser file listings were execution/preservation failures, not evidence that a valid model had or had not trained. Completed-run assertions required actual saved predictions, identity checks and metric replay.

Controlled neural gates then compared a CGM neural baseline with the event GRU, favoring CGM-only in both completed seed fits. These initially used only current glucose and slope as CGM features. A full-history cache subsequently supplied 24 masked CGM slots, independently verified against the frozen windows. In the recovered two-epoch full-history comparison, history-only AP 0.471865 exceeded history-event 0.460532, with paired difference 0.011334; participant-macro Brier was 0.021357 versus 0.021839. Those models had 36,607 versus 36,609 parameters, respectively. A separate sequence event-zero ablation also favored event-zero but is not a graph replication, and its archive lacks an explicit locked-holdout-use field.

An epoch 1 checkpoint's existence is not the same as saved epoch 1 predictions. The documented replay work restores checkpoint evaluation separately; outstanding replay tasks remain historical or open according to their result artifacts. None of the recovery operations authorizes silent retraining or reporting missing checkpoints as complete.

Sources: [GRU recovery](loop_gru_completed_validation.md), [controlled first gate](loop_controlled_first_gate_result_2026_10_05.md), [epoch replay](loop_controlled_epoch1_replay_result_2026_10_11.md), [full-history result](loop_full_history_result_2026_10_17.md), [sequence ablation audit](../audit/loop_full_history_event_ablation_outer0_seed20261003_paired_20261031.json).

## 11. Graph, matched sequence and time-aligned pooling

The graph assigns each retained event to the nearest observed CGM slot at or after that event and no later than the prediction index. Event and target-slot representations, elapsed time, and modality indicators enter three message experts. Generic routing averages expert outputs; typed routing selects by modality. Count-normalized messages are added to CGM-slot embeddings before temporal GRU readout. The capacity-matched late-fusion sequence instead encodes CGM and event histories separately. Both have 36,883 parameters, but computation, fusion, widths and optimization differ.

Across two seeds and five folds at one epoch, the graph exceeded that sequence implementation on AP and macro-Brier in all ten fits. Mean fold AP differences were+0.086532 and+0.086575 at the two seeds. This is not proof of graph-topology benefit or incremental event value over an optimized CGM-only model.

The subsequent time-aligned pooling control preserves event membership and assignment to CGM bins, independently encodes events and pools by bin. Its 8,466-parameter fusion/gating bank replaces the graph message experts while keeping the total 36,883. Importantly it also changes CGM processing in event-empty bins. The result compares complete implementations; a strictly factorial shared-CGM-path control has not been completed.

At two epochs, pooling had higher AP in all ten fold-seed pairs and lower macro-Brier in nine. A source-mismatched first-seed outer-4 graph run was excluded and rerun. Within accepted pairs source fingerprints match, but first-seed fingerprints vary across folds. All second-seed folds share one frozen source digest. The protocol-specified summary averages each participant's paired effects over both fixed seeds, giving graph-minus-pooling AP −0.0098996662 (95% interval−0.0104766942 to−0.0093454128) over 650 people and macro-Brier +0.0001264322 (+0.0001096007 to+0.0001428662) over 652. The intervals condition on the saved fitted predictions.

A separate eight-epoch CPU comparison on outer-0 and seed 20261031 yielded graph AP 0.533263 versus pooling 0.533979; difference−0.000716, interval[−0.001317,−0.000106]. Macro-Brier difference was+0.00001415. The smaller difference cannot be attributed solely to training duration because fold, seed, hardware and source histories differ from the two-seed aggregate. This follow-up does not establish convergence, equivalence or general algorithm superiority.

Sources: [sequence control](loop_non_graph_capacity_matched_control.md), [pooling comparison](loop_time_aligned_nongraph_control.md), [extended schedule](loop_extended_schedule_protocol_2026_10_31.md), [two-seed paired summary](../audit/loop_graph_vs_aligned_nongraph_two_seed_five_fold_participant_summary.json).

## 12. Relation, event-input and explanation diagnostics

Modality-specific routing has mixed results: typed AP is higher in 2/5 folds at one seed, with unweighted mean difference−0.000476. Both models already receive modality information. This tests expert routing, not access to independent clinical relations.

Two graph event-disabled pairs have opposite directions. The one-epoch seed 20261004 outer-0 pair favored events byAP+0.002800; the two-epoch seed 20261031 pair favored disabled by graph-minus-disabledAP−0.002278. Seed and schedule both change, so neither factor is isolated. Zeroing events removes event-encoder/edge-module gradients; matching declared parameter count does not match effective capacity.

Nearest-versus-second-nearest admissible CGM endpoints were compared across two seeds/five folds. The two-seed participant summary favored nearest on AP by+0.002097 and macro-Brier by−0.0000773, with nearest favored in 8/10 fits. This is sensitivity to one topology perturbation. Within-window reassignment of event ages produced a much smaller AP advantage for original pairing, mean+0.0001118, in 10/10 fixed checkpoints; only 3/10 AP intervals excluded zero, and Brier directions split 5/5. These are model sensitivities, not physiological or causal relation validation.

An exploratory explanation screen used 518 event-containing windows across 130 validation people from one checkpoint. Top events were selected using deletion sensitivity, and then assessed with related deletion/retention measures against modality/count-matched random sets. The random sets were not matched for recency/value. The procedure is selection-conditioned and cannot establish independent faithfulness, human usefulness or clinical explanation quality. No blinded clinician or patient evaluation was completed.

Sources: [routing/relations](loop_temporal_relation_pilot.md), [event ablation](loop_event_ablation_result_2026_10_25.md), [endpoint control](loop_endpoint_perturbation_result_2026_10_25.md), [age control](loop_event_age_reassignment_control.md), [explanation screen](loop_graph_event_explanation_faithfulness.md).

## 13. External feasibility and CGM-only transfer

DCLP3 post-randomization data supplied 7,930,123 strict candidate 120-minute-history/30-minute-future windows from 168 participants. DCLP5 raw CGM times supplied 5,113,177 numeric-only windows from 100 participants; adjusted-preferred CGM times supplied 5,123,158. DCLP3 baseline records were excluded because the release documents date misalignment. The candidate counts remain conditional on source-clock rules, sentinel interpretation, duplication handling and eligibility.

Basal/bolus overlap makes an insulin-only external study feasible in principle, but raw/adjusted timestamps can differ by many hours and sometimes more than 24 hours. Basal state, zero-rate meaning, units, extended-bolus mapping and event availability are not harmonized. No usable meals were found in the screened Roche columns. A valid insulin-only external comparison requires a corresponding Loop-trained common-input model rather than silently deleting meal inputs at transfer.

Five frozen two-feature Loop CGM logistic predictors were replayed without refitting on DCLP3 and DCLP5 under the reported timestamp sensitivities. Each exceeded persistence on participant-macro AP and Brier. These are five models tested on reused external participants, not five independent cohorts. Labels are release-local future CGM thresholds; no event graph was transferred, and no clinical episode outcome was validated. The transfer supports limited CGM transportability context only.

Sources: [external feasibility](dclp_temporal_coverage_audit_2026_10_31.md), [transfer report](frozen_loop_cgm_jaeb_transfer_20261031.md), and linked v3 transfer audits.

## 14. Literature and novelty record

The curated matrix contains 70 unique records as of 31 October. Primary-source checks cover diabetic temporal-event causal networks, event-time KGs, temporal patient KGs, T1D graph prediction, same-horizon/Loop benchmarks, event-context ablations, explanation methods and physiological plausibility. A matrix record can be a journal paper, thesis, preprint, review or related study-family output;70 is not a count of independent clinical studies or database search yield.

The review is targeted, not systematic. Native database exports, a complete deduplicated PRISMA flow, independent human screening and complete final-paper retrieval are absent. Some claims are abstract-only or access-limited; related author outputs are not independent replication. The matrix and source notes retain these distinctions. No field-wide absence or “first” assertion is supported.

The candidate contribution is the auditable empirical comparison of recorded event representations and its comparator-dependent results. Current evidence does not support broad graph superiority, a new clinical KG, or clinically faithful explanations. A negative comparison can be scientifically useful when its input contract, control limitations, development selection and optimization uncertainty are accurately reported.

Sources: [matrix](literature_matrix.csv), [search log](literature_search_log.md), [source comparison](targeted_prior_art_search_2026_10_31.md), [search protocol](pubmed_search_protocol_2026_10_31.md).

## 15. Reproducibility, evidence levels and current local state

Evidence has several levels: source-table audit; frozen cache identity; completed-run metadata; paired prediction alignment; metric recomputation; and summary or manuscript regeneration. Passing a downstream hash or arithmetic check does not validate the study design, upstream semantics, clinical endpoint or fairness. The manuscript verifier checks 42 completed run summaries for 21 central pairs and reconciles the two-seed summary to independent recomputation receipts. It does not independently refit every model or repeat all historical prediction processing.

The original artifact corrections are retained. These include tied-score AP repair, direction labels in a superseded Brier comparison, compressed/expanded partition discovery, unsafe zero-partition execution, stale notebook cells, recovery after draft/session failures, and exclusion/rerun of a source-mismatched graph pair. Earlier numerical records are not silently merged with corrected outputs.

Current local git status reports LOOPDeviceBasal1.txt and LOOPDeviceBasal2.txt deleted from the source release. This documentation task did not restore or alter those files. Saved-cache and prediction-audit verification can still succeed, but a complete raw-to-cache rebuild requires authorized reacquisition of the missing upstream tables. There is no claim that the current checkout can regenerate every stage solely from its present raw files. Likewise, current source files cannot automatically substitute for a historical run's source digest.

The aggregate manuscript package excludes raw clinical records, identifiers, patient prediction shards, private caches and checkpoints. In particular, the audit directory also contains an old temporary partition subtree; a generic recursive copy of audit/ would be inappropriate for a public document bundle. Only allowlisted aggregate files are packaged. Public code release still requires a confirmed license, environment record and author-reviewed redistribution plan. The full local worktree is not a publication artifact.

## 16. Journal reporting, internal review and remaining requirements

The primary reporting framework is TRIPOD+AI, with observational description informed by STROBE. PROBAST+AI guides discussion of bias and applicability; no completed independently adjudicated assessment is claimed. ICMJE informs authorship, declarations and AI disclosure. A checklist reports where information is present, partial or unavailable; it does not manufacture missing analyses or guarantee acceptance. The [official-source compliance review](../manuscript/reviews/reporting_standards_review_2026_11_08.md) contains item-level locations and evidence gaps.

Three agents separately reviewed reporting requirements, statistical/methods accuracy, and clinical/editorial quality. Their ratings use an explicit 1–5 internal rubric, not a validated quality instrument. Each recorded baseline ratings, findings, and subsequent revision status. The [revision response](../manuscript/revision_response_2026_11_08.md) identifies text changes, corrected facts and unresolved research or author requirements. AI-agent agreement is not independent human or clinical review.

Submission requires confirmed authors/affiliations, ethics/exemption determination for this secondary analysis, data-use compliance, funding/interests/PPI statements, accurate AI disclosure, a target journal/article type, and code/environment release decisions. Population characterization, source observation dates, demographic/subgroup missingness, calibration, alert burden/lead time, optimization, replicated event-value controls and external graph validation are scientifically unresolved. Some are indispensable for stronger claims; not every exploratory methods paper requires every prospective experiment. The chosen journal and claim determine the final acceptance criteria.

The documentation deliverable is complete only when its numerical tables, source links, review responses and export integrity have been verified. The study must not be described as submission-ready while required author facts or evidence remain absent. See [submission readiness and declarations](../manuscript/submission_readiness_2026_11_08.md).
