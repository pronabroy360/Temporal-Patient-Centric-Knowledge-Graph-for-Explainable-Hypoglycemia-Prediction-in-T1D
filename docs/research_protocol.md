# Research protocol v0.2

Date: 10 September 2026. Status: proposed defaults, not preregistered or frozen. Revise using development data and record changes before exposing evaluation results. Clinical terminology and prior-work checks are in [proposal validation](proposal_validation.md).

The [refined proposal](refined_proposal.md) supplies the research framing;
[decisive experiments](decisive_experiments.md) specifies its additional
controls. This remains the historical v0.2 design: development experiments
have since begun. The executed Loop split, selection history, recovered
results and remaining deviations are documented in the
[2 October crosscheck](research_crosscheck_2026_10_02.md). Its development
results must not be represented as completed untouched nested CV.

## Question and scope

Does a typed temporal patient-event graph improve advance prediction of CGM-defined hypoglycemia over matched tabular, sequence and temporal-neighborhood graph models for previously unseen people with T1D?

Primary horizon: 30 minutes. Secondary horizon: 60 minutes. Use a separate model/head per horizon initially. Primary outcome: any observed CGM value <70 mg/dL within the horizon at an eligible non-low index. This is a threshold-crossing endpoint, not a claim of sustained symptomatic hypoglycemia. Secondary endpoints: <54 mg/dL and sustained-low episodes, subject to event counts.

Select the development/benchmark dataset using the access and field gate in the [fallback strategy](dataset_fallback_strategy.md). Loop is the provisional primary cohort with canonicalization, coverage and window-index audits completed. Upload linkage failed the observed-availability gate; immediate availability is an explicitly retrospective assumption. See the corrected pilot recovery document for the AP correction and current evaluation status. DCLP3 and DCLP5 are insulin–CGM replication candidates. OhioT1DM is available only through an eligible supervising advisor; T1DEXI remains conditional. All analysis is retrospective. No dosing policy or intervention is estimated.

## Eligibility, input, and labels

Proposed rules for a native 5-minute CGM grid:

| Element | Operational definition |
|---|---|
| Prediction index | A valid observed CGM timestamp t; glucose at t is >=70 mg/dL. |
| Recovery eligibility | Valid observed readings at t−10, t−5 and t are all >=70. This causal three-reading rule suppresses prediction during an ongoing low; it is a protocol choice, not a clinical standard. |
| CGM history | (t−120 minutes, t], yielding 24 nominal observations t−115 through t on a complete grid. |
| History coverage | At least 22/24 observations; no more than two consecutive missing grid points; t and the recovery readings must be observed. |
| History filling | Last observation carried forward for at most two grid slots, with missingness and age indicators. Never backfill; remaining missing values receive a training-derived fill plus mask. |
| Future coverage | Primary analysis requires all 6 observations at +5…+30 or all 12 at +5…+60. Otherwise label is unknown and excluded for that horizon, even if a low was observed. This avoids different coverage selection for positives and negatives. |
| Label | 1 if min(observed future glucose) <70, otherwise 0, conditional on complete future coverage. Exactly 70 is not low; exactly 54 is not Level 2. |
| Input events | Only occurrences and fields available by t. No future CGM, outcome nodes, future episode attributes, or target-derived edges. |

Do not silently round irregular source timestamps onto this grid. The adapter must define timestamp tolerance, duplicate resolution and gap detection from source documentation and development-data inspection before implementing these defaults. Raw values and timestamps remain traceable. Apply the same adapter and eligible-window manifest to all models.

Coverage exclusions can select unusually well-observed periods. Report inclusion/exclusion flow, excluded positive-containing incomplete windows, and retained monitoring by participant. A secondary partial-coverage analysis must specify its missing-outcome assumptions separately; it must not silently label missing futures negative. Examine results under stricter complete-history rules and alternative recovery rules selected before final testing.

Do not interpolate CGM targets or shift sensor glucose to match presumed blood-glucose timing. Analyze the recorded CGM endpoint. A future low at +5 minutes is positive for the 30-minute target; this does not mean 30 minutes of warning was achieved.

## Episode and alert analysis

Keep this secondary analysis distinct from the any-low window endpoint. Proposed discrete episode convention: three consecutive 5-minute low samples qualify a sustained episode, onset is the first low; three consecutive samples >=70 establish recovery at the first of those recovery samples. Three samples span 10 minutes between timestamps and represent three sampling intervals only under a sample-hold convention. State this explicitly rather than calling it 15 minutes of continuously observed low glucose. A sensitivity analysis can require four samples spanning 15 elapsed minutes.

