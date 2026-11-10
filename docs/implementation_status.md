# Implementation status

Updated: 31 October 2026. This current summary supersedes older dated status
notes below; those entries remain as a chronological audit trail.

## Current research evidence snapshot

- The primary current novelty synthesis is the [31 October evidence report](novelty_evidence_report_2026_10_31.md), with source-by-source claims in the [primary-source check](primary_source_novelty_check_2026_10_31.md). Hüni's University of Bern thesis now supplies full methods for the related CGM-only visibility-graph/LSTM precedent, including the 120-minute/30-minute any-low task; the thesis is within-person chronological validation, not a patient-disjoint event-graph comparison. Do not assume the final Springer chapter is identical.
- The graph-generic model beat the exactly parameter-count matched late-fusion event-sequence model in two seeds × five folds at one epoch. This does not isolate graph topology because alignment, fusion and computation differ.
- The stricter exactly parameter-matched graph versus time-aligned pooling comparison is complete in two seeds × five folds at two epochs. Pooling had higher participant-macro AP in all ten fits; Brier favored pooling in nine. A further eight-epoch CPU outer-0 pair at one seed slightly favored pooling, with a much smaller gap. The eight-epoch check is not convergence evidence.
- Modality-typed routing is mixed and has no consistent advantage over generic routing. Nearest-versus-second-nearest endpoint and event-age reassignment screens show small, bounded sensitivities. A new two-epoch graph event-input comparison (outer-0, seed 20261031) slightly favored the event-disabled branch on AP and Brier, updating the earlier one-fold, one-seed, one-epoch event-enabled result in the opposite direction. This is still only one fold and seed; zeroing the event input also removes gradients to the event encoder and edge experts, so parameter counts match but effective capacity does not. A separate recovered two-epoch full-history sequence ablation (outer-0, seed 20261003) also favored event-zero over event-enabled; it is not a graph replication, and archived metadata lacks an explicit locked-holdout-use field.
- Five frozen CGM-only Loop logistic models transferred without refitting to DCLP3/DCLP5 and beat persistence on the tested release-specific CGM targets. This is not external event-model or graph validation. Timestamp semantics remain unresolved.
- The locked 183-person group remains unopened. Event availability is retrospective occurrence-time replay with immediate availability assumed, not measured. No clinical utility, validated clinical relation ontology, or faithful clinical explanation is established.

The highest-priority empirical gaps are multi-fold/multi-seed event-disabled
and relation controls, broader optimization uncertainty, independent
explanation-fidelity assessment, measured or simulated availability, and
harmonized external event-model validation. The default system Python has no
PyTorch; the isolated local environment has CPU-only PyTorch and was used for
the new two-epoch ablation. The user's active Kaggle session has been left
untouched.
Do not start another long training job until that session is available or a
separate runtime is explicitly in use.

**Event-time reassignment screen, 29 October 2026:** outer-0, seed `20261005`,
was evaluated from the saved epoch-1 graph checkpoint. Rotating event ages
within each window preserved event and age multisets but broke event-time
pairing. Original-minus-reassigned participant-macro AP was +0.000257 (95%
paired participant interval [+0.000128, +0.000393]); macro-Brier difference
was +0.00000214 (interval [−0.00000085, +0.00000505], includes zero). The
unperturbed checkpoint replay matched the saved AP/Brier and exact prediction
window identity to tight tolerances. This is a small fixed-checkpoint ranking
sensitivity, not evidence of clinically valid relations or generalizable
benefit. The original source digest cannot be reproduced from the current
workspace, so exact source reproduction is not claimed. The same diagnostic
is complete on all five outer folds at seed `20261005` and replicated at seed
`20261004`. Original pairing has higher AP in all 10 seed-fold fits (mean
delta +0.0001118), though only 3/10 fold-specific intervals exclude zero.
Macro-Brier direction is split evenly, with 4/10 intervals excluding zero.
The same 652 people recur across seeds, so these fold-specific results are not
independent and their intervals are not pooled. Next assess explanation
faithfulness. See the [control report](loop_event_age_reassignment_control.md),
[two-seed summary](../audit/loop_event_age_reassignment_two_seed_five_fold_summary_20261029.json),
and [seed summaries](../audit/loop_event_age_reassignment_seed20261005_five_fold_summary_20261028.json).

