# Independent methods, statistics, and evidence review

Review date: 8 November 2026 (Asia/Dhaka). Reviewer role: an independent AI-agent review of the existing artifacts, requested by the researcher. Evidence snapshot reviewed: 31 October 2026, before the parent agent's journal-quality revision. This is a reproducibility and interpretation review, not independent scientific peer review or statistical certification.

## Scope and method

I inspected the manuscript, its builder, results snapshot, verification output and evidence map; the executed temporal-model implementation; the two-seed aggregation script; the paired-bootstrap implementation; the public cohort, overlap and truncation audits; and selected graph/control, longer-schedule, event-ablation and external-transfer audit records. I did not train a model, score the reserved participants, inspect patient identifiers, or replay all raw prediction shards. Independent arithmetic checks below operate on the public results snapshot, not participant-level observations.

Primary reviewed sources:

- [Current manuscript](../manuscript.md), [template](../manuscript_template.md), [results snapshot](../results_snapshot.csv), [builder](../build_manuscript.py), [verification](../verification.json), and [evidence map](../evidence_map.json).
- [Executed temporal model implementation](../../kaggle_event_sequence_gru/train_history_relations.py), particularly `TemporalRelationModel.__init__` and `forward`.
- [Two-seed aggregation implementation](../../scripts/summarize_two_seed_graph_aligned_control.py) and [paired participant-bootstrap implementation](../../scripts/compare_loop_pilot_archives.py).
- [Two-seed participant summary](../../audit/loop_graph_vs_aligned_nongraph_two_seed_five_fold_participant_summary.json), [second-seed five-fold summary](../../audit/loop_graph_vs_aligned_nongraph_seed20261030_five_fold_summary.json), and [eight-epoch pair](../../audit/loop_longer_schedule_outer0_seed20261031_graph_vs_aligned_cpu8.json).
- [Split coverage](../../audit/loop_model_split_coverage.json), [source CGM audit](../../audit/loop_cgm_patient_cohort_flow.json), [window overlap](../../audit/loop_multimodal_window_overlap.json), [truncation distribution](../../audit/loop_event_sequence_truncation_distribution.json), [event-summary logistic record](../../audit/loop_event_logistic_outer0_validation_v2.json), and [two-epoch event-ablation pair](../../audit/loop_graph_event_ablation_outer0_seed20261031_paired_20261031.json).

## Overall assessment

The saved evidence supports a careful exploratory comparison. The central numerical result is internally consistent: graph minus time-aligned pooling has a participant-macro AP difference of −0.0098996662 and a macro-Brier difference of +0.0001264322 after each participant's effects are averaged over the two fixed seeds. The respective fixed-prediction participant-bootstrap intervals are [−0.0104766942, −0.0093454128] and [+0.0001096007, +0.0001428662]. These are effects for the recorded fits and development participants, not estimates of model-family superiority after optimization or generalization to a new cohort.

The strongest technical limitation is more specific than the draft currently states: the aligned pooling comparator changes the nonlinear CGM pathway even when a time bin contains no events. Therefore this is not a pure removal of the pairwise event–CGM message function. The paper can report that pooling outperformed the tested graph under matched input and parameter-count budgets, but cannot attribute the difference causally to the presence or absence of graph messages.

No substantive arithmetic error was found in the 21-row main numerical snapshot. One feature-count statement is incorrect. Some details needed for full architectural reproduction and the exact summary estimand are insufficiently explicit in the original text. The remaining large gaps—model optimization, clinical warning assessment, replicated event-input effects, demographic characterization, event/graph external evaluation and author declarations—cannot be repaired by prose alone.

## Independent numerical checks

The following checks were run directly on `results_snapshot.csv` and the public aggregate JSON; these checks were additional to the existing manuscript verifier.

| Check | Observed result | Interpretation |
|---|---|---|
| Number of snapshot rows | 21 | Ten graph/late-fusion pairs, ten graph/pooling pairs and one eight-epoch pair. This is not a count of every historical project experiment. |
| Point-estimate differences | All 21 AP and Brier differences agree with first minus second to an absolute tolerance of 1e−12 | Arithmetic consistent. |
| Interval ordering | All 42 metric intervals are ordered and contain their paired point difference | No malformed interval found; this does not validate interval coverage assumptions. |
| Participants per complete five-fold seed | 652 | Matches the development analytic cohort. |
| AP-defined participants per complete five-fold seed | 650 | Two people without positive windows are omitted from AP, not from Brier. |
| Windows per complete five-fold seed | 44,028,064 | Repeated seeds do not create additional independent windows or patients. |
| Positive labels per complete five-fold seed | 1,296,297 | Matches the development summary. |
| Seed-20261029 weighted AP difference | −0.0076067152 | Participant-weighted, unlike the unweighted fold mean. |
| Seed-20261030 weighted AP difference | −0.0121926173 | Agrees with the second-seed aggregate. |
| Average of the two participant-weighted AP differences | −0.0098996662 | Agrees with averaging each person's paired difference over both seeds, because the participant and AP-defined sets are unchanged. |
| Average of the two participant-weighted Brier differences | +0.0001264322 | Agrees with the two-seed aggregate. |