Missing samples break episode confirmation. Runs entering or leaving observation gaps have censored boundaries and are excluded from confirmed-onset/complete-duration calculations. Record counts and durations of exclusions. Retrospective episode confirmation may use CGM after onset; none of those future fields are graph inputs.

For each model and horizon:

1. Produce scores at all input-eligible times, independently of future label availability.
2. Choose a threshold on validation participants: maximize confirmed-episode sensitivity subject to <=1 unmatched alert per evaluable monitored day. This alert budget is a proposed research operating point, not a clinical standard. If no useful threshold meets it, report that result; include the full sensitivity–alert-burden curve.
3. Issue an alert when the score reaches threshold and no alert has occurred in the preceding 30 minutes. Refractory suppression uses only elapsed time and prior alerts. Compare a 60-minute refractory period secondarily.
4. Match an alert at a to the earliest unmatched confirmed episode onset s with 0 < s−a <=H. Use one-to-one chronological matching. Subsequent redundant alerts are counted as unmatched burden and reported separately.
5. Score only alerts with complete observable follow-up through a+H and enough extra data to confirm any candidate onset near that boundary. With the three-reading definition this can require H+10 minutes. Refractory behavior still follows the original chronological alert stream, including alerts later excluded for unobservable outcomes.
6. For event sensitivity, require a complete pre-onset observation interval of length H and post-onset confirmation. Report episodes with no input-eligible index in that interval separately and count them as missed in an additional all-observable-episode sensitivity measure.

Report detected/eligible episodes, missed episodes, unmatched alerts per evaluable input-eligible monitored day (sum of eligible 5-minute intervals divided by 24 hours), alert counts during excluded follow-up, and fraction of total monitoring evaluated. Also report total monitored-day burden as a separate denominator. Report median/IQR lead time among detections and proportions of all eligible episodes detected >=15 and >=30 minutes early; add >=45 minutes for H=60. Do not assign missed episodes a zero-minute lead time without labeling that alternative summary.

## Splits and model selection

Primary design: nested patient-disjoint cross-validation. Use outer leave-one-subject-out only when the selected cohort is small enough for it to be computationally and statistically appropriate; otherwise use frozen grouped outer folds. If all 12 OhioT1DM participants become available and eligible, LOSO remains its proposed analysis. Within each outer training set, use fixed grouped inner folds for hyperparameters, early stopping, calibration and threshold selection. Keep outer-patient data out of those decisions. Record release-provided split membership; a custom LOSO analysis is not the original BGLP challenge protocol.

Materialize the outer assignment as a versioned manifest and validate it before fitting any model. The `t1d_tkg.manifest` utility provides deterministic LOSO manifests, checks that each participant appears in exactly one test fold, and produces a canonical checksum for the archived split.

Use development-only results to freeze schema and search space. Run all prespecified outer-fold configurations as one evaluation campaign; do not repeatedly inspect outer-fold errors to redesign the model. Fit scalers, imputers, learned graph embeddings and class weights only within training folds. Make graph objects independent per prediction window, with no shared hidden patient state across folds.

Optional within-patient chronological benchmark: assign whole input/label support intervals to split blocks. Purge any sample whose history or future label interval crosses a boundary. If adding longer summaries, extend the support and purge accordingly. Preserve original release boundaries when reproducing the release benchmark.

Personalization is a separate secondary experiment: adapt using an explicitly earlier patient block, then test on a later block. No learned ID embedding in primary unseen-patient inference. No per-person summary estimated from the full test timeline. Patient context derived from earlier test observations is an explicitly reported online-history condition, not zero-history transfer.

External validation: freeze source-trained preprocessing, model, threshold and calibration before external outcome evaluation. Use harmonized fields available in both datasets. If a reduced-input model is needed, train it on source data first. Report direct transfer separately from recalibration/fine-tuning; adaptation and external test participants/blocks must be disjoint.

## Models and controlled comparisons

Train in stages: persistence/slope scores, logistic regression, boosted trees, GRU, a strong contemporary sequence comparator selected in the literature stage, temporal-neighborhood GNN, and one relation-aware graph model. Include an individual-event sequence comparator, a missingness-aware GRU-D-style comparator, and a fixed modality-summary physiology graph with a matched summary-sequence control. Add a visibility-graph comparator in the CGM-only analysis. These controls follow the newly identified prior work; they are adaptations unless exact reproduction is demonstrated.

