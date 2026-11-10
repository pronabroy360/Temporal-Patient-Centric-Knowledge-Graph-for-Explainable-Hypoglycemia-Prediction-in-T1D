# Novelty status and paper direction

**Evidence reviewed through 31 October 2026.** This is the current novelty
decision record for the project. It distinguishes the research question, the
results actually supported by local artifacts, and the evidence still needed
before submission. The earlier machine-readable inventory is
[`audit/novelty_evidence_bundle_20261031_v9.json`](../audit/novelty_evidence_bundle_20261031_v9.json); the completed matched-control results and current prior-art synthesis are in the
[31 October evidence report](novelty_evidence_report_2026_10_31.md). The first seed's five matched-control folds have varying source digests; the completed second seed uses one frozen source digest across all five folds. Both limitations are retained where relevant.

A predeclared eight-epoch CPU schedule check is now complete for outer-0 at
seed 20261031. Its paired AP difference (graph minus aligned pooling) was
−0.000716 (95% fixed-prediction participant interval [−0.001317, −0.000106]);
the macro-Brier difference was +0.00001415 ([+0.00000111, +0.00002768]). This
keeps the direction favoring pooling but sharply narrows the effect compared
with the two-epoch multi-fold aggregate. It is only one fold and one seed, so
it does not establish convergence or model-fit uncertainty. See the
[protocol and result](loop_extended_schedule_protocol_2026_10_31.md).

## Decision

The project has a potentially publishable **comparative empirical question**,
but the present evidence does not support a new knowledge-graph method, a
first-in-T1D claim, a claim that clinical relations add predictive
information, or a claim of faithful clinical explanations.

The most directly relevant graph-specific comparison now has five completed,
two-epoch folds at seed 20261029. Within each fold, graph and time-aligned
non-graph models used the same event tokens, event-to-CGM bins, optimizer,
participant membership, input/window contracts, and exactly 36,883 trainable
parameters. The five validation folds cover 652 disjoint development
participants. Aligned pooling had higher participant-macro AP in all five
folds: graph-minus-control differences were −0.008941 (outer-0), −0.005902
(outer-1), −0.011140 (outer-2), −0.006601 (outer-3), and −0.005691
(outer-4). Each paired participant-bootstrap interval excluded zero in the
same direction; these intervals condition on fixed predictions and do not
represent model-refitting uncertainty. Macro-Brier favored the graph only in
outer-0 (difference −0.000118) and favored aligned pooling in outer-1 through
outer-4 (differences +0.000174, +0.000152, +0.000078, and +0.000111). The
within-fold comparisons are strict and prediction identities match, but the
whole-project source digests vary across folds (`168ee…` for outer-0, `a4d1…`
for outer-1 and outer-4, `a54c…` for outer-2 and outer-3). The original
outer-4 graph artifact had a different source digest from its control and was
excluded; the graph was rerun under the control's `a4d1…` source before
comparison. Thus, this is five-fold one-seed evidence, but not an exact-source
five-fold replication.

The prespecified second seed (`20261030`) is complete across all five folds
under one frozen source digest. The strict paired audits favor aligned pooling
on both AP and macro-Brier in every fold. Across the 652 development
participants, the saved-prediction aggregate gives graph-minus-control AP
−0.012193 (95% fixed-prediction participant interval [−0.012935, −0.011445])
and macro-Brier +0.0001728 ([+0.0001554, +0.0001894]).

The protocol-specified two-seed participant summary averages each person's
paired differences across both fixed seeds before participant bootstrap. It
favors pooling: graph-minus-control AP −0.009900 (95% interval
[−0.010477, −0.009345]) over 650 AP-defined participants, and macro-Brier
+0.0001264 ([+0.0001096, +0.0001429]) over 652 participants. Pooling leads AP
for 639 participants and Brier for 528. The same participant folds are reused
across seeds; these intervals condition on the fitted predictions and do not
measure seed or cohort uncertainty. See the [two-seed aggregate](../audit/loop_graph_vs_aligned_nongraph_two_seed_five_fold_participant_summary.json)
and the [second-seed five-fold aggregate](../audit/loop_graph_vs_aligned_nongraph_seed20261030_five_fold_summary.json).

