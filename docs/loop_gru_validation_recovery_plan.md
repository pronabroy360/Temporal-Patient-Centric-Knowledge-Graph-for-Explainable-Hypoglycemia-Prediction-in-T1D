# Loop GRU pilot: recovery, validation, and next experiments

Prepared: 20 September 2026.

## Purpose and current decision

Turn the completed Kaggle GRU pilot into an auditable sequence-model result before expanding training or claiming that clinical events or graph relations improve prediction. Preserve the completed computation wherever possible: if the final checkpoint survives, export predictions and recompute metrics through evaluation only.

The research question remains: **When do clinical event relations improve hypoglycemia prediction beyond models given the same information, timing, and capacity?**

This document began as a recovery task list. As of 1 October 2026, the
completed run, both checkpoints, and all 130 participant prediction archives
have been recovered and integrity checked. Exact participant/timestamp/label
pairing against the selected two-epoch CGM baseline is complete. The GRU's
participant-macro AP difference is `+0.014742` with paired-participant 95%
interval `[+0.012150, +0.017206]`; pooled Brier difference is `-0.001773`.
See [the completed validation record](loop_gru_completed_validation.md) and
`audit/loop_gru_vs_cgm_outer0_validation.json`. Sections A–D remain below as
the audit trail; Sections F–H describe the substantive work still required.

It supplements the [research protocol](research_protocol.md), [model split](loop_model_split.md), [sequence contract](loop_event_sequence_contract.md), and [decisive experiments](decisive_experiments.md). Where earlier summaries imply that the pilot established event benefit or a Brier improvement, use the qualifications below.

## 1. Evidence already available and corrections

The user-provided final log reports:

| Item | Reported value |
|---|---|
| Model | `64-event-sequence-gru-parallel-v2` |
| Training | Two epochs, 26,949,192 windows per epoch |
| Seed | `20260920` |
| Architecture | Hidden size 64; maximum 64 events |
| Execution | Batch size 4096; three producers; two Tesla T4 GPUs |
| Evaluation | `outer-0` validation; 130 participants |
| Validation windows | 8,885,621 |
| Positive labels | 274,044 |
| Participant-macro AP | 0.4717971296707051 |
| Participant-macro Brier | 0.021461022423620916 |

Expected provenance:

```text
manifest_sha256:
69b41e4acfae7d2afc990c8cd15d8fc3f969784d4e5f6534a9263033d341ad52

window_identity_sha256:
26036d7d3d27c21a4407d15aacd916b98ba598dfded5da319288a74b54a592aa
```

These are reported results. Remote artifact existence and correspondence to the local source must still be verified. A stopped process after a final result is compatible with normal completion; a PID file alone proves neither liveness nor success. The log does not prove that checkpoints remain downloadable now.

Corrections to earlier interpretations:

- The CGM logistic AP reference is approximately 0.4570554856, giving a nominal GRU-minus-logistic difference of approximately +0.014742. Exact paired window and participant membership still needs verification.
- The GRU Brier value is a mean of participant Brier scores. The logistic value 0.0228799143 is pooled over windows. **Do not compare these as evidence of improvement.** Compute both aggregations for both models.
- The GRU changes the CGM branch and model capacity as well as adding events. A gain over logistic regression does not isolate event information or ordering.
- This is a non-graph validation pilot. It establishes neither graph superiority nor relational semantic value.
- The inspected trainer copies the window identity hash from cache metadata; that is not a fresh verification of evaluated window identities. It does not persist individual predictions.
- Immediate availability is assumed from occurrence time. The result is retrospective replay, not demonstrated prospective performance.

## 2. Task A — recover and preserve the completed run

- [ ] Inspect the live Kaggle working directory and any saved private notebook outputs. Locate the actual trainer, log, result JSON, and epoch checkpoints.
- [ ] Look specifically for `loop_sequence_gru_epoch1.pt`, `loop_sequence_gru_epoch2.pt`, and `loop_sequence_gru_result.json`; do not infer absence from a possibly stale output panel.
- [ ] Save available artifacts privately under a unique run directory; do not overwrite them with a new run.
- [ ] Record SHA256 digests and file sizes for the trainer, checkpoints, result, and log. Preserve the actual executed script and imported project code/version, not only the current local copy.
- [ ] Record Python, PyTorch, CUDA, NumPy, scikit-learn, GPU information, and the available environment/package inventory.
- [ ] Verify that the epoch-2 checkpoint loads and that its architecture, epoch and seed agree with the run. Inventory available optimizer and random-state fields; do not assume the old checkpoint supports exact interrupted-training resume.

Recovery decision:

| Available evidence | Action |
|---|---|
| Final checkpoint and compatible code | Evaluate it without training to reconstruct predictions and metrics |
| Epoch-1 checkpoint only | Preserve it; document incomplete recoverability before choosing a continuation |
| Only final log or aggregate JSON | Preserve as a reported pilot; predictions cannot be reconstructed from metrics |
| No recoverable checkpoint | Prepare and test the corrected pipeline before a clearly labeled new run |

