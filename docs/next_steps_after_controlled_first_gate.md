# Next gates after the first matched graph comparison

Updated: 31 October 2026. This is a **development-stage** plan informed by
the completed two-seed, five-fold graph-versus-time-aligned-pooling
comparison, earlier epoch-1 checkpoint replay, and prior controlled studies.
It is not a retroactive preregistration. The locked holdout remains untouched.

The second-seed replication of the stricter time-aligned pooling comparison
is complete. The five folds used two epochs per arm and one frozen source
digest (`a4d1a91916a675024110e1c30d54546c3aa0d51724480dfdbcdbb141dea71648`).
Strict paired audits passed on all five folds. Pooling led participant-macro
AP and Brier in each fold. Recomputed over all 652 disjoint development
participants and 44,028,064 windows, graph-minus-control AP was −0.012193
(95% fixed-prediction participant interval [−0.012935, −0.011445]) over 650
AP-defined participants; macro-Brier was +0.0001728
([+0.0001554, +0.0001894]). Pooling had higher AP for 632 participants
(graph for 18) and lower Brier for 567 (graph for 85). The machine-readable
aggregate is `audit/loop_graph_vs_aligned_nongraph_seed20261030_five_fold_summary.json`.
As specified in the protocol, a second participant-level summary averages
each person's paired differences across both seeds before bootstrap. It gives
graph-minus-control AP −0.009900 (95% fixed-prediction participant interval
[−0.010477, −0.009345]) over 650 AP-defined participants and macro-Brier
+0.0001264 ([+0.0001096, +0.0001429]) over 652. Pooling led AP for 639
participants and Brier for 528. This summary is
`audit/loop_graph_vs_aligned_nongraph_two_seed_five_fold_participant_summary.json`.
The intervals condition on the two fitted seeds and the same participant folds;
they do not estimate seed or cohort uncertainty. This completes the prescribed
two-seed comparison, not the broader validation package.
Byte-identical epoch-1 and epoch-2 checkpoints and run-metadata snapshots for
the aligned arm are stored under
`private/loop_seed20261030_recovery/outer0_aligned_nongraph_epoch1/` and
`private/loop_seed20261030_recovery/outer0_aligned_nongraph_epoch2/`; their
checkpoint SHA-256 values are `e8d92e287f144e86e507f97078a7a51be62efd0591081fc562f914b2d3494ef3`
and `d8fd972782d8f6180a6c29463d983ae8ff666a9670bf81debf10770d924413ed`.
Byte-identical graph recovery copies and run-metadata snapshots are stored under
`private/loop_seed20261030_recovery/outer0_graph_epoch1/` and
`private/loop_seed20261030_recovery/outer0_graph_epoch2/`. Checkpoint SHA-256
values are `b3ced144cc2449e295194d82ad6a2f6fccf0ab2c11b5699f67ad0a240cc31473`
and `827750d75d2888f8682cc7c93c676307cebfc6cf958d2bfa41465342d1b6bd8a`,
respectively. The locked holdout is excluded.

Outer-1 `graph-generic` at seed `20261030` completed both epochs and its
development validation replay. Its epoch-1 checkpoint is backed up at
`private/loop_seed20261030_recovery/outer1_graph_generic_epoch1/` with SHA-256
`ebb03036e851f5d46f9634c7089fbe26ade67e5e03183d762e10eee039becdaa`; the
epoch-2 checkpoint and completed run summary remain in the active run
directory. The equal-parameter aligned non-graph arm completed and passed
the strict paired audit. Outer-2, outer-3, and outer-4 graph/aligned pairs
also completed and passed. All five folds at seed `20261030` favor aligned
pooling on participant-macro AP and macro-Brier. See the five-fold aggregate
summary above. The conclusion remains specific to this model, data release,
split, seed, and two-epoch training protocol.

## What the first gate decides

The clean event GRU has lower participant-macro AP and higher Brier score than
the capacity-similar CGM-only MLP on identical validation windows. The paired
fixed-prediction interval favors CGM-only. Therefore the study cannot claim
that the present event representation improves prediction, and the earlier
comparison against a logistic CGM model does not isolate event information.
This result does not answer whether a better event architecture or explicit
relations can help, and it does not establish clinical-event absence or
real-time availability.

## Ordered work

1. **Preserve the first gate.** Keep the original ZIP, its SHA256, both model
   directories and the aggregate paired report private. Do not tune on the
   internal development-test or locked holdout. The recovered bundle is
   complete; this gate is done.
