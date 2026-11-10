# Colab seed 20261004 resume handoff

**Resolved later on 15 October 2026:** This handoff preserves the state at
the failed comparator run. Drive was remounted, the saved-prediction metric
audit identified a small MLP report mismatch, the original reports were backed
up and reconciled, and the strict paired comparison passed. The campaign now
records `complete: true`. Use the [verified second-seed result](loop_seed20261004_second_gate_result.md)
for current metrics and next steps; the absent-file and incomplete-campaign
statements below describe the earlier failure only.

Updated: 2026-10-15

## Safe to close the laptop

The Colab notebook header showed **All changes saved** when checked through the connected browser. The campaign driver is no longer running (the supplied status reported no live process / a defunct Python process), and the training artifacts were written to Google Drive. You can shut down the laptop. The Colab runtime itself was still connected when inspected; no active campaign process was indicated.

Notebook: [loop_seed_replication_colab.ipynb](https://colab.research.google.com/drive/1hYJANNYYChoNYhBPOU3VkY-1jFDq_6yl)

Drive campaign root:

```text
/content/drive/MyDrive/loop_seed_replication_runs/loop_seed_replication_20261013T095921Z_42ed4995
```

## What completed

- Seed `20261004`, outer fold 0, two-epoch clean event GRU training completed. The campaign log recorded both `cgm-mlp_outer0_seed20261004` and `clean-gru_outer0_seed20261004` as completed runs.
- The clean-GRU artifacts were written under `clean-gru_outer0_seed20261004`, including epoch checkpoints and run/result metadata. The prior training output reported 130 validation participants, 8,885,621 windows, and 274,044 positive labels. Its prediction identity was independently verified.
- The seed 20261004 paired comparison did **not** complete. `paired_comparison_seed20261004.json` and `seed20261004_completion.json` were absent in the diagnostic output, and `campaign.json` still had `complete: false`. The seed 20261003 comparison remains recorded separately.
- No seed 20261004 paired model result should be reported yet.

## Exact failure

The driver reached `compare_controlled_neural_archives.py` and stopped because its consistency guard found that the first archive (`cgm-mlp_outer0_seed20261004`) reported a `participant_macro_ap` value that did not match the value recomputed from its saved predictions:

```text
ValueError: first archive's reported participant_macro_ap differs from its predictions
```

The local recovery helper provides a strong explanation: it computes metrics from a fresh CPU checkpoint replay, but verifies that replay against the pre-existing prediction files only within a score tolerance of `1e-5`; it then writes the replay metrics into `result.json` and `run.json` without replacing the original prediction files. The saved GPU predictions differed from CPU replay by as much as `3.28e-7`. AP depends on score order, so tiny floating-point changes can change AP when scores are very close or tied. This makes the report and prediction files internally inconsistent even when the checkpoint replay is otherwise valid. This explanation is supported by the code path but still needs the archive-only metric audit below to confirm the actual saved-prediction values.

Do not bypass the comparison guard or treat the unpaired model metrics as a valid controlled comparison.

## Resume procedure

1. Reopen the notebook above and mount Google Drive if the runtime restarted.
2. Set `ROOT` to the Drive campaign path shown above. Read `campaign.json`, both run directories' `result.json` and `run.json`, and their validation prediction archives. Confirm files and hashes before changing anything.
3. Recompute participant-macro AP directly from each saved prediction archive using the project's `threshold-grouped-ap-v2` implementation. The new local helper is `scripts/reconcile_controlled_archive_metrics.py`; first run its default read-only audit against the MLP archive and save its JSON output outside that archive. It recomputes the report metrics from the actual saved JSONL files.
4. If the audit confirms only report/prediction metric disagreement and all identity/count checks pass, rerun it with `--apply`. It creates a timestamped backup of both metadata files and updates aggregate metric fields from the unchanged prediction files. Then run `compare_controlled_neural_archives.py` against the MLP and GRU archives. Do not retrain either model unless the checkpoint and prediction identity checks fail.
5. Rerun only the paired comparator after both archives pass identity, contract, and reported-metric checks. Write the comparison to a new output path if a prior output already exists.
6. Once the comparison succeeds, verify paired-window identity and aggregate metrics, then create and checksum a durable result bundle and update the research notes. Keep this as development validation; the locked holdout remains untouched.

## Commands and paths to inspect next

```text
campaign.json
campaign_seed20261004_driver.log
paired_comparison_seed20261004.log
paired_comparison_seed20261004.json          # expected absent after this failure
cgm-mlp_outer0_seed20261004/result.json
cgm-mlp_outer0_seed20261004/run.json
clean-gru_outer0_seed20261004/result.json
clean-gru_outer0_seed20261004/run.json
```

The immediate next task is to audit the MLP saved-prediction AP mismatch, not to start another training campaign. A read-only audit cell was added to the open notebook, but Colab left it queued behind a busy kernel during this session; no remote audit result has been confirmed yet.
