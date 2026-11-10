# Outer-1 matched replication handoff — 19 October 2026

## Current state

The outer-1 graph-generic and non-graph history/event capacity-matched runs were started in the existing Kaggle draft session. They were allowed to run as requested, then the session ended at its 12-hour limit before either epoch completed. No checkpoint or validation predictions were produced. The Kaggle session is now off.

The following live details record the Kaggle session before it expired; they are historical, not current process status.

At the latest live check, the Kaggle session showed **11h34m elapsed** against its 12-hour session allowance and the weekly T4 x2 quota banner showed **0 hours remaining**. Both jobs were launched in that session, each assigned one Tesla T4. The remote run directories are:

- `/kaggle/working/loop_graph_generic_outer1_seed20261003_20261019`
- `/kaggle/working/loop_sequence_matched_outer1_seed20261003_20261019`

At 00:08:05 UTC, graph process PID 79358 was alive after 32m25s and had logged epoch 1, batch 1,900: 7,565,410 of 25,756,087 expected training windows (29.4%). The non-graph sequence process PID 79394 was alive after 27m52s and had logged batch 1,700: 6,772,582 windows (26.3%). Both reports still said `complete: false`; neither run had created a checkpoint or prediction shards. The process snapshot showed both T4s at 0% utilization at that instant, and the logs included waits for history producers. The observed rate implies the one-epoch runs may not finish within the remaining session window. Keep polling the same PIDs and logs; do not infer completion from session activity alone.

Neither run had written a checkpoint or prediction shards at the latest file listing. Both trainers write checkpoints only after a full epoch. Therefore there is currently no completed outer-1 model result to evaluate. A metadata-and-log snapshot was created without touching the jobs, then downloaded and verified locally:

- `private/kaggle_artifacts/loop_outer1_live_partial_20261019T0007Z.zip`
- 7,380 bytes; SHA-256 `424ae1e28082c907bd518230bc24914fb1388c01887ad62b70885eb76de1bd86`
- ZIP CRC passed; contains both `run.json` files, both training logs, and a redacted process-status JSON (no participant identifiers or full preflight receipt).

Earlier verified snapshots remain at `private/kaggle_artifacts/loop_outer1_live_partial_20261019T0001Z.zip` (7,231 bytes; SHA-256 `7c41bd92cebfdbb358fda08d19f59fab0aae8e09f3b668a7735387868c2ac644`) and `private/kaggle_artifacts/loop_outer1_live_partial_20261019.zip` (6,758 bytes; SHA-256 `c2f451838e52840a5fe9e8d2cd07b6adb64acfb70e5ee820ecbc425375351b78`).

At 00:32 UTC on 19 October, I downloaded another fresh pair of live Kaggle logs. The graph-generic run had reached batch 3,300 (13,112,085/25,756,087 training windows; 50.9%); the non-graph sequence run had reached batch 3,100 (12,316,198/25,756,087; 47.8%). Both logs show CUDA preflight succeeded and then repeated producer-wait messages. At 00:32, the UI showed the draft session running at 11h59m with 0 weekly T4 x2 quota hours. The remote run folders still listed only `run.json` at the last refresh; neither fit had completed its epoch yet. The newest captured logs are preserved locally:

- `private/kaggle_artifacts/live_outer1_logs/graph_outer1_20261019T003230Z.log` — 8,454 bytes; SHA-256 `0d7be68a726408a823b12aa7cfeb8969fbd329e539440f99849200df189378e0`.
- `private/kaggle_artifacts/live_outer1_logs/sequence_outer1_20261019T003232Z.log` — 6,132 bytes; SHA-256 `9256bdf74c1ab221ac0226078661e92c4b6752d4baf1943407ccb8b299f4897d`.