2. **Checkpoint replay and convergence diagnostic — complete.** Provenance
   passed: the replayed checkpoints match the bundled source fingerprint
   `05f4584f8f83afe9480ec289833b2df7484a3d4e4c5b3a0fb0f8dfb996ddb1cf`.
   The saved epoch-1 CGM MLP and clean event GRU were evaluated (without
   retraining) on the same 8,885,621 outer-0 windows as the saved epoch-2
   predictions. Both epoch-1 outputs passed prediction-window identity checks,
   and the completed ZIP was downloaded, SHA-256 checked, and tested for
   archive integrity. The paired fixed-prediction comparison shows both models
   improved from epoch 1 to epoch 2; the clean GRU improved more. The CGM MLP
   still leads at both checkpoints. This is a convergence diagnostic from one
   development fold and seed, not evidence about retraining variability or KG
   relations. See
   `docs/loop_controlled_epoch1_replay_result_2026_10_11.md` and
   `audit/loop_controlled_epoch1_replay_comparison.json`.
3. **Replicate the fixed first gate — complete.** The seed-20261004 MLP and
   clean GRU each completed two epochs and produced 130 matched participant
   prediction files. A CPU replay wrote a slightly different MLP AP into its
   report; the original report was backed up and aggregate metrics were
   reconciled to the unchanged saved predictions. The strict paired comparator
   then passed on all 8,885,621 windows. The MLP again led in participant-macro
   AP (`0.482129` versus `0.473504`; paired difference `+0.008626`, 95%
   participant-bootstrap interval `+0.006917` to `+0.010288`) and had lower
   Brier. Both seeds use the same validation cohort, so this is a two-fit
   direction check, not independent-cohort replication. See the
   [second-seed result](loop_seed20261004_second_gate_result.md).
