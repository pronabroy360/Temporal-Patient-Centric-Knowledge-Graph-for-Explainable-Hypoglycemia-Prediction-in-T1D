# Implementation status

Updated: 5 October 2026.

**Current gate:** the [controlled neural experiment specification](loop_controlled_neural_experiments.md)
supersedes historical next-step statements below. The [outer-0 first-gate
comparison](loop_controlled_first_gate_result_2026_10_05.md) has now run and its
bundle and paired predictions have been verified locally. The capacity-similar
CGM-only MLP outperformed the clean event GRU on this one-fold, one-seed
development gate. Graph-relation modeling, stronger full-CGM-history controls,
seed replications and the locked holdout remain pending. The ordered work is in
[next gates after the first gate](next_steps_after_controlled_first_gate.md).

**Correction status:** see [corrected pilot recovery](corrected_pilot_recovery.md).
Historical AP values below require recomputation; the shared tied-score AP
defect is fixed. Software tests do not establish scientific performance.

Software fixtures and Loop development pilots have run. Their historical AP results require corrected evaluation; graph and final holdout results do not yet exist.

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

The controlled sequence comparison has now trained and been paired on Loop development data. The planned learned graph model, full-CGM-history control, final calibration/alert evaluation, external replication, FHIR/RDF parsing and T1DEXI adapter remain unfinished. The graph representation is a deterministic candidate for the protocol, not a validated ontology or clinical decision-support system.

The Loop streaming adapter is covered by synthetic tests only. Release-backed window-index and event-alignment audits have since been completed.

The evaluation primitives and transparent smoke baselines are implemented and tested, and development pilots have been run on Loop records. Learned sequence/graph training and application of calibration, bootstrap uncertainty, and threshold selection remain pending empirical implementation and evaluation.

The CGM-only, captured-event summary, and individual-event sequence LOSO runners are exercised on the synthetic fixture. Their output is a software smoke result only; synthetic AP/Brier values are not study results.