**Modality-routing replication update:** a matched one-epoch `graph-typed`
versus `graph-generic` comparison is complete across all five development
folds for seed `20261004`. Both variants have 36,883 parameters and their
paired validation windows and input contracts match. Typed minus generic
participant-macro AP is negative in three folds and positive in two; the
unweighted fold mean is −0.000476. Macro-Brier differences are mixed as well.
Treat this as a mixed result for modality-derived expert routing, not evidence
for or against clinically meaningful KG relations. See the [five-fold
summary](../audit/loop_relation_typed_vs_generic_seed20261004_five_fold_summary_20261020.json)
and the [relation pilot record](loop_temporal_relation_pilot.md). The
outer-0 matched event-disabled graph comparison has now been repeated at two
epochs under seed `20261031`, with a small difference favoring event-disabled.
The result remains one fold/seed and does not overcome the effective-capacity
limitation. Fold/seed replication, event-order controls, and a prespecified
explanation-faithfulness assessment remain. The locked holdout remains sealed.

**Event-input ablation update, 25 October 2026:** on outer-0, seed `20261004`,
the generic temporal graph exceeded the event-disabled branch by +0.002800
participant-macro AP (10,000-draw paired participant interval [+0.001996,
+0.003609]) and had −0.0002003 macro-Brier difference (interval [−0.0002411,
−0.0001597]). The 36,883-parameter runs matched source, inputs, split,
optimizer, prediction windows, and identity checks. This is preliminary
single-fold evidence for recorded-event input value. Because disabling events
also leaves event modules without gradients, it does not match effective
capacity and does not isolate relation semantics. Replicate on additional
folds/seeds and run a causal endpoint-perturbation control. See the
[event-ablation report](loop_event_ablation_result_2026_10_25.md) and
[paired audit](../audit/loop_relation_event_ablation_outer0_seed20261004_paired_20261025.json).

**Two-epoch graph event-input follow-up, 31 October 2026:** a fresh outer-0
fit at seed `20261031` used the same 2-epoch schedule, optimizer, training
membership, frozen input digest, 36,883 declared parameters, and validation
windows in the generic graph and event-disabled branches. Graph-minus-disabled
participant-macro AP was −0.002278 (95% paired fixed-prediction participant
interval [−0.003334, −0.001218]); macro-Brier difference was +0.00007086
([+0.00004314, +0.00010078]), also favoring event-disabled. The metrics cover
130 participants and 8,885,621 windows; both run records declare that the
locked holdout was not used. This reverses the direction of the one-epoch
seed-20261004 result, demonstrating schedule/seed dependence rather than a
stable event-input benefit. It does not isolate relation semantics: disabling
events removes event-derived information and the gradients to event modules,
so equal parameter count is not equal effective capacity. The interval
conditions on these two fitted models and is not fit/seed uncertainty. See the
[paired audit](../audit/loop_graph_event_ablation_outer0_seed20261031_paired_20261031.json).