4. **Add a full-CGM-history control — epoch-2 comparison verified.** The
   earlier pair sees only current glucose and recent slope. The
   [versioned history-cache gate](loop_full_cgm_history_gate.md) now defines
   and fixture-tests a causal, masked 120-minute CGM history on the frozen
   windows. The research-scale private cache has been built for 652
   development participants (44,028,064 windows; 1,296,297 positives), passed
   independent row-by-row validation, and was staged as
   `private/kaggle_loop_full_history_input`. Its history content digest is
   `aace94dab8d0d1b59a24b900a981bd4b603de5b9b48dc1eab6b06ea85f7c0afd`.
   Kaggle's console reported history-only AP `0.471865` and history-event AP
   `0.460532` on outer-0 validation, with a paired history-only advantage of
   `0.011334` (95% participant-bootstrap interval `0.009345` to `0.013209`).
   Macro Brier was `0.021357` and `0.021839`; pooled Brier was `0.021005` and
   `0.021467`. Both per-model bundles and the aggregate report were recovered;
   ZIP integrity, SHA-256, model metadata, participant prediction alignment,
   and metric recomputation passed. The initial empty Kaggle file listing was
   stale. See [the verified result](loop_full_history_result_2026_10_17.md).
   Keep the earlier two-feature model as a separate, stronger reported
   baseline (AP about `0.482`). The original archives contain both epoch
   checkpoints and only epoch-2 prediction files. The history-only epoch-1
   checkpoint has now been replayed and independently compared with its
   epoch-2 predictions: participant-macro AP improved from `0.430144` to
   `0.471865` on the same windows. Its verified bundle is recovered locally.
   The history-event epoch-1 replay is complete and strictly paired to epoch 2;
   both checkpoint replays are recorded in the linked full-history result note.
 5. **Same-architecture event-disabled control — complete for one pilot fit.**
    `history-event-zero` and its strict comparator ran for outer-0, seed
    20261003, two epochs. The disabled branch scored AP 0.469458 vs 0.460532
    for event-enabled (paired difference −0.008926, 95% participant-bootstrap
    interval −0.010402 to −0.007357); its macro Brier was also lower. This is
    not a clean equal-capacity estimate because disabling events removes
    event-encoder gradients. The result is exploratory, and the two-epoch
    training budget is not evidence of convergence. See the verified paired
    output and archive checksum in `loop_full_history_result_2026_10_17.md`.
 6. **Direct graph-benefit control — complete for one screening fit.** The
    graph-generic outer-0 run was compared with a non-graph CGM-history/event
    sequence model matched exactly at 36,883 parameters. Both used seed
    20261003, one epoch, the same 24-step CGM history, 64-event budget, split,
    input digest, optimizer and 130 validation participants. Strict row-level
    checks reconciled all 8,885,621 windows and 274,044 positive labels. The
    graph model led in participant-macro AP (0.474481 vs 0.389901; paired
    difference +0.084580, 10,000-draw 95% participant-bootstrap interval
    +0.078104 to +0.090816; higher for 126/130 participants) and Brier
    (0.021522 vs 0.024211; difference −0.002690, interval −0.003043 to
    −0.002347; lower for all 130).
    The complete bundle has been downloaded, checksum-verified and re-compared
    locally. This is one fixed-fit screening result and does not capture
    retraining variability. See the [matched control result](loop_non_graph_capacity_matched_control.md)
    and private artifacts under `private/kaggle_artifacts/`.
 7. **Replicate before making a broad graph claim.** Freeze the model
    definitions, preprocessing, epoch budget and selection rules using current
    development evidence. Run graph-generic and the capacity-matched non-graph
    sequence control over all five patient-disjoint outer folds and multiple
    prespecified seeds. Report fold/seed variation as well as
    participant-bootstrap intervals; the latter condition on fixed model
    fits. Do not open the locked holdout. Kaggle currently warns that the
    account is almost out of compute quota; its Active Events panel reports
    zero running events and the draft session is off. Confirm available quota
    or use a separate GPU runtime before starting the next long campaign, with
    the same inputs and artifact safeguards.
    **Update, 19 October:** the local MPS campaign has completed the matched
    graph-generic/sequence pair on all five outer folds, all with seed
    `20261003` and one epoch. The paired AP differences favor graph-generic on
    all folds (+0.080620, +0.081746, +0.073460, +0.110465, +0.086370); the
    descriptive mean is +0.086532. Macro-Brier differences also favor
    graph-generic on every fold (mean −0.002113). See the [outer-4 paired
    report](../audit/loop_mps_outer4_graph_vs_sequence_paired_20261019.json)
    and [five-fold summary](../audit/loop_mps_graph_vs_sequence_five_fold_summary_20261019.json).
    This completed patient-fold coverage for seed `20261003`; seed replication
    has since been completed as recorded below. The next gate is relation-shuffle,
    endpoint/time-reconstruction and
    event-order controls. Do not promote these one-epoch fits to a clinical or
    general graph claim.
    **Update, 20 October:** a second seed (`20261004`) has now completed both
    outer-0 MPS fits under the same one-epoch contract. The paired AP difference
    is +0.078540 (95% participant-bootstrap interval +0.069529 to +0.087102),
    and macro-Brier difference is −0.002178 (interval −0.002464 to −0.001901).
    Both seeds therefore favor graph-generic on outer-0, but this is one-fold
    seed replication only. See the [second-seed paired audit](../audit/loop_mps_outer0_seed20261004_graph_vs_sequence_paired_20261020.json).
    The next empirical gate remains prespecified seed replication on more
    folds and semantic relation perturbation controls; intervals on fixed
    predictions do not substitute for retraining uncertainty.
    **Update, 20 October:** seed `20261004` is now also complete on outer-1.
    Its paired AP difference is +0.090208 (95% participant-bootstrap interval
    +0.081627 to +0.098271), with macro-Brier difference −0.002430 (interval
    −0.002807 to −0.002070). Both seeds favor the graph-generic fit on outer-0
    and outer-1. This expands seed replication to two folds but remains a
    one-epoch architecture comparison; see the [outer-1 paired audit](../audit/loop_mps_outer1_seed20261004_graph_vs_sequence_paired_20261020.json)
    and [interim two-seed/two-fold summary](../audit/loop_mps_graph_sequence_two_seed_two_fold_summary_20261020.json).
    **Update, 20 October:** seed `20261004` is now complete on all five outer
    folds. Graph-generic has higher participant-macro AP and lower
    participant-macro Brier than the capacity-matched sequence control in each
    fold at both seeds. Across folds, the descriptive mean AP differences are
    +0.086532 (seed `20261003`) and +0.086575 (seed `20261004`); mean macro-Brier
    differences are −0.002113 and −0.002220. These are descriptive fold
    summaries, not uncertainty intervals over participants, folds, or model
    seeds. The models remain one-epoch exploratory fits and differ in more than
    graph topology, so this result does not identify relation semantics as the
    cause. See the [five-fold paired summary](../audit/loop_mps_graph_sequence_two_seed_five_fold_summary_20261020.json)
    and the [capacity-matched control record](loop_non_graph_capacity_matched_control.md).
    The next gate is matched event-disabled and relation-perturbation controls,
    followed by explanation-fidelity tests. Keep the locked holdout sealed
    until the model and analysis plan are frozen.
 8. **Test which event content and relations matter.** The matched
    generic-edge vs modality-typed temporal-graph pilot completed for outer-0,
    seed 20261003, one epoch per variant. Generic routing led on AP (0.47448
    vs 0.47186) and Brier (0.021522 vs 0.021619); see
    [`loop_temporal_relation_pilot.md`](loop_temporal_relation_pilot.md) and
    its audit receipt. This tests routing inductive bias: relation IDs derive
    from event modality and time, not additional clinical information. With
    the broad graph comparison now replicated, test generic versus typed
    routing, shuffled relations, event-order perturbations and event-disabled
    controls under matched training budgets. Report event coverage and the
    assumed occurrence-time availability. Measure explanation fidelity
    separately from predictive ranking.
    **Update, 20 October:** a one-epoch seed-`20261004` typed-versus-generic
    routing screen now covers all five patient-disjoint validation folds.
    Generic routing has higher participant-macro AP in three folds and typed
    routing in two; the unweighted mean fold difference (typed minus generic)
    is −0.000476. Macro-Brier differences are mixed as well. This is mixed,
    descriptive evidence about the tested modality-derived routing rule; it
    does not identify clinical relation semantics. At that time the next gate
    was a relation-assignment perturbation and matched event-disabled
    comparison. Both have since been run as outer-0 screens; see the 25 October
    update below. They still need fold/seed replication before a relation-level
    conclusion. See the
    [five-fold typed-routing summary](../audit/loop_relation_typed_vs_generic_seed20261004_five_fold_summary_20261020.json).
    **Update, 25 October:** the matched event-disabled comparison completed on
    outer-0, seed `20261004`. Generic graph minus event-disabled AP was +0.002800
    (paired 95% participant interval [+0.001996, +0.003609]); macro Brier
    difference was −0.0002003 (interval [−0.0002411, −0.0001597]). This is one-
    fold evidence for event-input value, not relation semantics; the disabled
    branch has fewer active trainable pathways. Replicate this on further folds
    and a second seed. **Update, 26 October:** the matched causal endpoint test is complete on
    outer-0 through outer-4 at seed `20261004`. Nearest-minus-second-nearest AP
    was −0.000631, +0.006681, −0.000183, +0.001618, and +0.004350; macro-Brier
    differences were +0.0000509, −0.0002618, −0.0000686, −0.0000571, and
    −0.0001664. AP favors nearest on three folds and second-nearest on two;
    Brier favors nearest on four. This remains a descriptive one-seed screen,
    not evidence of a general relation benefit. Next replicate this prespecified
    contrast with another seed; event-order and explanation-faithfulness tests
    remain. See the [endpoint-perturbation report](loop_endpoint_perturbation_result_2026_10_25.md),
    [five-fold summary](../audit/loop_relation_endpoint_perturbation_seed20261004_five_fold_summary_20261026.json),
    [outer-4 paired audit](../audit/loop_relation_endpoint_perturbation_outer4_seed20261004_paired_20261026.json),
    and [event-ablation report](loop_event_ablation_result_2026_10_25.md). A
    second seed (`20261005`) has completed all five folds. Its nearest-minus-
    second-nearest AP differences are +0.001615, +0.003555, +0.001039,
    +0.001413, and +0.000907; the outer-2 interval includes zero. Macro-Brier
    differences are +0.0000189, −0.0001642, −0.0000620, −0.0000215, and
    −0.0000179; the outer-4 interval includes zero. AP favors nearest on 5/5
    folds, Brier on 4/5. Across both seeds, nearest favors AP and Brier in 8/10
    seed-fold pairs. A participant-cluster bootstrap averaging each person's
    paired difference over both fixed seeds gives +0.002097 AP (95% interval
    +0.001761 to +0.002443) and −0.0000773 macro-Brier (−0.0000957 to
    −0.0000594). Interpret as endpoint-assignment sensitivity only: these
    intervals condition on the two fitted seeds and do not estimate a broad
    training-seed distribution. The next temporal control is a fixed-checkpoint
    within-window event-age reassignment: rotate ages across active records,
    preserving event and age multisets while breaking event-time/endpoint
    pairing. A naïve token-row order shuffle is not useful for this architecture
    because event messages are aggregated by target CGM node. The evaluator is
    [`evaluate_event_age_reassignment.py`](../scripts/evaluate_event_age_reassignment.py);
    method and exact command are in
    [`loop_event_age_reassignment_control.md`](loop_event_age_reassignment_control.md).
    The within-window event-age reassignment is complete for two seeds across
    all five outer folds using saved epoch-1 checkpoints. Every clean replay
    reproduced its archived metrics and exact prediction-window identity.
    Original-minus-reassigned AP is positive in 10/10 seed-fold fits (mean
    +0.0001118), but only 3/10 fold-specific participant intervals exclude
    zero. Macro-Brier direction is split 5/5, with 4/10 intervals excluding
    zero. Because the same 652 participants recur across seeds, these are
    descriptive fixed-fit results, not ten independent replications or a
    pooled participant interval. They show small, metric-dependent sensitivity
    to one deterministic timing reassignment, not relation validity or
    generalizable benefit. Exact source reproduction is not claimed because
    current workspace source digests differ from the original runs; clean
    predictions nonetheless reproduce stored scores within tight tolerances.
    See the [control report](loop_event_age_reassignment_control.md),
    [two-seed/five-fold summary](../audit/loop_event_age_reassignment_two_seed_five_fold_summary_20261029.json),
    and [both seed summaries](../audit/loop_event_age_reassignment_seed20261004_five_fold_summary_20261029.json).
    CPU was used because this Mac has no CUDA/MPS; the active Kaggle session
    remains untouched. An outer-0 exploratory event-set deletion/retention
    audit is now complete on 518 deterministically sampled validation windows
    across all 130 participants. Top-three events selected by individual
    deletion sensitivity changed predictions more under joint deletion than
    modality-matched random sets; retaining them stayed closer to the original
    prediction. Since the same deletion measure selected the top events, the
    joint-deletion contrast is selection-conditioned and is not independent
    evidence of explanation faithfulness. The next gate is a stronger
    attribution/perturbation design with independent selection and evaluation,
    recency/value-matched controls, and replication across folds/seeds. See
    [`loop_graph_event_explanation_faithfulness.md`](loop_graph_event_explanation_faithfulness.md).
    See the [seed-20261005 five-fold summary](../audit/loop_relation_endpoint_perturbation_seed20261005_five_fold_summary_20261028.json),
    [combined two-seed summary](../audit/loop_relation_endpoint_perturbation_two_seed_five_fold_summary_20261028.json),
    [participant-cluster bootstrap](../audit/loop_relation_endpoint_perturbation_two_seed_participant_cluster_bootstrap_20261028.json),
    and [outer-4 paired audit](../audit/loop_relation_endpoint_perturbation_outer4_seed20261005_paired_20261028.json).
