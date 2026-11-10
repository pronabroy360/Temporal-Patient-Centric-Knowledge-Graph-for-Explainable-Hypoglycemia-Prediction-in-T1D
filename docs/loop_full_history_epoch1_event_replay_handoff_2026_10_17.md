# Full-history event epoch-1 replay handoff — 2026-10-17

## Completed

The history-only epoch-1 checkpoint replay was recovered locally and strictly
compared with its saved epoch-2 validation predictions. The verified result is
recorded in `docs/loop_full_history_result_2026_10_17.md`, with the machine
readable comparison at
`audit/loop_full_history_history_only_epoch1_vs_epoch2_strict_20261017.json`.

## Kaggle retry status

The event-model epoch-1 replay had **not** started at the time of this earlier checkpoint. In the active
Kaggle notebook `Loop Sequence T1D Controlled Comparison`, the session reports
`Draft Session Running`. The visible preflight output is still at
`verify_full_history_input`; its receipt and the event-loader equivalence probe
result were absent at the last inspection. The console displayed old status
text and did not return a fresh process listing while the run remained active.
Treat the displayed process ages and logs as stale until a new status result or
completion artifact appears.

On a later recheck, the same stage and missing-artifact state remained visible.
An interrupt was attempted through Kaggle's run controls, but the UI continued
to report `Draft Session Running`; termination was not confirmed. Do not assume
the cell or its child processes stopped. The Kaggle tab was brought forward in
Chrome to make manual inspection possible; no runtime restart was performed.

The retry stages development-only inputs at
`/kaggle/working/loop_full_history_epoch1_input_20261017`, uses the original
source package at
`/kaggle/working/t1d_full_history_code_76cc64f3fe2d`, and resumes the original
run under
`/kaggle/working/loop_full_history_20261016T182943Z_68b02d56`. The locked
holdout is excluded. Do not start a second replay or cancel the active run
based on the stale console text.

## Resume gate

Before inference, confirm all of the following from fresh Kaggle output:

1. `epoch1_restaged_preflight_receipt.json` exists and reports successful
   validation of the staged development input.
2. `event-epoch1-loader-probe/probe_result.json` exists and confirms exact
   equality between the original and selected-participant event loaders for
   the probe partitions.
3. The receipt and probe bind to the original epoch-1 history-event checkpoint
   and the frozen manifest/window identity.

Only then run `scripts/evaluate_full_history_checkpoint_selected.py` with the
matching receipt, probe result, original source run and epoch-1 checkpoint.
Package and verify its predictions before computing paired comparisons.

## 17 October input-discovery failure

The active Kaggle notebook `Loop Sequence T1D Controlled Comparison` later
showed the assertion `Expected one history-cache archive, found 0`. Its input
panel showed the development input dataset attached, while the failing cell was
the older archive-only discovery code. This is an input-discovery failure, not
a model or CUDA failure. The page also reported `Failed to save draft` with a
Kaggle `ConcurrencyViolation` (draft sequence mismatch). At the latest visible
failure, the assertion had stopped that cell and both GPUs showed 0% use; no
epoch-1 event replay result was emitted. Do not infer that training began from
the presence of the earlier epoch-2 folders.

The local full-history notebook generator was updated to detect cache folders
and archives by the `loop-cgm-history-cache-v1` metadata value and to accept a
full-history development input directly. The corrected generated notebook is
`kaggle_event_sequence_gru/loop_full_history_comparison.ipynb`. The live Kaggle
draft did not accept or save that correction during the check. Clear the
draft-save conflict before relying on edits there; preserve/download the
completed epoch-2 bundles before changing or restarting that runtime.

## Live-session artifact audit — 17 October, 19:42–19:43 local

The active Kaggle console was checked read-only. It confirms that
`/kaggle/working/loop_full_history_input` exists and has a
`loop-full-history-input-v1` contract, and that the recovered
`history-event` run has both epoch checkpoints (epoch 1 is 456,925 bytes) and
130 saved validation prediction files. The root preflight receipt exists and
covers 652 development participants. The checkpoint's saved `source_sha256`
matches `train_history_controlled.source_digest()` for
`/kaggle/working/t1d_full_history_code_76cc64f3fe2d`; the run is complete and
is the event variant. This confirms the artifact needed for an epoch-1 replay
is still present in this Kaggle working directory.

The receipt's quick `input_stat_sha256` does not match the current staged copy.
The evaluator explicitly supports this restaging case by re-verifying all
history, CGM and event contents against the receipt before inference. The
mounted source package does **not** contain either
`evaluate_full_history_checkpoint.py` or
`evaluate_full_history_checkpoint_selected.py`. The local optimized evaluator
is available, but it must be transferred outside the frozen source directory
so the training-source digest remains unchanged; a console transfer attempt
failed with `SyntaxError`, and no evaluator or inference run was started.

At the latest browser check, Kaggle reported “Waiting for the next available
notebook” at queue position 70, both GPUs were at 0%, and no replay output
existed. The live notebook still reports `Failed to save draft` and a
`ConcurrencyViolation`. Its visible training cell contains a malformed
`lock_path` line from an earlier console probe. Do not run that cell or start
the two-model training cell again. The diagnosis is now precise: the missing
ZIP assertion is a stale archive-only input-discovery path, while completing
the checkpoint replay additionally requires a healthy Kaggle session and the
two evaluator helpers. No model inference has been claimed from this audit.