**Acceptance:** a private artifact inventory states exactly what was recovered and which verification tasks remain. Never promise restart-proof persistence solely because a checkpoint exists in `/kaggle/working`.

## 3. Task B — audit inputs, model implementation, and splits

- [ ] Compare recovered training code with `kaggle_event_sequence_gru/train_gru_parallel.py` and archive any differences.
- [ ] Verify manifest checksum, cache versions, partition identities, file integrity, and the declared input contract. Explicitly handle compressed versus expanded cache files instead of relying on a global `gzip.open` replacement in the reusable runner.
- [ ] Assert pairwise disjoint training, validation and development-test participant sets, and exclusion of all 183 locked-holdout participants.
- [ ] Reconcile outer-0 training membership to 395 participants and validation membership to 130. Reconcile actual training-window counts with the selected manifest groups.
- [ ] Carry participant, timestamp and label through evaluation. Compare ordered timestamp/label digests with the frozen CGM cache/index for each evaluated participant; reject duplicates, missing windows, unexpected participants and label mismatches.
- [ ] Verify `(t−120 minutes, t]` event selection, no future events, 64-event truncation, missing/conflict masks, numeric channels and scaling.
- [ ] Record the actual newest-first ordering used by the cached sequence encoder and define tie behavior. Do not silently change order while reproducing the completed checkpoint.
- [ ] Test padding and empty-event histories: the selected GRU state must correspond to a valid position, and padded events must not introduce unintended evidence.
- [ ] Audit exact-repeat and same-time-variant provenance features for possible dependence on later records. If prediction-time availability cannot be justified, restrict the claim and define a development-only removal sensitivity.

**Acceptance:** code and data checks establish which information each prediction used and prove exact evaluation membership. Matching aggregate row counts or copied hashes alone is insufficient.

## 4. Task C — implement evaluation-only recovery and prediction export

- [ ] Add an evaluation-only mode that loads a specified checkpoint, performs no optimizer updates, and selects an explicit fold and evaluation scope.
- [ ] Default evaluation to validation. Require an explicit scope and a recorded frozen configuration for development-test evaluation. Do not include a locked-holdout scoring path in this pilot workflow.
- [ ] Save private predictions with stable participant linkage, prediction timestamp, label and probability. Use a schema compatible with the existing archive comparison tools or a documented adapter.
- [ ] Stream predictions to disk rather than retaining all participants' labels and scores as Python lists. Keep metric computation bounded by participant or partition where practical.
- [ ] Use unique run directories, atomic artifact writes, an incomplete/completed marker and content digests. Mark completion only after output integrity checks pass.
- [ ] Re-evaluate the recovered epoch-2 checkpoint and compare its aggregate metrics with the logged values. Investigate discrepancies; do not adjust results to reproduce the target numbers.

**Acceptance:** a verified prediction archive can be rescored without retraining, and model state remains unchanged during evaluation.

## 5. Task D — correct metrics and perform paired comparison

For both the recovered GRU and matching CGM baseline, compute:

- [ ] Participant-macro AP and the count of participants for whom AP is defined. Specify how all-negative and all-positive participants are handled and use the same policy for both models.
- [ ] Pooled AP, pooled Brier and participant-macro Brier.
- [ ] Exact participant, window and positive-label counts.
- [ ] Per-participant AP and Brier differences on identical windows, including wins/losses and distribution summaries.
- [ ] A 2,000-draw paired participant bootstrap with a recorded seed and 95% interval for the primary difference. Resample participants with all their windows; do not treat overlapping windows as independent observations.
- [ ] Tied-score AP checks against the corrected project metric implementation and scikit-learn.

Definitions:

```text
pooled Brier = sum of squared errors across all windows / number of windows
participant-macro Brier = mean of each participant's Brier score
participant-macro AP = mean AP over the declared eligible participant set
```

Validation intervals are descriptive because this population has informed development. They are not independent confirmation. The AP difference from the logistic reference must not be described as an isolated event effect.

**Acceptance:** the corrected report contains like-for-like metrics, paired membership checks and uncertainty, and explicitly supersedes the earlier Brier comparison.

## 6. Task E — make future runs reproducible and operationally reliable

- [ ] Add explicit input/code paths, fold, evaluation scope, seed, optimizer settings and run-directory arguments. Remove hard-coded account paths from the reusable runner.
- [ ] Record the full effective configuration, parameter count, code/environment digests, train/evaluation counts, truncation counts and artifact locations.
- [ ] Save sufficient model, optimizer, epoch, random-state and sampler/progress information for the stated resume guarantee. Test resume behavior; distinguish exact resume from a restarted epoch.
- [ ] Add worker timeouts and liveness checks so a producer failure cannot leave the consumer waiting indefinitely.
- [ ] Report preprocessing, training, evaluation, checkpoint and completion stages, with timestamps and throughput. Check CPU/RAM/GPU use before committing to a long run.
- [ ] Validate checkpoint recovery, prediction export and artifact preservation on a small fixture before another full-data run.
- [ ] Benchmark concurrency against available CPU, memory and GPU resources. Two GPUs allocated does not imply effective utilization. Reuse prepared inputs where feasible without changing event/window membership.
- [ ] Implement a private durable artifact-save procedure and verify retrieval. Preserve completed runs before changing or stopping sessions.