The manuscript verifier states that it checks 42 local completed-run summaries for the 21 central comparisons. I inspected that verification scope but did not independently reread all 42 run files or all prediction records. The separate recomputation receipt reports byte-identical rebuilt summaries; a receipt is provenance evidence, not proof that every original software choice was appropriate.

## Findings requiring revision

### M1. Specify the full aligned-control computation and avoid causal attribution

Severity: major interpretation/reproducibility issue.

The original §2.8 describes independent event encoding, time-bin pooling and fusion, but omits the architecture used to achieve the 36,883-parameter count. The implementation contains:

1. A shared two-to-64 CGM encoder, 17-to-64 event encoder, 64-channel GRU and 64-to-32-to-one head.
2. Sixteen trainable event-channel gains, `1 + 0.1*tanh(g)`, applied to the first 16 event-embedding channels.
3. Event summation in the same nearest-observed-later CGM bins, divided by the square root of each bin's event count (minimum denominator one).
4. A separate event-count feature scaled by `sqrt(64)`.
5. A 129-to-64 fusion layer with tanh.
6. A 64-to-two linear branch-gate layer with sigmoid.
7. A second tanh over gated CGM states, gated pooled events and the learned fusion output.

For a no-event bin, the graph computes `tanh(cgm_state)`, while aligned pooling applies a learned CGM-dependent fusion and gate computation. Equal parameter count therefore does not isolate pairwise event–CGM interactions or alignment as the mechanism. The control's event count is derived from the common input membership and is not extra source information, but its explicit exposure to the fusion layer is another implementation distinction.

Required documentation fix: include layer widths, nonlinearities, gates and the no-event behavior; use a schematic or equations in supplementary methods. Interpret the result as an implementation-level matched-information comparison. Required empirical work for an isolated mechanistic claim: a factorial control sharing the same CGM pathway and fusion computation, with only the event-conditioned message operation changed.

### M2. Correct 14 total features versus 12 added event features

Severity: moderate factual error.

Original §3.6 says: “adding fourteen recorded-event summary features to logistic regression”. The audit's 14-feature list consists of the two original CGM features plus 12 recorded-event summary features. Required wording: “Expanding the two-feature CGM model to 14 features by adding 12 recorded-event summary variables reduced AP …”. The numerical AP values themselves match the audit.

### M3. Name the summary estimand and bootstrap procedure explicitly

Severity: moderate methods omission.

The original methods explain paired bootstrap intervals for graph versus sequence, while the central two-seed graph-versus-pooling summary is mainly explained later in Results. Supplementary statistical methods should define

`d_i = (1/2) Σ_s [AP_graph(i,s) − AP_pool(i,s)]`,

and report `mean_i d_i` over the 650 AP-defined participants. Apply the analogous formula over all 652 people for macro-Brier. Resample participants with replacement; retain both seed-specific effects together before averaging. Document 10,000 draws, percentile interval construction, bootstrap seed 20261031 for AP and 20261032 for Brier, and undefined-AP handling. These facts are in the aggregator source.

Required interpretation: seed-specific fits are fixed, overlapping training sets remain a dependence source, and the same people occur at each seed. These intervals exclude model fitting, selection, cohort and seed uncertainty. A narrow interval is not proof of a clinically meaningful difference. No minimally important predictive difference has been justified.

### M4. Preserve the exploratory selection history

Severity: major design limitation already partly disclosed.

The early protocol prioritized graph-versus-sequence and typed-routing questions. Time-aligned pooling and other controls were introduced after development findings. The current hierarchy is sensible for a retrospective analysis but must not be retroactively described as an untouched prespecified primary comparison or completed nested cross-validation. Add a protocol-to-execution table: original design, executed deviation, reason and inference consequence. Distinguish a repository-local run plan written before a follow-up from an externally registered protocol.