These are genuine progress snapshots and supersede the earlier stale status-cell row. The remaining ~49–52% could not fit before the 12-hour session boundary. The Kaggle runtime subsequently ended at that boundary; a fresh check found only `run.json` in each run directory, with no completed epoch checkpoint or validation predictions. The attempt is incomplete and contributes no outer-1 performance evidence. Its final log bundle is preserved at `private/kaggle_artifacts/loop_outer1_terminated_partial_20261019_bundle.zip` (17,195 bytes; SHA-256 `ee76bc525e7de6d702c16b5884a65942f8744b26a02baa8b4403c88c23df080b`).

On 19 October, a fresh Colab T4 runtime was connected as a fallback. The private input mount did not complete: Colab requests a Google Drive popup authorization, but the browser blocks the popup and the notebook fails with `MessageError`/`ValueError: mount failed`. The current Drive folder expected by the notebook is `/content/drive/MyDrive/loop_sequence_input`; the history cache archive is expected separately at `/content/drive/MyDrive/loop_full_history_private/loop_cgm_history_cache_upload.zip`. A verified local copy of the base input exists at `private/colab_seed_replication_20261013/loop_sequence_input.zip` (2.4 GiB), and the history cache at `private/loop_cgm_history_cache_upload.zip` (611 MiB), but neither was staged into this Colab session. No training was launched there. To resume this route, the user must allow Colab's blocked Google Drive authorization popup (the visible “Re-open” prompt) once; then rerun the mount cell and verify both expected paths before starting training. Do not use “Run all” in the existing seed-replication notebook: it is not the graph-versus-sequence campaign notebook.

Latest Drive check: the correct account’s search surfaced `loop_cgm_history_cache_upload.zip` as a separate file, distinct from the `loop_sequence_input` folder, which contains only the CGM cache, event cache, contract and manifest. Drive required its “Download anyway” confirmation because the 611 MiB ZIP could not be scanned. A trusted browser click completed the download into Chrome’s temporary Downloads file; its SHA-256 (`07420a151888d15cc010ca1aaa69e5ac20976e4a971a7d0f4ba46339b233b2d5`) exactly matches the existing local `private/loop_cgm_history_cache_upload.zip`. The canonical local archive and extracted full-history input pass the 13-check preflight: matching manifest/window digests, 64 partitions, 652 development participants, 44,028,064 aligned windows, and no locked holdout. The Drive copy is now recovered and independently byte-matched; it has not been mounted or staged into Colab. The current Colab page shows `Connect T4`, and its diagnostic output says both expected input paths are absent. No training was launched. The full local test suite passes (145 passed, 3 skipped).

Latest Kaggle status check: the `Loop Sequence T1D Controlled Comparison` editor shows `Draft Session off (run a cell to start)`. Kaggle’s Active Events panel reports `Loop Temporal Relation Pilot` as `Cancelled`, with 13 hours recorded and 0 Active Events; the fresh editor tab’s `/kaggle/working` output tree is empty. Its Input pane lists the base sequence input, epoch-1 replay input, full-history development input and corrected/Kaggle runner datasets, so the data/code attachments are present even though no run is active. A warning says the account is almost out of compute quota. This state was observed without starting, stopping, or editing the notebook. No new GPU job is running, and the incomplete outer-1 attempt remains without checkpoints or validation predictions. Resume only after confirming a usable quota/runtime and keeping the corrected, checkpoint-resumable outer-1 runner attached.

For a future run, the local `train_history_controlled.py` now filters both CGM histories and event sequences to the fold's eligible training participants before joining them. This avoids building sequences for validation/test participants in every producer pass. The generated full-history and temporal-relation notebooks have been rebuilt to embed this source. Focused cache tests pass (6 passed), and the complete local suite passes (145 passed, 3 skipped). The running Kaggle jobs use an already-extracted older code payload and cannot receive this optimization in place; they were left untouched.

## Run contract

Both jobs use outer fold 1, seed `20261003`, one epoch, batch size 4096, three producer workers, the same verified full-history development input and manifest, and the same 64-event history budget. The graph and sequence models have 36,883 trainable parameters. Their train/validation groups are disjoint from the locked holdout. The staged sequence trainer writes `locked_holdout_used: false` in its run report. The locked holdout must remain unopened.