**Causal endpoint-perturbation update, 26 October 2026:** the nearest-observed-
later-CGM endpoint was compared with the second-nearest such endpoint (fallback
to nearest when only one admissible target exists) across outer-0 through
outer-4, seed `20261004`, one epoch per arm. Inputs, participant split within
each pair, optimizer, parameter count (36,883), source digest, and prediction
windows matched and passed identity checks. Nearest-minus-second-nearest AP
differences were −0.000631, +0.006681, −0.000183, +0.001618, and +0.004350;
nearest had higher AP in three folds and second-nearest in two. Macro-Brier
differences were +0.0000509, −0.0002618, −0.0000686, −0.0000571, and
−0.0001664; nearest had lower Brier in four folds. The descriptive means
(+0.002367 AP and −0.0001006 macro Brier) do not capture training-seed or
cohort uncertainty and do not establish a reliable relation benefit. Replicate
with another seed; event-order controls and explanation-faithfulness
evaluation also remain. See the [endpoint report](loop_endpoint_perturbation_result_2026_10_25.md),
[five-fold summary](../audit/loop_relation_endpoint_perturbation_seed20261004_five_fold_summary_20261026.json),
[outer-4 paired audit](../audit/loop_relation_endpoint_perturbation_outer4_seed20261004_paired_20261026.json),
[four-fold summary](../audit/loop_relation_endpoint_perturbation_seed20261004_four_fold_summary_20261026.json),
and the [outer-0 paired audit](../audit/loop_relation_endpoint_perturbation_outer0_seed20261004_paired_20261025.json). The second-seed replication (`20261005`) is complete on all five folds with matched generic/endpoint-shifted prediction identities. Its nearest-minus-second-nearest AP differences are +0.001615, +0.003555, +0.001039, +0.001413, and +0.000907 (outer-2 interval includes zero); macro-Brier differences are +0.0000189, −0.0001642, −0.0000620, −0.0000215, and −0.0000179 (outer-4 interval includes zero). AP favors nearest on 5/5 folds and Brier on 4/5. Across both seeds, nearest favors AP and Brier in 8/10 seed-fold pairs. A participant-cluster bootstrap averaging paired differences over both fixed seeds gives +0.002097 AP (95% interval +0.001761 to +0.002443) and −0.0000773 macro-Brier (−0.0000957 to −0.0000594). This remains endpoint sensitivity, not a relation-benefit or novelty claim; intervals condition on two fixed seeds and do not estimate a broader training-seed distribution. See the [seed-20261005 five-fold summary](../audit/loop_relation_endpoint_perturbation_seed20261005_five_fold_summary_20261028.json), [combined two-seed summary](../audit/loop_relation_endpoint_perturbation_two_seed_five_fold_summary_20261028.json), [participant-cluster bootstrap](../audit/loop_relation_endpoint_perturbation_two_seed_participant_cluster_bootstrap_20261028.json), and [outer-4 paired audit](../audit/loop_relation_endpoint_perturbation_outer4_seed20261005_paired_20261028.json).

**Initial Kaggle evidence gate:** on 19 October, the first exact-capacity graph-versus-non-graph comparison completed for outer-0, seed 20261003, one epoch. Graph-generic achieved AP 0.474481 and participant-macro Brier 0.021522; the non-graph history/event sequence model with the same 36,883 parameters achieved AP 0.389901 and Brier 0.024211. The paired AP difference was +0.084580 (10,000-draw 95% participant-bootstrap interval [+0.078104, +0.090816]); graph AP was higher for 126/130 participants. The macro Brier difference was −0.002690 (10,000-draw 95% interval [−0.003043, −0.002347]); graph Brier was lower for all 130. This was the screening result that motivated the local MPS cross-fold comparison; intervals condition on fixed predictions. See the [matched control result](loop_non_graph_capacity_matched_control.md), [paired audit](../audit/loop_graph_vs_capacity_matched_outer0_paired.json), and [10,000-draw sensitivity audit](../audit/loop_graph_vs_capacity_matched_outer0_paired_10000draws_20261019.json).

**Cross-hardware check:** the same graph-versus-sequence direction was reproduced by fresh one-epoch M4 MPS fits on the same fold and seed: AP 0.475384 vs 0.394764 (paired difference +0.080620; interval [+0.071498, +0.089245]) and macro Brier 0.021945 vs 0.023899 (difference −0.001953; interval [−0.002211, −0.001708]). All 130 participants and 8,885,621 windows passed prediction-identity checks. This is a hardware robustness check, not independent fold/seed replication. See the [MPS paired audit](../audit/loop_mps_outer0_graph_vs_sequence_paired_20261019.json).

The 18 October full-text review of the SysCon 2026 author manuscript further narrows the candidate novelty: multimodal physiology graphs, typed insulin/carbohydrate/activity relations, and graph edge-faithfulness tests are established prior work. Individual timestamped event instances versus modality summaries/sequences remains a provisional empirical distinction; the paper cannot claim a novel KG architecture or global first. See the [full prior-work review](syscon_2026_prior_work_review.md).