All five configurations have disjoint validation groups, but their training sets overlap, and an additional internal development-test group is withheld within each configuration. “Outer fold” is a repository name and does not alone establish nested model selection. A validation cohort reused for method redesign is not an untouched confirmation set.

### M5. Do not infer an epoch effect from the two- versus eight-epoch headline difference

Severity: major interpretive hazard, mostly handled in the original limitations.

The eight-epoch CPU pair is one fold and one additional seed; the main two-epoch summary averages two other seeds and five folds with heterogeneous first-seed sources. A much smaller gap is a descriptive finding. It cannot isolate schedule duration from seed, fold, hardware and implementation history. Keep “single-fold schedule follow-up” wording, avoid “convergence proved” or “training longer closes the gap”, and do not pool it into the two-seed effect.

### M6. Make AP denominators visible where headline results appear

Severity: moderate reporting improvement.

The AP mean is over 650 people with at least one positive label, whereas Brier is over 652. The methods and Table 1 state this correctly; the abstract should give these denominators for the central result, or make the conditional AP population clear. No-positive participants remain in coverage and Brier. This is not a missing-value imputation issue.

### M7. Separate calibration, alert burden, and clinical outcomes from the measured quantities

Severity: major unexecuted research requirements, correctly acknowledged.

AP is ranking performance under retained prevalence; Brier combines calibration and resolution and is not a complete calibration assessment. Reliability curves, calibration intercept/slope, threshold choice, alert refractory behavior, false alerts per day, sustained-event sensitivity and warning lead times are absent. The any-future-reading target may be positive for a low only five minutes away. It is not a 30-minute guaranteed warning and does not establish prevention of symptomatic or severe hypoglycemia.

The original text appropriately discloses these limits. Documentation should retain them as open experimental requirements rather than treating omission as compliance. Independent explanation evaluation is also missing: selecting “important” events by deletion and then testing their deletion is selection-conditioned, especially when random controls do not match recency/value.

### M8. Bound external transfer claims to the actual model and endpoint

Severity: major interpretation condition, already handled reasonably.

The DCLP3/DCLP5 work tests five frozen two-feature CGM logistic models against persistence on release-local future-CGM labels. It does not evaluate the event graph, does not establish a clinical episode outcome, and does not create five independent cohorts. Raw/adjusted-clock semantics and insulin-state mappings remain unresolved. Report external transfer in a supplementary diagnostic section, without allowing it to substantiate event-relation transportability. An insulin-only external route would need a corresponding source-trained common-input model, not silent removal of carbohydrate channels at external inference.

### M9. Distinguish canonicalization correctness from sensor validity and clinical-event completeness

Severity: material data limitation, appropriately recognized.

The source audit mixes rows and unique timestamps; the manuscript correctly cautions against subtracting ambiguous timestamp counts as if each were one row. Numeric glucose retention after duplicate/conflict handling does not establish device-validity bounds. Participant-level presence of basal, bolus and food records does not mean complete capture in every window; the 22.654% all-three and 20.222% no-record window fractions are coverage diagnostics, not proof of clinical absence. Basal entries are recorded state/rate records, not reconstructed integrated insulin exposure. These distinctions should remain prominent in the master record and methods supplement.

### M10. Repair the reproducibility navigation record

Severity: moderate documentation discrepancy and local prerequisite.

`manuscript/README.md` still says the PDF was not recompiled and Tectonic was unavailable. The current project history shows a compiled PDF; refresh the README using actual artifact checks rather than inherited text. Current working-tree status also lists `LOOPDeviceBasal1.txt` and `LOOPDeviceBasal2.txt` as deleted. This does not invalidate existing caches or paired predictions, but a full raw-to-cache reconstruction currently requires reacquiring or otherwise restoring those upstream source inputs under the applicable terms. Do not restore or redistribute them automatically. Do not describe aggregate-only evidence regeneration as a full training reproduction.

## Initial section ratings

These are subjective editorial/methodological ratings, not journal acceptance probabilities. Scale: **1** = materially unreliable or unsupported; **2** = major evidence or specification gaps; **3** = usable exploratory report with important gaps; **4** = strong, clear and internally consistent within the stated exploratory scope; **5** = unusually complete and reproducible within its stated scope, with no material documentation omission identified. A reporting score cannot turn unperformed research into completed validation.