**Acceptance:** a short end-to-end trial produces reloadable checkpoints, verified predictions and results, surfaces worker errors, and demonstrates the documented recovery procedure.

## 7. Task F — establish what causes the apparent improvement

Before assigning the gain to clinical events, compare on the same development windows:

| Comparator | Question |
|---|---|
| Existing CGM logistic | Does the candidate exceed the established simple reference? |
| CGM-only neural model with comparable training/capacity budget | Could nonlinear CGM modeling explain the difference? |
| GRU with event presence/quality but clinical values masked | How much signal comes from capture patterns? |
| Full permitted event-value GRU | Do recorded amounts add value beyond presence/quality? |
| Declared order/time ablation with fixed event membership | Is improvement associated with the temporal representation? |

- [ ] Specify architecture, parameter counts, optimizer/search budgets and the exact ablation transformations before running them.
- [ ] Give controls identical admissible CGM information and windows. Report remaining capacity differences honestly.
- [ ] If using event-order shuffling, declare seeds and explain which time attributes remain; shuffled positions with age attributes do not remove all temporal information.
- [ ] Retain negative results. Improvement is not a mandatory gate for scientifically valid reporting.

**Acceptance:** conclusions distinguish nonlinear capacity, capture/quality features, clinical values and temporal representation. None of these contrasts alone proves clinical causality or graph value.

## 8. Task G — freeze the sequence comparator and broaden evaluation

- [ ] Freeze the selected architecture, input semantics, optimizer, epoch/selection rule, capacity budget, calibration procedure and three explicit seeds. Treat the already observed seed as a pilot, not a retrospectively prespecified replicate.
- [ ] Replicate on development validation with the declared seeds and archive all results. Any subsequent configuration change creates a new documented development version.
- [ ] Implement the five-fold train/validation/development-test mapping from the protected manifest; the inspected trainer currently hard-codes outer-0 validation.
- [ ] Document prior exposure: outer-0 validation participants appear as another fold's development-test participants. Configuration selection has therefore touched parts of rotating development evaluation. Report the broader results as development evidence, not fully untouched confirmation.
- [ ] Compare matched models on the same folds and seeds; report seed variability separately from participant sampling uncertainty. Do not count seed repeats as new independent patients.
- [ ] Keep the 183-participant holdout predictively unevaluated until the entire final procedure is frozen.

**Acceptance:** an immutable B4 specification and complete development report exist, with selection history and exposure limitations stated.

## 9. Task H — test the actual relational research question

After the sequence comparator is credible, implement B4/G0/G1/G2 comparisons using identical retained event instances, attributes, timestamps and labels:

- **B4:** frozen sequence comparator.
- **G0:** graph with shared/generic edge transforms.
- **G1:** same graph with relation-specific transforms.
- **G2:** edge descriptors derived from endpoint types and relative time.

- [ ] Freeze relation definitions and audit whether they are directly recorded or constructed from event type/time.
- [ ] Match capacity and search budgets as closely as practical, documenting exact differences.
- [ ] Use paired folds, declared seeds and participant-level uncertainty for the planned contrasts.
- [ ] Do not interpret G1 beating a weaker logistic or compressed-summary model as proof that semantic relations help.
- [ ] If G2 matches G1, consider structured parameterization as the explanation rather than extra relation information.

**Acceptance:** claims map to the actual contrasts in [decisive experiments](decisive_experiments.md), including null or inconclusive outcomes.

## 10. Later tasks — robustness, holdout and external cohorts

- [ ] Run declared auxiliary-event availability delays on fixed evaluation windows, using the same admissible inputs for each model. Label these as simulated delays when real arrival times are unavailable.
- [ ] Select calibration and alert thresholds on the allowed validation population; evaluate episode sensitivity, false alerts per evaluable day and lead time under the protocol.
- [ ] Assess explanation fidelity and provenance separately from clinical usefulness. Rebuild dependent features/topology after event removal.
- [ ] Freeze the final analysis, training/calibration procedures, claims and artifacts before one final locked-holdout evaluation. Report results regardless of direction.
- [ ] Audit compatible external cohort mappings before transfer. DCLP3/DCLP5 may support common-field replication if their gates pass; AIDE/FLAIR roles depend on verified available modalities. Do not assume all datasets can validate meal-aware event relations.

## Immediate deliverables and execution order

1. Private inventory of recovered Kaggle artifacts and their digests.
2. Tested evaluation-only runner with exact window verification and private prediction export.
3. Recovered-checkpoint evaluation and corrected paired GRU/CGM report, including both Brier aggregations.
4. Tested reusable runner with unique artifacts, recovery support and worker diagnostics.
5. Written control/seed/fold specification, followed by matched development experiments.
6. Frozen B4 comparator and then the controlled graph study.

Do not launch a new multi-fold training campaign solely to repair metrics that can be recovered from a surviving checkpoint. If recovery is impossible, document that fact and run the corrected pipeline as a new experiment.