A further 19 October primary-source check found a 2024 patient-centric diabetes PHKG/digital-twin paper, a Helmut-Schmidt-Universität project page (updated August 2026) describing a semantic T1D graph with short-term hypoglycemia-onset prediction, personalized short-horizon T1D risk models, patient-wise hour-ahead multimodal hypoglycemia prediction, and a 2026 T1-DEXI event-input/LSTM study. This substantially closes the door on broad conceptual claims; the HSU source is an ongoing project description, not a completed performance report. The first modality-typed versus generic-edge experiment does not favor typed routing; the direct graph-versus-capacity-matched sequence result supplies preliminary evidence for graph message passing in this particular setup. Whether individual-event relation structure adds reproducible value remains unresolved. See the [focused prior-work addendum](closest_prior_work_event_graph_addendum_2026_10_19.md), [novelty report](novelty_evidence_report_2026_10_17.md), [assessment](novelty_assessment.md), and [literature log](literature_search_log.md).

The non-graph dual-GRU control with exactly 36,883 parameters is now trained and compared. The trainer's smoke test enforces the instantiated parameter count on a GPU; local regression tests check the parameter formula and reporting contract. The local MPS campaign has completed graph-generic and parameter-matched sequence pairs on all five development folds for two seeds and one epoch. Outer-0 event-disabled and causal endpoint-perturbation checks are also complete. The event-age reassignment screen and one sampled event-set deletion/retention diagnostic are complete; broader independent explanation-fidelity evaluation remains open.

**Current compute availability check — 19 October 2026, 01:42 UTC:** the Kaggle controlled-comparison notebook showed Draft Session off, 0 Active Events, and a near-exhausted GPU quota warning; the full-history input and runner datasets remain attached. The existing Colab tab is the earlier CGM-only MLP versus clean-GRU seed notebook, not the full-history graph-versus-sequence campaign; its visible output reports the staged input paths absent and the page says it is connecting to a runtime. No remote training was started or stopped. Thus the outer-1 comparison remains incomplete, and there is currently no verified compute session for the prespecified cross-fold/seed campaign. The user’s prior instruction was to leave any live Kaggle work running; the fresh view showed none running.

**Subsequent local MPS completion:** after that timestamped availability check, the five-fold paired comparison completed locally on seed 20261003. Do not interpret the older Kaggle/Colab availability snapshot as the current campaign status. The [five-fold audit aggregate](../audit/loop_mps_graph_vs_sequence_five_fold_summary_20261019.json) records paired prediction identity and foldwise metrics; no locked-holdout data were used.

**Historical first-gate record:** the [outer-0 comparison](loop_controlled_first_gate_result_2026_10_05.md)
found that the CGM-only MLP outperformed the clean event GRU on one fold and one
seed. The stronger full-CGM-history comparison has since been run; see the
 latest evidence gate above. The ordered work now starts with event-information
 and graph-representation controls, followed by multi-seed/fold evaluation.

**Correction status:** see [corrected pilot recovery](corrected_pilot_recovery.md).
Historical AP values below require recomputation; the shared tied-score AP
defect is fixed. Software tests do not establish scientific performance.

**Relation-experiment implementation and result:** the matched generic-edge vs
modality-typed trainer and strict paired comparator completed on Kaggle. The
T4×2 CUDA smoke test passed both variants at 36,883 parameters. The corrected
run metadata includes `hidden`, required by the checkpoint contract; both
archives passed strict input/split/prediction-window checks. The original
generic-versus-typed pair bundle remains in Kaggle working storage and its
SHA-256 is recorded in the
[audit receipt](../audit/loop_temporal_relation_outer0_paired_pilot.json); that
specific two-model bundle has not been copied into this project. This is a one-epoch pilot only. The
event-derived relation labels do not represent new clinical facts, and a
non-graph model with matched information and capacity has now been evaluated;
both raw archives and predictions are locally preserved in the ignored
`private/kaggle_artifacts/loop_graph_vs_capacity_matched_outer0_20261019/`
directory.