| Section or dimension | Initial rating / 5 | Main reason |
|---|---:|---|
| Study design and selection history | 3.0 | Honest development framing; protocol deviations and adaptive selection need a consolidated chronology. |
| Cohort and source-data accounting | 4.0 | Large explicit source/window audit and patient denominators; demographic table and exclusion monitoring characterization missing. |
| Endpoint, missingness and eligibility | 4.0 | Threshold, six future slots, recovery rule and masked history clearly specified; no sustained or symptom outcome claimed. |
| Architecture and matched-control specification | 3.0 | Input matching strong, but aligned gates/count/no-event path underdescribed and causal interpretation must be tightened. |
| Training and optimization | 2.5 | Schedules and optimizer are explicit; one/two epochs and one eight-epoch pair do not establish adequate optimization or seed uncertainty. |
| Statistical estimand and uncertainty | 3.5 | Correct participant-level conditional intervals; central two-seed formula and exact bootstrap settings need placement in Methods. |
| Main result arithmetic and denominators | 4.5 | All 21 rows pass independent arithmetic checks; pooled/macro distinction explicit; feature-count sentence needs correction. |
| Event-input and relation robustness | 2.5 | Broad diagnostic set but mostly one-epoch fits; opposite event-input directions and effective-capacity confounding remain. |
| Explanation evidence | 2.0 | Scope is candid; current experiment is selection-conditioned sensitivity, not independent fidelity. |
| External validity | 2.0 | Limited CGM-only transfer; no independent event/graph evaluation and unresolved clocks. |
| Reproducibility and provenance | 3.5 | Hashes, cached identities and saved predictions are valuable; historical source variations, typed raw recovery, environment/archive release and raw-input availability incomplete. |
| Interpretation and clinical restraint | 4.0 | Explicitly avoids causal, clinical utility and first-graph claims; refine graph-versus-pooling mechanism wording further. |

For a high-quality exploratory paper, reporting can be improved immediately. Confirmatory and clinical evidence scores must remain limited until the missing empirical work is actually completed. A high-quality manuscript can make these boundaries clear without presenting the whole project as ready for clinical deployment or a top-tier acceptance decision.

## Revision and follow-up review status

Initial review completed and key findings sent to the parent agent. The parent is revising the synthesis and manuscript. A second read of the revised documents is pending; post-revision scores must be based on those saved artifacts, not presumed improvement.

## Final rereview of the revised dossier

A second review examined the rebuilt compact manuscript, supplementary methods, complete research record, refreshed README and submission-readiness register on 8 November 2026. The main paper now leads with graph versus time-aligned pooling, relegates older model families to contextual diagnostics, and explicitly describes the exploratory development design. The detailed historical results remain in the master record and numerical supplement rather than being removed.

### Resolution of findings

| Finding | Revised state | Final disposition |
|---|---|---|
| M1: control architecture and no-event pathway | Main §3.4 and Supplement S3 give the 129→64 fusion, branch gates, channel gains, parameter bank and event-empty CGM-path difference. Discussion rejects pure message-operation attribution. | Reporting issue resolved; a fully isolated mechanistic experiment remains unperformed. |
| M2: 14 versus 12 added event features | Main §4.3 and master record specify 14 total features: two CGM plus 12 event variables. | Factual correction resolved. |
| M3: summary estimand and bootstrap | Main §3.6 gives participant-first seed averaging; Supplement S5 gives the formula, AP/Brier denominators, 10,000 draws and distinct bootstrap seeds. | Reporting issue resolved. |
| M4: adaptive development history | Main §3.5, Supplement S4/S6 and the master record identify iterative design, rotated internal groups, local plans and absent unchanged prospective registration. | Reporting issue resolved; development-selection uncertainty remains. |
| M5: two versus eight epochs | Main §4.2 and Discussion explicitly prohibit assigning the smaller gap solely to schedule duration and avoid convergence/equivalence claims. | Interpretation resolved; adequate optimization and replicated long-schedule evidence remain open. |
| M6: AP population | Abstract and main metrics give AP n=650 and Brier n=652. | Resolved. |
| M7: clinical performance/explanation scope | Main Discussion and readiness register retain missing calibration, alert/lead-time, independent explanation and prospective evidence. | Correctly disclosed; outputs remain unperformed. |
| M8: external transfer | CGM-only DCLP transfer remains supplementary context with clock/event limitations and no external graph claim. | Scope appropriately bounded; graph/event external evaluation remains absent. |
| M9: source data versus clinical completeness | Main Methods, cohort coverage, master record and supplement distinguish observations, masks, recorded events, basal state and clinical outcomes. | Reporting strong; source semantics, demographic characterization and model-level range sensitivity remain incomplete. |
| M10: reproduction navigation | README now links current artifacts and reproduction commands; master record explicitly identifies missing raw basal tables and limits aggregate regeneration. | Documentation discrepancy resolved; full raw reconstruction still requires source reacquisition and historical-code/environment preservation. |