Separately, the earlier graph-generic vs. late-fusion event-sequence screen
favored the graph implementation in ten one-epoch fold-seed fits. That
comparison cannot be attributed to graph topology because the architectures
fuse and process information differently. Taken together, the evidence says
the graph-vs-sequence result is comparator-dependent; it does not establish a
general graph or clinical-relation effect.

The defensible paper question is:

> **When does explicit alignment of recorded insulin and meal events to a
> patient’s recent CGM history improve short-horizon hypoglycemia-risk
> prediction over equally informed, capacity-matched temporal models, and
> which modeling choice accounts for any improvement?**

For current analyses, describe event availability as retrospective
occurrence-time replay with immediate availability assumed. Actual reporting
latency was not measured.

## What the implementation is

The released experiments construct a per-window temporal event graph: 24
five-minute CGM slots, including observation masks, and up to 64 individual
basal, bolus, or food event tokens over two hours. Each retained event is
connected to the nearest observed CGM slot at or after its recorded occurrence
time. The edge is derived from timestamps and the event modality is already a
model input. Graph messages are summed at CGM slots before a recurrent readout.

This is a useful **temporal event graph** representation. It is not yet a
persistent patient knowledge graph, an externally authored ontology, or a
graph of independently asserted causal clinical relations. “Patient-centric
knowledge graph” in the current project title risks promising those stronger
properties. A safer working title is:

> **Event-to-CGM Temporal Graphs for Short-Horizon Hypoglycemia Risk: A
> Patient-Disjoint Comparison with Matched Sequence Models**

The paper should call the experiment a development comparison, not confirmatory
validation. The graph and relation experiments use Loop. A separate frozen
CGM-only transfer diagnostic now covers DCLP3 and DCLP5; it does not transfer
events or validate graph relations. A new identifier-free timestamp-span audit
found basal and delivered-bolus events inside the broad CGM span for 125
DCLP3 and 100 DCLP5 participants, creating a possible insulin-only external
validation route. A follow-up sorted, duplicate-aware audit found 7,930,123
candidate 120-minute-history/30-minute-future windows in DCLP3
post-randomization data and 5,113,177 raw-CGM-time windows in DCLP5 under the
initial mixed timestamp policy. Positive prevalence was 3.05% and 3.29%,
respectively. A consistent adjusted-preferred DCLP5 run yields 5,123,158
windows and 168,656 positives; raw/adjusted choices also change pump-event
lookback counts. DCLP5 low-sentinel handling is reported by timestamp policy.
These counts establish feasibility and policy sensitivity only: source clock
semantics, basal-state reconstruction, availability and exact transfer parity
remain to be checked. The five frozen Loop CGM logistic models were replayed
without refit on both cohorts and beat the persistence-slope comparator for
the release-local future-CGM endpoint in DCLP3 raw and DCLP5 raw/adjusted-
preferred sensitivities. This is limited external CGM context, not model
validation of insulin events or graph relations. See the [DCLP temporal
screen](dclp_temporal_coverage_audit_2026_10_31.md) and [transfer
report](frozen_loop_cgm_jaeb_transfer_20261031.md).

## Executed evidence