The private full-history dataset subsequently finished mounting (16.99 GiB),
and Kaggle started a fresh draft session. The epoch-1 replay still did not
start: GPU use remained 0%. A separate local notebook is now generated at
`kaggle_event_sequence_gru/loop_full_history_event_epoch1_replay.ipynb`. It
uses the saved event checkpoint only, verifies the unchanged training-source
fingerprint, performs the two-partition event-loader parity probe, then
evaluates epoch 1 and bundles the validation predictions. It embeds the two
evaluator helper scripts outside the frozen training source tree. The active
Kaggle draft remains unsavable and its displayed cell now contains additional
console-probe text; do not execute or rely on that live draft. No model
training or inference was started by these checks.

## Browser bridge note

Kimi WebBridge is connected again. Its status reports an update available:
`kimi-webbridge upgrade`. No upgrade was run during the replay check.

## Corrected replay attempt — 17 October, 14:15 UTC

The missing-archive problem was traced to a split Kaggle mount. The directory
`/kaggle/working/loop_full_history_input` held the full-history contract and
CGM feature cache, but the sequence dataset (manifest plus event cache) and
the full-history dataset (64 history partitions) were mounted under separate
read-only roots. The first checkpoint-only attempt therefore stopped before
inference when the evaluator could not find `loop_model_manifest.json`.

The second attempt assembled
`/kaggle/working/loop_full_history_epoch1_replay_input_20261017` using symlinks
to those mounted caches and copied the existing full-history contract. The
canonical manifest SHA matched the contract exactly
(`69b41e4acfae7d2afc990c8cd15d8fc3f969784d4e5f6534a9263033d341ad52`), the
contract says `contains_locked_holdout: false`, all 64 history partitions are
present, and the event-cache metadata is present. The local replay cell and
generated notebook were updated to assemble these split inputs automatically;
the notebook passes AST validation and the focused test set passes (7 tests).

The loader-parity gate has now passed: selected and original event feature rows
were identical across partitions 2 and 3 for 3 participants and 140,253
windows; the probe also records the epoch-1 checkpoint SHA-256. The full
At that earlier checkpoint, receipt-bound content revalidation was active in
Kaggle. The replay later completed; see the completion record at the end of
this handoff. The historical instructions below describe that interrupted
attempt and are retained for provenance, not as current instructions.

## Replay completed and locally verified — 17 October, 15:08 UTC

The receipt-bound content scan completed, followed by inference with the saved
event epoch-1 checkpoint. All 64 partitions finished. The report verified all
130 validation participants, 8,885,621 windows, 274,044 positive labels, and
the frozen prediction identity SHA-256
`a68ad87255e8b8944b269a6995489640ee6b37576799e917d548a0d161700224`. The
selected loader's differential probe passed on partitions 2 and 3 (140,253
windows across 3 participants), and the checkpoint SHA-256 is
`0b430e7c5a4b4e5c8f3f4695d6d6f0b937e57ae50981dac42de38a1b963b66df`.

The completed bundle was downloaded to
`private/full_history_recovered_20261017/history-event-epoch1-replay_bundle.zip`.
It is 126,361,188 bytes, its SHA-256 matches Kaggle's reported
`4600bc3b55b7066d5b5c8a2de68c75c6e2687c834c172188d431585d191d1c46`, and
`unzip -t` passes. The local comparison script paired every participant,
timestamp and label against the saved history-event epoch-2 predictions. The
strict result is
`audit/loop_full_history_history_event_epoch1_vs_epoch2_strict_20261017.json`:
epoch 2 exceeds epoch 1 by 0.063455 participant-macro AP (95% fixed-prediction
participant-bootstrap interval 0.057791 to 0.068603) and improves macro Brier
by 0.002372 (interval 0.002077 to 0.002700). Paired epoch-1 history-only vs
history-event results are in
`audit/loop_full_history_history_only_vs_event_epoch1_20261017.json`; the
history-only branch leads AP by 0.033068 and macro Brier by 0.000893 in that
epoch. Both fits improved by epoch 2, so the early-epoch difference is only an
optimization diagnostic, not evidence that the event model is inferior after
convergence or that graph relations do not help.

At replay completion, the Kaggle runtime was idle. Its old unsaved notebook
draft still reported a save conflict and contained stray console text; the
successful replay was executed from the console in the existing runtime, not
from that corrupted cell. Do not run the old cell. The replay cell and
generated notebook now assemble split mounted caches automatically and pass
local AST checks plus the focused test suite.

## Stale comparison-cell input error — 17 October 2026

Inspection of the active `Loop Sequence T1D Controlled Comparison` Kaggle
editor confirmed that its saved cell is an older archive-only version. It
raises `Expected one history-cache archive, found 0` because the private
history cache is mounted as the extracted directory
`/kaggle/input/datasets/roypro360/loop-full-history-development-input-20261016/loop_cgm_history_cache`,
not as `loop_cgm_history_cache_upload.zip`. The sequence input (manifest, CGM
feature cache and event cache) is mounted separately. The editor also reports
`Failed to save draft`, so its old cell should not be used as the source of
truth.

The corrected local notebook
`kaggle_event_sequence_gru/loop_full_history_comparison.ipynb` accepts either
the combined development input or these separately mounted datasets and
validates their contracts before training. The stale
`/kaggle/working/loop_full_history_input` directory in that editor is
incomplete because it lacks `loop_model_manifest.json`; do not pass it to the
trainer. The checkpoint-replay runtime has a complete, receipt-checked input
assembly at `/kaggle/working/loop_full_history_epoch1_replay_input_20261017`.