The existing input and derived outer-1 preflight receipts are:

- `/kaggle/working/loop_temporal_relation_preflight_receipt.json`
- `/kaggle/working/loop_temporal_relation_preflight_outer1_receipt.json`

The job record is `/kaggle/working/loop_outer1_matched_replication_job.json`. Code root:
`/kaggle/working/t1d_temporal_relation_code_c74cf96e4bbd`.

## Recovery and completion steps

1. In the current Colab notebook, manually allow Colab's blocked Google Drive authorization popup once. Then rerun the Drive-mount cell and verify that the base input exists at `MyDrive/loop_sequence_input` and the history-cache archive exists at `MyDrive/loop_full_history_private/loop_cgm_history_cache_upload.zip`.
2. Do not use “Run all” in the open seed-replication notebook; it is not the graph-versus-sequence campaign notebook. Stage the verified full-history input and run only a purpose-built outer-1 graph-generic versus non-graph capacity-matched campaign.
3. Before any multi-hour retry, make the driver resume from validated per-epoch checkpoints and copy each checkpoint, run contract, and completed prediction shard to persistent Drive storage. The previous Kaggle run ended before an epoch checkpoint was written.
4. After both variants complete, verify prediction shard counts and run contracts, then run `scripts/compare_graph_sequence_archives.py` on the two outer-1 archives. Require exact fold, seed, manifest, input, window identity, participant, window, and label agreement before interpreting paired metrics.
5. Preserve a checksum-verified bundle and add the comparison to the evidence report. Repeat across remaining outer folds and prespecified seeds before describing the finding as replicated. Keep the locked holdout unopened.

## Scientific status

The completed outer-0 paired comparison remains the only confirmed full-history graph-versus-sequence result so far. This outer-1 run is a planned replication, not evidence until both validation archives are complete and paired. No claim about typed semantic relations, causal effects, explanation faithfulness, or generalization across folds is supported by this run alone.

## Final session state

At 00:34 UTC, the Kaggle editor showed `Draft Session off (run a cell to start)`. A final refresh of both remote run directories still showed only `run.json`; no checkpoint or prediction files were written. The last downloaded graph and sequence logs reached 13,112,085/25,756,087 (50.9%) and 12,316,198/25,756,087 (47.8%) training windows, respectively. Their captured logs and a machine-readable termination record are bundled at `private/kaggle_artifacts/loop_outer1_terminated_partial_20261019_bundle.zip`; SHA-256 `ee76bc525e7de6d702c16b5884a65942f8744b26a02baa8b4403c88c23df080b`; ZIP CRC passed. The attempt ended incomplete and provides no validation comparison. Resume only on an available compute session with the same frozen inputs and protocol.

## Browser follow-up after the user requested that a live session be left running

At 01:42 UTC on 19 October, a fresh read-only check through Kimi WebBridge showed the controlled-comparison Kaggle notebook at `Draft Session off (run a cell to start)`, with **0 Active Events** and a warning that GPU quota is almost exhausted. The notebook still has the full-history development input and runner datasets attached. No run is currently active in this notebook; I did not start, stop, or edit a Kaggle job. This fresh state supersedes any suggestion that a job is still running, while honoring the instruction not to stop an active session.

The existing Colab tab is `loop_seed_replication_colab.ipynb`, a different first-gate study (CGM-only MLP versus clean event GRU, outer-0, seeds 20261003/20261004). Its visible outputs include an old `GPU Tesla T4` diagnostic, but also report that both expected staged input directories are absent; the page currently says it is connecting to a runtime. It is not the full-history graph-generic versus capacity-matched sequence campaign. No Colab cell or Drive mount was run. Reading the Kaggle notebook’s embedded cell frame timed out, so its cell code could not be freshly inspected. WebBridge reported version 2.0.24 available and suggested `kimi-webbridge upgrade`; no upgrade was run.