Software fixtures and Loop development pilots have run. Historical AP results require corrected evaluation. The graph-generic versus parameter-matched sequence comparison now has paired development results across all five patient-disjoint outer folds for two seeds. Semantic relation interpretation, multi-epoch stability, independent multi-fold explanation-fidelity evaluation, external validation, and the final locked-holdout evaluation remain incomplete.

Implemented in `src/t1d_tkg`:

- `Event`: timezone-aware canonical events with occurrence and optional availability time.
- `build_prediction_windows`: protocol-aligned `(t−120,t]` histories, recovery eligibility, unknown labels for incomplete future coverage, exact threshold handling, and as-of filtering of historical inputs.
- `build_asof_graph`: deterministic patient-scoped event graph with typed ownership, temporal and prior-event relations. Future events, unavailable records and outcome nodes are excluded.
- `audit_dataset`: machine-readable participant summary for the first data audit, including coverage dates, longest CGM gap, duplicate timestamps, arrival-metadata categories, and confirmed low episode counts. Duplicate timestamps are surfaced and block window counts until a release-specific resolution policy is frozen.
- `synthetic_events`: deterministic fixture containing two patients, low glucose, missing future follow-up, delayed availability and a future event.
- `ohio`: conservative parser for the documented OhioT1DM XML blocks; it requires an explicit timezone and preserves source attributes.
- `scripts/audit_ohio.py`: release audit runner that records per-file parse errors instead of silently dropping malformed files.
- The Ohio audit runner can persist its JSON report and generate a checksummed LOSO manifest from successfully parsed participants.
- `metrics`, `episodes`, and `baselines`: dependency-free AP/Brier summaries, confirmed-episode matching, refractory alerts, and a persistence/slope reference score.
- `features`, `multimodal`, `event_sequence`, `logistic`, and `evaluation`: CGM-only summaries, matched captured-event summaries, an individual-event sequence encoding, a small transparent logistic smoke model, and fold-isolated LOSO evaluation for the first benchmark.
- `graph_features`: fixed-width as-of graph summaries with typed, generic-relation, and no-relation controls, plus a LOSO logistic smoke runner. This is a topology control, not the planned learned temporal GNN.
- `uncertainty`: deterministic paired participant-cluster bootstrap for AP or Brier contrasts on fixed out-of-fold predictions, retaining undefined AP replicates.
- `calibration`: fold-local Platt scaling plus equal-width reliability bins and expected calibration error.
- `episodes`: deterministic score-to-alert simulation and validation-only threshold selection under the configured unmatched-alert budget.
- `manifest`: deterministic patient-disjoint LOSO fold manifests with structural validation, JSON round-tripping, and canonical SHA-256 checksums.
- `explanations`: provenance records tied to admissible graph nodes and edge-closed evidence-removal masks for later fidelity experiments.
- `validation`: collection-level preflight checks for duplicate IDs/timestamps, ordering anomalies, unsupported types, availability assumptions, and missing provenance.
- `scripts/run_synthetic_benchmark.py`: end-to-end synthetic artifact containing audit, fold manifest/checksum, baseline metrics, out-of-fold predictions, and paired bootstrap output.
- `archive`: prediction-archive validation against the fold manifest, including participant coverage, label/score lengths, binary labels, and probability bounds.
- `config`: versioned benchmark parameter object recorded in the end-to-end artifact.
- `loop_adapter`: provenance-preserving Loop row mapper plus a line-by-line table iterator with optional protected participant filtering; no implicit deduplication or sorting.
- `window_index`: compact JSONL serialization/streaming reader for window metadata, with fold assignment, count reconciliation and exact-byte SHA-256.
- `scripts/validate_window_index.py`: pre-model validation gate for required metadata, binary/unknown label consistency, timestamps, and protected fold assignments.
- `range_policy`: explicit numeric-retention policy registry and streaming CGM filter for the unfiltered primary analysis and two bounded development sensitivities; no cutoff is silently applied.
- Both modules are exported from `t1d_tkg` so audit and modeling scripts share one public implementation.
- `manifest.fold_by_patient` derives deterministic per-patient test-fold assignments for window-index records.
- `scripts/validate_window_index.py --manifest ...` enforces those assignments before modeling.
- The same validator reports and optionally verifies the index file's exact SHA-256 digest.
- The Loop partitioned CGM audit can now emit protected gzip-compressed window-index partitions during its existing canonicalization pass; directory validation reports aggregate counts and a digest over partition digests.
- The primary Loop CGM window index is generated and validated; model-fold assignment and auxiliary-event coverage audits are complete.
- `scripts/audit_loop_window_event_alignment.py` is ready to measure canonical basal, bolus, or food coverage within the frozen 120-minute window histories without emitting event payloads.
- The completed overlap audit establishes a 12,771,176-window all-three-modality sensitivity cohort; primary captured-event comparisons retain all frozen windows with explicit missing-record handling.
- A protected five-fold development manifest is frozen for model selection; 183 participants remain locked for the final test.
- The historical pre-correction rule AP was 0.2252. Corrected five-fold rule AP is 0.209095 over 650 AP-defined participants; use the corrected result below.
- A storage-bounded, validation-only runner is ready for the captured-event logistic comparator. It uses rolling as-of event summaries and preserves explicit missing-record semantics; no event-aware model has been evaluated on the locked holdout.
- Historical pre-correction outer-0 and five-fold AP reports are retained for provenance and superseded by corrected results.
- A protected, development-only CGM feature-cache builder now verifies exact ordered window timestamps and labels against the frozen index. Cached and raw pilot paths match on the synthetic release. Historical release-backed AP values still require corrected reruns.
- The release-backed cache is complete: 64 partitions, 44,028,064 windows, 1,296,297 positives, and 652 development participants. Its manifest and window-identity hashes match corrected validation. Corrected five-fold development-test evaluation is next.
- Corrected five-fold CGM development evaluation is complete: participant-macro AP 0.446938 and pooled Brier 0.021590 for logistic, versus AP 0.209095 and Brier 0.055132 for the rule. AP is defined for 650 of 652 participants. The locked holdout remains excluded from predictive evaluation.
- The recorded-event runner can now reuse the verified CGM cache, eliminating CGM partitioning and sorting while retaining the raw/cache equivalence test. It still partitions basal, bolus, and food records for each run.
- Outer-0 recorded-event summary validation is complete and negative relative to matched CGM logistic: AP 0.425768 versus 0.457055, paired difference −0.031288 with participant-bootstrap interval [−0.037799, −0.025438]. The subsequent prespecified frozen-CGM event residual was also negative for ranking: selected AP 0.444091 versus 0.457055, paired difference −0.012965 with interval [−0.015520, −0.010363], despite lower Brier. Both are stopped before development-test or holdout evaluation; individual-event timing is the next diagnostic. See [residual result](loop_event_residual_validation_result.md).
- The recovered outer-0 64-event GRU validation is complete and exactly paired to the selected CGM logistic on 130 participants and 8,885,621 windows. Participant-macro AP is 0.471797 versus 0.457055, a difference of +0.014742 with paired-participant interval [+0.012150, +0.017206]. Pooled Brier is 0.021107 versus 0.022880. This is positive sequence-model development evidence under assumed immediate event availability; it does not isolate event information from neural-model capacity and does not establish graph-relation value. See [GRU validation](loop_gru_completed_validation.md).
- The subsequent capacity-similar first gate reverses the apparent advantage: CGM-only MLP participant-macro AP is 0.481604 versus 0.469331 for clean event GRU on exactly paired outer-0 windows. The recovered archive and predictions independently reproduce both reports. This supersedes any claim that the earlier logistic comparison isolated event benefit. See [controlled neural first-gate result](loop_controlled_first_gate_result_2026_10_05.md).
- LOSO runners accept `include_predictions=True` to archive participant-keyed out-of-fold labels and scores for paired uncertainty analysis.
- LOSO runners also accept a validated manifest, ensuring every comparator uses the archived participant assignment.