| Experiment | Verified result | Supported interpretation | Main limitation |
|---|---|---|---|
| Graph-generic vs. capacity-matched late-fusion event sequence | Five folds × two seeds; 36,883 parameters each; 24-step CGM history, up to 64 events; one epoch; exact paired window identities. Graph AP is higher and macro-Brier lower in 10/10 fits. Descriptive mean AP difference is +0.086532 at seed 20261003 and +0.086575 at seed 20261004; mean macro-Brier differences are −0.002113 and −0.002220. | Strong directional evidence that this graph implementation outperformed this sequence implementation under the specified development protocol. | One epoch per fit; only two seeds; folds reuse the same study and rotated participant groups; bootstrap intervals condition on fixed predictions. Fusion point, alignment, recurrent structures, message aggregation, and optimization differ, so this is not a graph-topology-only causal contrast. See [ten-fit summary](../audit/loop_mps_graph_sequence_two_seed_five_fold_summary_20261020.json). |
| Graph-generic vs. time-aligned non-graph pooling control | Two seeds × five disjoint folds, two epochs, exactly 36,883 parameters; same event inputs and causal event-to-bin timing. Seed 20261029: pooling has higher AP in all five folds; macro-Brier favors graph in one and pooling in four; source digests vary by fold but match within each pair. Seed 20261030: one frozen source digest across all folds; pooling leads AP and macro-Brier in all five folds. Across 652 participants after averaging each participant's paired differences over the two seeds, graph-minus-control AP is −0.009900 (95% fixed-prediction participant interval [−0.010477, −0.009345]) among 650 AP-defined participants; macro-Brier is +0.0001264 ([+0.0001096, +0.0001429]). Pooling leads AP for 639 participants and Brier for 528. | Evidence that the tested graph message-passing operation does not improve prediction over same-information, same-timing pooling under this two-epoch Loop development protocol. | Same cohort and patient folds across seeds; intervals condition on saved fits and do not capture refitting or cohort uncertainty. This does not establish general graph ineffectiveness, clinical-relation invalidity, or clinical utility. Event availability remains assumed immediate; locked holdout is unopened. See the [two-seed participant summary](../audit/loop_graph_vs_aligned_nongraph_two_seed_five_fold_participant_summary.json), [second-seed aggregate](../audit/loop_graph_vs_aligned_nongraph_seed20261030_five_fold_summary.json), and [time-aligned control protocol](loop_time_aligned_nongraph_control.md). |
| Modality-typed vs. generic graph routing | Five folds, one seed, identical parameter count. Typed AP was higher in 2/5 folds and lower in 3/5; mean fold typed-minus-generic AP was −0.000476. Brier direction was mixed. | The tested modality-specific expert routing did not show a consistent advantage over generic routing. | Single seed; relation labels are derived from modality and time, not independently curated clinical assertions. See [five-fold typed-routing summary](../audit/loop_relation_typed_vs_generic_seed20261004_five_fold_summary_20261020.json). |
| Event-input ablation inside the generic graph | One outer-0 pair: generic graph minus event-disabled AP +0.002800 (fixed-prediction 95% participant-bootstrap interval [+0.001996, +0.003609]); macro-Brier −0.000200. | Preliminary evidence that event inputs can help the tested graph fit in this one comparison. | Only one fold/pair. A separate two-epoch sequence event-zero pair on outer-0/seed 20261003 favors event-zero but is not a graph replication. Disabling events also removes event-encoder/edge-expert gradients, and that recovered archive lacks an explicit locked-holdout-use field; neither pair establishes a general event effect or isolates relations. See [paired ablation](../audit/loop_relation_event_ablation_outer0_seed20261004_paired_20261025.json). |
| Nearest vs. second-nearest causal CGM endpoint | Two seeds × five folds. A participant-cluster bootstrap after averaging each participant’s paired difference across the two fixed seeds estimated nearest-minus-second-nearest AP +0.002097 (95% interval [+0.001761, +0.002443]) and macro-Brier −0.0000773 ([-0.0000957, −0.0000594]); nearest favored on both metrics in 8/10 seed-fold pairs. | The predictions are sensitive to this specific event-to-CGM endpoint assignment. | One perturbation and two one-epoch seeds; this does not establish relation validity or graph superiority. See [endpoint cluster bootstrap](../audit/loop_relation_endpoint_perturbation_two_seed_participant_cluster_bootstrap_20261028.json). |
| Within-window event-age reassignment | Two seeds × five fixed epoch-1 checkpoints. Original pairing has higher AP in 10/10, with mean difference +0.0001118; only 3/10 fold-specific participant intervals exclude zero. Brier direction is split 5/5. Clean replay reproduced archived scores and prediction identities. | Small, metric-dependent fixed-model sensitivity to one deterministic reassignment of event ages. | Not retraining, no pooled cross-seed participant bootstrap, and not evidence for clinical relations. See [event-age summary](../audit/loop_event_age_reassignment_two_seed_five_fold_summary_20261029.json). |
| Event explanation sensitivity sample | Deterministic sample of 518 event-containing windows from all 130 outer-0 validation participants. Top-three tokens chosen by single-event deletion sensitivity; joint deletion effect exceeded modality-matched random by participant-average 0.003943, and retaining top tokens reduced deviation from original prediction by 0.003841 versus random sets. | A preliminary local model-sensitivity result for one checkpoint. | The top events were selected using deletion sensitivity, so the joint-deletion comparison is selection-conditioned. Random sets are not matched on recency/value. It is not an independent faithfulness test, causal explanation, or clinical validation. See [report](loop_graph_event_explanation_faithfulness.md) and [aggregate output](../audit/loop_graph_event_explanation_faithfulness_outer0_seed20261005_20261029_v2.json). |
| Earlier CGM-only vs. event-model diagnostics | The two-seed outer-0 CGM-MLP vs clean-GRU gate favored CGM-only on AP and Brier in both seeds; the separate one-seed full-history comparison also favored CGM-only over its event-enabled sequence model. | The effect is representation-dependent; the graph-vs-sequence result must not be described as proof that events generally add value beyond CGM. | These are distinct architectures and schedules from the graph comparison. See [two-seed first-gate summary](../audit/loop_first_gate_two_seed_summary_20261018.json) and [full-history paired result](../audit/loop_full_history_paired_recovered_20261017.json). |

