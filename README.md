# T1D temporal patient knowledge graph research

Status: proposal validation, public-release auditing, corrected CGM development benchmarking, and a verified controlled event-sequence first gate, updated October 2026. No locked-holdout or graph-relation result has been produced.

The project will test whether typed, time-aware patient-event relations improve advance prediction of CGM-defined hypoglycemia and the fidelity of explanations. Novelty and predictive benefit remain hypotheses.

The current framing is **When Do Temporal Patient Knowledge Graphs Help Hypoglycemia Prediction?** The contribution is a controlled study of individual clinical events, relations and information availability. Generic semantic/temporal graph architecture is established prior work.

Start with the new novelty package:

1. [Novelty assessment](docs/novelty_assessment.md): expanded closest-work comparison and claim boundaries.
2. [Refined proposal](docs/refined_proposal.md): research questions and intended contributions.
3. [Decisive experiments](docs/decisive_experiments.md): controls that separate timing, information, model size and relation effects.
4. [Search log](docs/literature_search_log.md): queries, version corrections and unresolved access limits.

Supporting working documents:

1. [Proposal validation](docs/proposal_validation.md): verified claims, missing prior work, methodological corrections, and evidence limits.
2. [Research protocol](docs/research_protocol.md): proposed labels, evaluation, models, statistical analysis, and leakage controls.
3. [Research plan](docs/research_plan.md): milestones and completion gates, with no fixed deadline.
4. [Data dictionary](docs/data_dictionary.md) and [graph schema](docs/graph_schema.md): initial implementation contracts, pending dataset inspection.
5. [Literature matrix](docs/literature_matrix.csv): 21 curated records with evidence/access flags; not a systematic review.
6. [Implementation status](docs/implementation_status.md): what is runnable now and what remains blocked on data access.
7. [Data access checklist](docs/data_access_checklist.md): the authorization register, pre-import controls, and first-release audit gate.
8. [Dataset fallback strategy](docs/dataset_fallback_strategy.md): OhioT1DM eligibility correction, alternative access routes, and the cohort selection gate.
9. [AIDE T1D release audit](docs/aide_t1d_release_audit.md): structural, CGM chronology and scope decision for the supplied public release.
10. [Dataset intake template](docs/dataset_intake_template.md): repeatable provenance, field-gate and release-audit record for each added dataset.
11. [Jaeb candidate screening](docs/jaeb_candidate_screening.md): file and participant-modality comparison of AIDE, Loop, DCLP3, DCLP5 and FLAIR.
12. [Loop release audit](docs/loop_release_audit.md): full raw field scan, chronology risks, units and upload-time validation gate.
13. [Loop upload-linkage audit](docs/loop_upload_linkage_audit.md): evidence that upload times cannot support the primary observed-latency claim.
14. [Loop canonicalization specification](docs/loop_canonicalization_spec.md): exact-duplicate keys, conflict handling and storage-safe transformation rules.
15. [Loop streaming adapter](docs/loop_streaming_adapter.md): line-by-line provenance-preserving event mapping without raw-data duplication.
16. [CGM range policy](docs/loop_cgm_range_policy.md): explicit primary and development sensitivity policies.
17. [Loop window-index generation](docs/loop_window_index_generation.md): storage-bounded protected metadata generation and validation commands.
18. [Loop window-index validation](docs/loop_window_index_validation.md): frozen primary CGM benchmark counts and partition digest.
19. [Loop event-to-window alignment](docs/loop_event_window_alignment.md): storage-bounded auxiliary-event coverage audit.
20. [Loop model split](docs/loop_model_split.md): development-only folds and locked final holdout design.
21. [Loop model split coverage](docs/loop_model_split_coverage.md): frozen-window balance across development folds and holdout.
22. [Loop CGM rule baseline](docs/loop_cgm_rule_baseline.md): first development-only release-backed empirical comparator.
23. [Development CGM rule result](docs/loop_cgm_rule_development_result.md): first empirical reference result, before learned modeling.
24. [Loop CGM logistic pilot](docs/loop_cgm_logistic_pilot.md): one-fold validation-only learned baseline runner.
25. [Matched CGM logistic validation result](docs/loop_cgm_logistic_outer0_validation_result.md): first matched learned-versus-rule development comparison.
26. [Kaggle training workflow](docs/kaggle_training.md): GPU training guidance and private feature-table notebook.
27. [Outer-0 CGM logistic test result](docs/loop_cgm_logistic_outer0_test_result.md): frozen-configuration internal development-test check.
28. [Five-fold CGM logistic development result](docs/loop_cgm_logistic_development_result.md): frozen development benchmark before event-aware modeling.
29. [Loop captured-event logistic pilot](docs/loop_event_logistic_pilot.md): matched development-only recorded-event comparator.
30. [Loop CGM development feature cache](docs/loop_cgm_feature_cache.md): one verified raw-data pass followed by reusable corrected pilot inputs.
31. [Corrected CGM validation](docs/loop_cgm_corrected_validation_result.md): repaired AP results and the renewed two-epoch selection.
32. [Loop CGM feature-cache result](docs/loop_cgm_feature_cache_result.md): verified release-backed development cache counts and checksums.
33. [Corrected five-fold CGM result](docs/loop_cgm_corrected_development_result.md): corrected development reference with explicit AP denominator.
34. [Recorded-event summary validation](docs/loop_event_summary_validation_result.md): matched negative result, paired uncertainty, and its restricted interpretation.
35. [Next research steps](docs/next_steps_after_event_summary.md): gated path from event-signal diagnostics through graph controls, holdout and external replication.
36. [Loop canonical event-instance cache](docs/loop_event_instance_cache.md): protected event contract for residual, sequence and graph comparisons.
37. [Frozen-CGM event residual pilot](docs/loop_event_residual_pilot.md): the next controlled event-signal diagnostic and its prespecified candidate grid.
38. [Frozen-CGM event residual result](docs/loop_event_residual_validation_result.md): completed negative ranking result and the retained individual-timing question.
39. [Controlled neural comparisons](docs/loop_controlled_neural_experiments.md): corrected inputs/checkpoint guards, CPU replay evidence, fixed comparison plan and a complete Kaggle notebook.
40. [Controlled neural first-gate result](docs/loop_controlled_first_gate_result_2026_10_05.md): recovered bundle, paired validation comparison, and interpretation limits.
41. [Next gates after the first gate](docs/next_steps_after_controlled_first_gate.md): optimization checks, full-CGM-history control, event ablations, replication and relation tests.
The fold manifest utility in `t1d_tkg.manifest` creates and validates the shared patient-disjoint split; `t1d_tkg.window_index` writes and validates compact metadata-only window indexes.