The test suite currently checks:

- incomplete futures remain `unknown`;
- current/recent lows are ineligible for the advance-warning task;
- exactly 70 mg/dL is not below the threshold;
- delayed future observations can define retrospective labels without becoming inputs;
- unknown or late records are excluded from as-of graphs;
- graphs are patient-scoped and edge references are closed.
- the individual-event sequence encoding retains only the most recent as-of events and excludes future or late-arriving records.
- fold manifests can be saved and validated before model training; the synthetic writer demonstrates the archival format.
- evidence records reject nodes outside the prediction-time graph and preserve source record IDs for traceability.
- dataset audits include the collection validation report before participant summaries are generated.

Validation command:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 scripts/audit_synthetic.py
PYTHONPATH=src python3 scripts/baseline_multimodal_synthetic.py
PYTHONPATH=src python3 scripts/write_synthetic_manifest.py /tmp/t1d-folds.json
PYTHONPATH=src python3 scripts/run_synthetic_benchmark.py --output /tmp/t1d-synthetic-artifact.json
```

## Known limitations

The adapter is implemented against the published block/attribute layout, but it is not yet validated against an authorized release. Its field semantics, duplicate policy, clock behavior and record-arrival metadata must be verified from the actual release. The synthetic fixture uses `assumed_immediate` availability and is not evidence about real logging behavior. In particular, the timezone, exact missing-value spellings, duplicate records, event clock semantics and whether any transaction-time metadata exists still require a real-file audit. Run it only after access:

```bash
PYTHONPATH=src python3 scripts/audit_ohio.py /path/to/ohiot1dm --split training --timezone Region/City
```

The `--timezone` argument is required because the documented XML timestamps do not carry an offset. Choose it from the release documentation or institutional data agreement; do not accept the default UTC assumption without recording that decision.

The full-CGM-history controls and learned temporal graph pilots have now been trained and paired on Loop development data, including an exact-parameter-count non-graph comparator. Current relation-control results and their limits are consolidated in the 31 October evidence report linked above. Independent explanation-fidelity evaluation, measured event availability, calibration/alert evaluation, external event-model validation, FHIR/RDF parsing and the T1DEXI adapter remain unfinished. The graph encoder remains an experimental research model, not a validated ontology or clinical decision-support system.

The Loop streaming adapter is covered by synthetic tests only. Release-backed window-index and event-alignment audits have since been completed.

The evaluation primitives, transparent smoke baselines, and development-only learned sequence/graph pilots have run on Loop records. Broader explanation-fidelity evaluation, external validation, calibration/alert-threshold application, and locked-holdout evaluation remain outstanding.

The CGM-only, captured-event summary, and individual-event sequence LOSO runners are exercised on the synthetic fixture. Their output is a software smoke result only; synthetic AP/Brier values are not study results.

Historical one-epoch MPS graph-versus-late-fusion-sequence comparison has
identity-verified paired results on all five patient-disjoint outer folds for
two seeds (`20261003` and `20261004`).
Graph-minus-sequence participant-macro AP is positive in all ten fold-seed
pairs, and macro-Brier differences are negative in all ten. Descriptive
five-fold mean AP differences are +0.086532 for seed `20261003` and +0.086575
for seed `20261004`; mean macro-Brier differences are −0.002113 and −0.002220.
All fits use one epoch and 36,883 trainable parameters per model. This supports
the tested graph-generic implementation over the tested capacity-matched
sequence comparator on Loop development folds, but does not isolate graph
topology or clinical relation semantics because the architectures differ in
other ways. Participant bootstrap intervals condition on each fitted model's
fixed predictions and do not provide uncertainty across seeds or studies.
Later results show that the stricter time-aligned pooling control reverses the
AP direction at two epochs across two seeds and five folds, and an eight-epoch
outer-0 schedule check slightly favors pooling. Replicated event-disabled
controls and independent explanation-fidelity tests remain outstanding. A
single sampled deletion/retention sensitivity audit is documented in
[`loop_graph_event_explanation_faithfulness.md`](loop_graph_event_explanation_faithfulness.md).
The locked holdout remains sealed. See the [historical two-seed/five-fold
summary](../audit/loop_mps_graph_sequence_two_seed_five_fold_summary_20261020.json)
and the [current novelty evidence report](novelty_evidence_report_2026_10_31.md).