The predictive target in these runs is any one of the six observed future CGM
readings at nominal +5 through +30 minutes below 70 mg/dL. A label is known
only when all six future readings are observed; incomplete futures are not
treated as negative. It does not require sustained hypoglycemia, symptoms, or
the <54 mg/dL threshold. The locked cohort is reserved and was not evaluated.

## Prior art that constrains novelty

1. **Semantic patient-specific T1D KGs already exist as a proposal.** The
   ESWC 2024 paper proposes patient-specific contextual KGs and semantic
   integration for T1D hypoglycemia prediction; its own conclusions call the
   research early-stage. The 2025 dissertation describes preliminary work but
   does not establish the matched outpatient CGM relation benchmark used here.
   Therefore “first patient-centric semantic KG for T1D hypoglycemia” is not a
   tenable claim. [ESWC paper](https://2024.eswc-conferences.org/wp-content/uploads/2024/05/77770363.pdf),
   [dissertation](https://dspace-backend.ub.uni-siegen.de/server/api/core/bitstreams/1e658634-a368-49e9-93b2-4491e750edb8/content).
2. **Temporal graph prediction and graph explanations for T1D are published.**
   Sarwar et al.’s 2026 JAMIA GAT-BiGRU represents multimodal CGM time points
   as nodes in a temporal k-neighborhood graph, predicts glucose and
   30/60-minute hypoglycemia risk, and reports GNNExplainer and retrospective
   counterfactual recommendations, evaluated on OhioT1DM and BrisT1D. Its
   publisher abstract is available; fine-grained details beyond that inspected
   abstract should not be inferred here. [Publisher record](https://doi.org/10.1093/jamia/ocag104).
3. **Physiology graphs and graph-structure diagnostics are prior work.**
   Sarwar et al.’s 2026 SysCon author manuscript describes a modality-node
   physiology graph for glucose forecasting and hypoglycemia risk with
   ablation and explanation analyses. It was inspected through an author
   upload because the IEEE full text was not retrievable in the audit; exact
   version and split details remain to be checked. [Author-uploaded manuscript](https://www.researchgate.net/publication/404642556_Explainable_Multitask_Graph_Network_for_Blood_Glucose_Forecasting_and_Hypoglycemia_Risk_Classification).
4. **Multimodal event features and temporal alignment are not new.** The 2026
   MT-HypoNet paper uses CGM, insulin and carbohydrate inputs aligned to a
   five-minute grid, represents meals/boluses as event covariates and sums
   multiple same-bin events; it reports retrospective Loop validation plus
   external datasets and prospective T2D assessment. It is not a graph or a
   matched event-relation study, but it rules out novelty based merely on
   combining CGM with timestamped insulin/meal context or using Loop at scale.
   [Primary full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC13019577/),
   [publisher record](https://doi.org/10.1016/j.isci.2026.115294).
5. **Physiological explanation is also an active comparator space.** The 2026
   PhyNet study imposes monotonic physiological constraints on T1D glucose
   forecasting and evaluates physiological consistency and counterfactuals.
   Our deletion sample does not support a broader explanation or safety claim.
   [PubMed record](https://pubmed.ncbi.nlm.nih.gov/42685163/).

This is a targeted, source-linked literature update, not a systematic review
or proof that no exact equivalent exists. See the [primary-source prior-art
update](primary_prior_art_update_2026_10_29.md) for the focused source check
and explicit JAMIA access limits. Search queries and remaining access
limitations are recorded in [`literature_search_log.md`](literature_search_log.md).

## Paper-safe contribution statement

> We report development-stage comparisons of temporal insulin/meal-event
> models on identical patient-specific Loop prediction windows. A generic
> event-to-CGM graph outperformed a late-fusion event-sequence implementation
> in ten one-epoch fold-seed fits. In two-epoch comparisons against an exactly
> parameter-matched, time-aligned pooling control, pooling had higher AP in all
> five folds at each of two seeds and lower Brier in every second-seed fold.
> Averaged within participant across seeds, graph-minus-control AP was −0.009900
> (95% fixed-prediction participant interval [−0.010477, −0.009345]) and
> macro-Brier was +0.0001264 ([+0.0001096, +0.0001429]). These findings are
> specific to the tested cohort, models and training schedule; they do not
> establish general graph failure, clinical relation validity or utility. The
> locked final-performance and external cohorts have not been evaluated.

This can support a transparent empirical comparison if the paper makes its
limits central. It cannot support a claim that knowledge-graph relations
improve prediction in general.

## Remaining work before a novelty claim is submission-ready

1. **Completed: two-seed aligned-control replication.** All five folds at seed
   `20261030` passed strict audits with one frozen source digest. The
   participant-level, two-seed summary is linked above. This does not settle
   convergence, stronger baselines, event availability, independent-cohort
   validation, or clinical utility.
2. Run a development-frozen multi-epoch learning-curve and tuning protocol for
   graph and comparator models. One epoch does not establish equal convergence.
3. Replicate the event-disabled graph control and the aligned control across
   the patient folds and prespecified seeds; do not count repeated participants
   or folds as independent cohorts.
4. Replace the selection-conditioned explanation screen with an attribution
   score independent of the perturbation evaluation, or a prespecified
   selection/evaluation split. Match random sets on recency and value, then
   test provenance and seek blinded clinical assessment before usability claims.
5. Quantify actual event availability if transaction/arrival times exist;
   otherwise freeze delayed-replay scenarios as simulations. Report calibration,
   episode-level sensitivity, false-alert burden and lead time before any
   clinical-use claim.
6. Finish the prior-art search against full supplements/methods where
   retrievable, report access limits, and harmonize the available Jaeb cohorts
   before calling any result external replication.
7. Freeze all choices before using the protected final holdout once. External
   replication should be a separate, harmonized study; the other local dataset
   folders have not generated results in this report.

## Verification ledger

The executable audit script
[`scripts/audit_novelty_evidence_bundle.py`](../scripts/audit_novelty_evidence_bundle.py)
checks paired archive hashes, complete local graph/sequence run metadata,
fold/seed/window identities, typed-routing and endpoint metric reconciliation,
event-age summary counts, and the aggregate explanation sample. The older v3
output predates the completed five-fold aligned-control comparison. The refreshed
five-fold aggregate-only output is
[`audit/novelty_evidence_bundle_20261031_v9.json`](../audit/novelty_evidence_bundle_20261031_v9.json).
It checks saved evidence; it does not rerun training or reconstruct all
participant bootstrap intervals from prediction shards.