Minor cross-reference and labeling defects discovered during rereview were sent to the parent: pooling table references after reordering, paired-difference orientation, a duplicated phrase, and “ten fits” versus “ten paired endpoint comparisons.” The current compact Methods uses “graph minus its comparator” and correctly references Tables 2–3. Endpoint-assignment comparisons should consistently be called paired comparisons; this is a terminology distinction rather than a numerical change.

### Independent final numerical verification

All 21 current rows of `results_snapshot.csv` were independently compared directly with their linked public paired-audit JSONs. For AP and macro-Brier, the first and second point estimates, first-minus-second difference, and both interval endpoints agree to an absolute tolerance of 1e−12. Difference arithmetic also passes. This adds source-value checks to the initial review's arithmetic checks. The numerical snapshot SHA-256 at final review is:

`49e33e998b9cbcd830f454d8f2a3eec3cd85f68b251f04eb8d7d2e313e08a1f8`.

The five-fold participant/window/positive totals and two-seed participant-weighted summary remain unchanged. I did not independently refit models, reread all protected prediction shards, perform a new bootstrap, confirm author declarations, or validate the target journal's editorial decision.

### Before-and-after ratings

The same anchored internal 1–5 rubric is used. Scores deliberately remain limited for empirical domains where no new evidence was generated. Improved disclosure raises reporting quality; it does not improve the underlying estimate's generalizability, optimization or clinical evidence.

| Section or dimension | Before | After | Basis for revised rating |
|---|---:|---:|---|
| Study design and selection history | 3.0 | 4.0 | Explicit exploratory hierarchy, protocol/execution ledger and development reuse; untouched confirmation is still absent. |
| Cohort and source-data accounting | 4.0 | 4.0 | Clear cohort flow and coverage; analytic demographics/date bounds remain missing. |
| Endpoint, missingness and eligibility | 4.0 | 4.5 | Compact main contract plus detailed supplement; measured sensor target and information-time assumptions clearly bounded. |
| Architecture and matched-control specification | 3.0 | 4.5 | Full gate/fusion computation, no-event behavior, parameter accounting and effective-capacity caveats. |
| Training and optimization | 2.5 | 2.5 | No new optimization evidence; limited schedules and unequal architectural difficulty remain. |
| Statistical estimand and uncertainty | 3.5 | 4.5 | Correct participant-first seed averaging, exact denominators/settings and conditional uncertainty interpretation. |
| Main result arithmetic and denominators | 4.5 | 4.5 | Source metrics and intervals stable; feature count corrected and headline denominators visible. |
| Event-input and relation robustness | 2.5 | 2.5 | Same mixed/limited diagnostics; stronger causal and event-value claims remain unsupported. |
| Explanation evidence | 2.0 | 2.0 | Selection-conditioned sensitivity only; independent fidelity/usability not added. |
| External validity | 2.0 | 2.0 | Same CGM-only transfer context; no graph/event transportability test. |
| Reproducibility and provenance | 3.5 | 4.0 | Stronger navigation, inventory, exact architecture and explicit source/receipt limitations; historical environment/code/raw prerequisites remain. |
| Interpretation and clinical restraint | 4.0 | 4.5 | Implementation-level claims, explicit CGM-path confounding and no first/causal/utility conclusion. |

Additional dossier ratings within this review's remit: **supplementary methods 4.5/5**, **master research record 4.5/5**, **submission-readiness transparency 4.5/5**. These ratings reflect clarity and traceability of the saved documents, not completion of the missing study requirements. No unweighted average of these heterogeneous scores is offered as a validated overall quality measure.

### Final disposition

The revised manuscript and dossier are acceptable as an internally reviewed, transparent description of the completed exploratory work. I found no remaining substantive numerical error in the 21 central comparisons or the main two-seed summary. The revised writing correctly limits graph-versus-pooling inference to the tested implementations and schedules. It provides a materially stronger basis for author review and journal-specific preparation.

This disposition is not approval for submission or a guarantee of top-tier readiness. Required author/ethics/data-use/code declarations, actual cohort characterization, optimization, calibration/alert outputs, stronger event-input controls, independent explanation evidence and claim-appropriate confirmation remain open exactly as recorded in the readiness register. Those must be supplied or the corresponding claims and journal scope must remain restricted. The internal agent review does not substitute for qualified independent human statistical, clinical or ethics review.