The [original startup handbook](T1D_Temporal_Patient_Centric_Knowledge_Graph_Research_Starter.md) remains the broader idea collection. The dated review and protocol supersede conflicting recommendations in that handbook. The protocol is a draft to refine on development data before freezing the evaluation.

## Run the software fixture

The current implementation has no third-party runtime dependency. From the project directory:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 scripts/audit_synthetic.py
```

The fixture intentionally includes a missing future, an ongoing low, an exact-70 boundary, a future event, and two patient IDs. It is a software check only; its audit numbers must never be reported as study results.

The audit also reports coverage bounds, longest CGM gap, duplicate timestamps, arrival-metadata categories, and confirmed low episode counts. If valid duplicate timestamps are found, it records the anomaly and blocks window counts until a release-specific duplicate policy is frozen.

The evaluation utilities are available through `t1d_tkg.metrics`, `t1d_tkg.episodes`, `t1d_tkg.baselines`, `t1d_tkg.evaluation`, `t1d_tkg.uncertainty`, and `t1d_tkg.calibration`. They implement the protocol's basic participant-level AP/Brier calculations, confirmed CGM episodes, refractory alerts, one-to-one episode matching, a transparent slope rule, fold-isolated CGM, captured-event summary, and individual-event sequence logistic smoke comparators, plus paired participant-cluster bootstrap intervals and fold-local calibration diagnostics for fixed predictions. They do not constitute model results until predictions from a fixed fold manifest are supplied.

Pass `include_predictions=True` to a LOSO runner to obtain participant-keyed out-of-fold labels and scores suitable for archiving and paired uncertainty analysis.

Pass the same `manifest` object to every LOSO runner to force all comparator folds to use the archived participant assignment.

Use `t1d_tkg.episodes.simulate_alerts` and `select_alert_threshold` on validation participants to apply the prespecified refractory and alert-burden rules before evaluating a frozen threshold on held-out participants.

The synthetic runner also exercises fixed-width typed, generic-relation, and no-relation graph summaries. These controls validate topology handling and fold isolation; they are not the planned learned temporal GNN and their synthetic scores are not study results.

The `t1d_tkg.explanations` helpers create prediction-time evidence records and remove selected nodes with their incident edges, preserving provenance for the later retention/deletion explanation tests.

`audit_dataset` includes a collection-validation report so duplicate IDs, timestamp ordering, unknown event types, availability assumptions, and missing provenance are visible before model preparation.

Run `PYTHONPATH=src python3 scripts/run_synthetic_benchmark.py --output /tmp/t1d-synthetic-artifact.json` to produce a complete software artifact with the audit, manifest checksum, baseline outputs, out-of-fold predictions, and paired bootstrap contrast.

`validate_prediction_archive` checks that every archived model covers exactly the manifest participants with aligned binary labels and bounded probabilities.

`DEFAULT_CONFIG` in `t1d_tkg.config` records the benchmark contract (history, horizons, grid, threshold, recovery, missingness, refractory period, and alert budget) and is embedded in the synthetic artifact.

The package accepts canonical `Event` objects. The OhioT1DM adapter follows the published XML block layout, but it has not yet been validated against the authorized release. The researcher cannot request OhioT1DM directly under the reported DUA eligibility rule; use this adapter only if an eligible supervising advisor obtains access. After access, inspect the actual XML semantics and run the audit before using any model.

For a release-backed run, generate the metadata-only window index after the
range policy decision, then validate it against the shared fold manifest:

```bash
PYTHONPATH=src python3 scripts/validate_window_index.py \
  private/loop_window_index.jsonl \
  --manifest private/loop_loso_manifest.json \
  --output audit/loop_window_index_validation.json
```

The validator checks row schema, timestamp and label invariants, duplicate
sample IDs, and patient-fold consistency before model execution.

An OhioT1DM-style XML adapter is now available for that step. It requires an explicit timezone because the documented XML timestamps are timezone-naive:

```bash
PYTHONPATH=src python3 scripts/audit_ohio.py /path/to/ohiot1dm --split training --timezone Region/City
```

Add `--output audit.json --manifest-output folds.json` to persist the report and generate the shared fold manifest with its checksum.

It has been tested on a synthetic XML fixture, not on the restricted release.

Loop's canonicalization, temporal eligibility, episode, auxiliary coverage, range, frozen window index and protected split layers are implemented and tested. Corrected CGM development benchmarking is complete. The first recorded-event summary comparator underperformed CGM and has been stopped; event residual and individual-event timing diagnostics come before graph testing. Upload linkage failed the observed availability-time gate, and the locked holdout remains excluded from predictive evaluation. Loop is the provisional primary cohort; DCLP3 and DCLP5 are insulin–CGM replication candidates, while AIDE and FLAIR support CGM/treatment-context analyses.
