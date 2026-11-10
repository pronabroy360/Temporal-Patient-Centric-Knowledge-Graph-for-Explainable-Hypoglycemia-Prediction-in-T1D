# Loop full-CGM-history input gate

Status: research-scale history cache built, independently validated, and
staged on 16 October 2026 with 44,028,064 windows from 652 development
participants and 1,296,297 positive labels. The builder and independent
row-by-row verifier matched the frozen CGM feature cache and window index.
The staged private Kaggle input excludes the locked holdout and binds history
content SHA-256 `aace94dab8d0d1b59a24b900a981bd4b603de5b9b48dc1eab6b06ea85f7c0afd`.
The Kaggle outer-0 comparison completed on 17 October 2026. The browser
console reported participant-macro AP 0.471865 for `history-only` versus
0.460532 for `history-event` (paired difference +0.011334 for history-only;
95% participant-bootstrap interval +0.009345 to +0.013209). Macro Brier was
0.021357 versus 0.021839, and pooled Brier was 0.021005 versus 0.021467.
History-only had higher participant AP for 114/130 people and lower Brier for
123/130. The run reported 8,885,621 windows, 274,044 positives, and parameter
counts 36,607 and 36,609.

The saved epoch-2 predictions and paired metrics have now been independently
verified from the recovered archives. The browser's initial empty file listing
was stale; the Kaggle runtime contained the files. Checksums, archive integrity,
checkpoint presence, prediction identities and metric recomputation are
recorded in [the run recovery and result note](loop_full_history_result_2026_10_17.md).
The locked holdout remains unopened. History-only epoch-1 predictions have
been recovered and verified; history-event epoch-1 predictions are pending.

## Why this gate exists

The two completed first-gate fits gave the event GRU only two CGM features:
current glucose and recent slope. Their result cannot establish whether events
add information beyond the full recent CGM trajectory. The next controlled
comparison needs the same prediction times and labels, with a causal CGM-only
history model as its primary comparator.

## Frozen input representation

At each existing 30-minute prediction index `t`, emit 24 five-minute slots in
`(t−120 minutes, t]`, oldest to current. Each slot has a glucose value in mg/dL
and an explicit observed/missing mask. A missing slot has zero payload and mask
zero; zero is **not** an imputed glucose measurement. The current slot must be
observed. The frozen eligibility rule requires at least 22 observed slots, at
most two consecutive missing slots, and three non-low recovery readings. The
label remains the previously frozen future-window label. No post-`t` reading
enters the features.

`scripts/build_loop_cgm_history_cache.py` canonicalizes all six Loop CGM
source tables with the established ambiguity/duplicate policy. It regenerates
the same logical-grid windows, then checks every development participant,
timestamp and label against **both** the protected two-feature cache and the
frozen window-index partition. It also checks current glucose against the
two-feature cache and aggregate counts before publishing a new versioned
private cache. The output contains development participants only, including
outer-fold training, validation and internal-test groups; it excludes the
locked holdout. The public summary contains counts and fingerprints, not study
IDs. The builder uses a temporary workspace and free-space floors. It refuses
to overwrite an existing output.

From the repository root, the research-scale command is:

```bash
PYTHONPATH=src python3 scripts/build_loop_cgm_history_cache.py \
  'data/Loop study public dataset 2023-01-31' \
  --model-manifest private/loop_model_manifest.json \
  --window-index-directory private/loop_window_index \
  --feature-cache-directory private/loop_cgm_feature_cache \
  --output-directory private/loop_cgm_history_cache \
  --summary-output audit/loop_cgm_history_cache.json
```

Adding `--preflight-only` checks the six raw tables, 64 frozen partitions,
manifest membership and disk floor without scanning raw rows. The local
preflight found 77.1 GiB free and the expected 44,028,064 development windows,
1,296,297 positive labels, 652 participants and window-identity SHA-256
`26036d7d3d27c21a4407d15aacd916b98ba598dfded5da319288a74b54a592aa`.

This is a full 111-million-row raw-data pass and sort. The completed build
reports 44,028,064 development windows, 1,296,297 positive labels and 652
participants, with the same window-identity SHA-256 as the frozen feature
cache. Preserve the private cache outside Git. A failed run does not publish
a partial cache.

After a successful build, run the independent content verifier and stage a
new private input. Both commands completed successfully for the current
cache; the staged package is separate from the old two-feature package:

```bash
PYTHONPATH=src python3 scripts/validate_loop_cgm_history_cache.py \
  --history-cache-directory private/loop_cgm_history_cache \
  --feature-cache-directory private/loop_cgm_feature_cache \
  --model-manifest private/loop_model_manifest.json \
  --output audit/loop_cgm_history_cache_validation.json

PYTHONPATH=src python3 kaggle_event_sequence_gru/stage_full_history_input.py \
  --base-input private/kaggle_loop_sequence_input \
  --history-cache private/loop_cgm_history_cache \
  --destination private/kaggle_loop_full_history_input
```

The staging script rechecks all history rows against the original cache,
binds the new content fingerprint into `input_contract.json`, and refuses
holdout-marked or manifest-mismatched inputs. The staged package and any
participant predictions remain private.

The code-complete Kaggle notebook is
[`kaggle_event_sequence_gru/loop_full_history_comparison.ipynb`](../kaggle_event_sequence_gru/loop_full_history_comparison.ipynb).
It embeds its exact source package (SHA-256
`3c4112501447b0872949689a7b77ec48e30e17213ba6ebde180bb3c7e991d7f9`),
so it needs only the **new** private full-history input dataset attached and a
GPU runtime; no separate code dataset or later script upload is required.
Opening the notebook does not start training. Running its single code cell
checks the GPU, verifies the private input, trains the two primary variants
sequentially, writes per-epoch checkpoints and per-model bundles, and then
runs the paired archive comparator. It uses a run lock to reject duplicate
launches in one runtime. The staged research-scale input is ready and training
completed. The per-model archives are now recovered and their paired epoch-2
comparison verified. The history-only epoch-1 replay is recovered and
verified; the history-event epoch-1 replay remains outstanding.
See the result note linked above.

A Colab-specific notebook is also prepared at
[`kaggle_event_sequence_gru/loop_full_history_comparison_colab.ipynb`](../kaggle_event_sequence_gru/loop_full_history_comparison_colab.ipynb).
It mounts Drive, copies the existing base input to Colab's local disk, unpacks
the history cache from `MyDrive/loop_full_history_private`, and persists
checkpoints and predictions under `MyDrive/loop_full_history_runs`. Its upload
bundle is `private/loop_cgm_history_cache_upload.zip` (641,156,185 bytes,
SHA-256 `07420a151888d15cc010ca1aaa69e5ac20976e4a971a7d0f4ba46339b233b2d5`).
The Kimi upload attempt is currently blocked because Chrome's “Allow access to
file URLs” permission is off. Also, the existing `loop_sequence_input` Drive
folder currently grants anyone with its link edit access; restrict its sharing
before running the clinical-data notebook. No new cache was uploaded to that
link-editable folder.

## Model comparison after cache completion

`kaggle_event_sequence_gru/train_history_controlled.py` now defines the
primary `history-only` and `history-event` variants plus the diagnostic
`history-event-zero`. Both primary models take the same 24-slot CGM history;
the joint model additionally takes up to 64 retained event records from the
same 120-minute lookback. The CGM-only GRU has **36,607** trainable
parameters; the joint CGM/event GRU has **36,609**. These counts, CPU
forward/backward passes, missingness response, and zero-event invariance were
checked in Colab. The current Colab account could connect only to CPU at the
time of this check, so CUDA and research-scale throughput remain untested.

The trainer independently verifies every new history row, the prior CGM
feature cache and event-cache contents before model allocation. It fixes
outer-0 participant-disjoint training and validation, AdamW `2e-4`, weight
decay `1e-4`, unweighted BCE with logits, batch size `4096`, three workers,
two epochs and a declared seed for the initial controlled pilot. It writes an
atomic checkpoint after each epoch and participant prediction archives. The
recovered original archives contain both checkpoints; only epoch-2
predictions were saved there. A separate history-only epoch-1 replay has
completed; history-event epoch 1 remains to be evaluated. This two-epoch fit is a fixed-budget
development pilot, not convergence evidence.
`scripts/compare_full_history_neural_archives.py` refuses to compare runs
with different seeds, code/input hashes, splits, windows or parameter budgets;
it recomputes metrics from saved predictions. The research-scale comparison
has been reproduced from the recovered archives. A two-epoch fit should be
reported as a fixed-budget development pilot, not convergence evidence.

Keep identical train and validation participants, window identities,
optimizer, seed list, epochs and metric definitions for both primary variants.
The zero-event variant is a same-architecture diagnostic; its inactive event
branch does not create equal effective capacity. Parameter count alone does
not ensure equivalent function class or optimization. Report macro AP,
macro Brier, pooled Brier, event coverage and the retrospective
immediate-availability assumption. This remains a development comparison,
not a relation-specific or locked-holdout result.

Only after this gate should event-content and explicit relation ablations be
interpreted. No graph novelty or predictive gain is claimed from the current
cache implementation.