Initial graph candidate: node-type projections, a small relation-aware encoder with time-difference edge attributes, then a GRU over chronologically ordered historical CGM embeddings and a final risk head. Size and depth are selected inside development folds. This is a starting architecture, not a novelty claim.

Every decisive comparison uses identical patients, windows, labels, modalities, units, missingness information and historical support. Give engineered glucose/insulin/carbohydrate summaries to all eligible comparators. Initially omit IOB/COB; introduce them only with documented kinetics, appropriate longer history and matched inputs. Record trainable parameters, tuning trials, runtime, memory and random seeds.

Prespecified ablations: full typed graph; generic relation message passing on identical topology; temporal-only graph; no-graph event/sequence model; no time encoding; and modality removals. Preserve parameter budget as closely as feasible and additionally compare capacity-matched models. Relation shuffling, if used, must preserve defined structural constraints and be described as a corruption control. Test genuine variation within source/target type pairs; typed endpoints may already identify the relation. Add an endpoint-type/time-derived relation control on the same topology. When labels are reconstructible, report relation-specific inductive bias rather than additional clinical information.

## Conditional information-availability study

Follow E3 in the [experiment specification](decisive_experiments.md): evaluate observed arrival times where available or explicitly simulated auxiliary-event reporting delays. Keep occurrence times fixed, hide events until arrival, and give all comparators the same admissible records. Compare graph-minus-event-sequence effects across scenarios. A delay scenario is not measured real-world latency, and CGM latency requires a separate stale-input protocol. Reporting-lag attributes are ablated on identical event membership, so their effect is not confounded with access to more events.

## Metrics and statistical analysis

Primary metric: participant-macro average precision (AP, stepwise precision–recall summary) at H=30. Do not interchange it with trapezoidal PR-AUC. Primary contrast: full graph minus multimodal GRU; key prespecified mechanistic contrast: full graph minus generic-relation graph. Report other comparators as planned secondary comparisons, not a post-hoc winning comparison.

Report AP for each participant with positive labels; AP is undefined for no-positive participants, which remain in calibration/alert analyses and are counted explicitly. Report pooled AP, each participant's prevalence, macro denominator, ROC-AUC where both classes exist, Brier score, reliability plots, sensitivity, precision and episode metrics. Retain natural validation/test prevalence even if training uses weighting or subsampling.

Estimate paired differences using 2,000 participant-cluster bootstrap resamples of fixed out-of-fold predictions. Keep all of a sampled participant's windows together and use identical resamples for every model. Record undefined replicates; do not replace them with zero. Report 95% intervals, individual participant differences, and between-seed variability from at least three prespecified seeds. More bootstrap draws do not remedy a small participant sample or capture all refitting uncertainty.

The unit of generalization is a participant, not a window. After the audit, assess precision using participant heterogeneity and episode counts; do not invent a universal minimum or claim power from window count. Select any practically meaningful effect threshold with domain input before testing. If intervals remain broad, call the result inconclusive. A semantic-benefit claim needs agreement across the mechanistic controls, not one positive p-value.

## Explanations and reproducibility

Extract event/edge evidence for the actual frozen predictor. Compare retention (sufficiency) and removal (comprehensiveness) against random masks matched on event type, recency and size. Distinguish message-edge masking from physical event removal. For event removal, rebuild dependent summaries so stale features cannot still reveal the removed event. Report invalid/disconnected perturbations and the potential for out-of-distribution masks.

Report sparsity, probability change, stability across seeds and small admissible perturbations, and evidence provenance. Select cases across true/false positives and false negatives using a prespecified sampling rule. Blinded structured domain review is a later milestone; without it, report computational fidelity only, not clinician usability.

Archive data-release identifiers and local checksums, exclusions, fold manifests, preprocessing/graph configuration, package environment, seeds and predictions. Keep protected patient data out of public releases; publish synthetic fixtures and code subject to dataset terms. The fixture tests strict threshold boundaries, unknown future labels, graph and feature availability-time cutoffs, cross-patient support, and episode/alert matching. Loop duplicate and release-specific policies are audited and versioned. Its upload linkage cannot establish observed event availability, so retrospective immediate availability and later simulated-delay analyses must remain explicitly labeled.