9. **Freeze and test.** Select the final configuration using development data,
   document every selection, then open the locked holdout once. External Jaeb
   cohorts can support later transportability checks only after their field,
   treatment-regime and label definitions are harmonized and independently
   audited.

Before any long Kaggle campaign, confirm a tiny file can be downloaded from
the active session. Save each completed model's `result.json`, checkpoints and
participant predictions promptly rather than relying on a single final ZIP.
Keep protected predictions out of Git. The current root-level extracted
campaign is ignored by `.gitignore`; the aggregate audits contain no patient
identifiers.

## Completed epoch-1 replay handoff

The replay input was
`private/loop_controlled_epoch1_replay_input.zip` (SHA-256
`d830229af8a738773897252a6d7908ef47b84b709c938f7254d5cd8931f2ea31`), and
the importable notebook is
`kaggle_event_sequence_gru/loop_epoch1_checkpoint_replay.ipynb`. The input
contract contains the exact archived source, both verified model checkpoints,
and no participant predictions or locked-holdout data. The notebook checks
every staged file hash before evaluation. The output bundle is
`private/loop_epoch1_replay_20261011T103602Z_a0f2f38d_bundle.zip` (243,869,545
bytes; SHA-256
`c6fdef48c6bcaf7e7ad46cf849f57565081142bbb5fba5f8364515490ec0dcc7`). Its
integrity test passed. Extracted outputs and participant-level predictions
remain private because they contain study IDs.
