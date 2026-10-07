# Kaggle run and checkpoint status — 4 October 2026

## What was verified live

The Kimi WebBridge was attached to the requested Kaggle notebook, `Loop Sequence T1D Controlled Comparison`. At approximately 22:03 Bangladesh time, the active cell was still running the `clean-gru` training stage on a T4 x2 session. The visible log had reached epoch 1, batch 4,400, with 17,492,757 training windows processed. The campaign directory shown by Kaggle was:

```text
/kaggle/working/loop_controls_20261004T152351Z_f5a83969
```

The Kaggle page displayed **“Failed to save draft.”** Its output browser showed `campaign.json`, `cgm-mlp.log`, `clean-gru.log`, and the `clean-gru_outer0_seed20261002` run directory. That run directory contained `run.json`; no epoch checkpoint was present at inspection time. The trainer writes each checkpoint only after finishing a complete epoch. A screenshot preserving this live state is in `audit/kaggle_controlled_comparison_live_20261004_220321.png`.

The generated notebook source is present locally at [loop_controlled_comparison.ipynb](../kaggle_event_sequence_gru/loop_controlled_comparison.ipynb), with its corresponding executable cell at [ONE_CELL_CONTROLLED_COMPARISON.py](../kaggle_event_sequence_gru/ONE_CELL_CONTROLLED_COMPARISON.py). These preserve the prepared workflow; they do not contain the live Kaggle kernel memory or guarantee a copy of its newest cell output.

## Save and restart implications

Saving a Kaggle notebook draft/version preserves notebook content, not the live Python process, GPU memory, optimizer state, or the current batch position. Closing the laptop/browser is not a reliable way to keep this GPU session alive. The current draft-save error also means there is no confirmation that Kaggle persisted the latest notebook edits.

The controlled trainer writes `checkpoint-epoch-N.pt` after a full epoch, but the current training mode does not resume training from a checkpoint. Its `--mode evaluate --checkpoint ...` path is for evaluation only. Rerunning the one-cell campaign creates a new timestamped/UUID campaign directory and starts training from fresh initialization. It will **not** continue from the same batch or checkpoint.

The current one-cell workflow builds a private bundle in a `finally` block after its campaign process exits. While the cell is active, that final bundle is not yet a durable copy of the current run. The only local preservation completed in this check is the live-state screenshot and this status record; a local download of Kaggle's live output bundle has not been verified.

## Safe next action

Keep the Kaggle tab/session running if you want this campaign to finish. Do not use **Cancel Run** or restart the cell. After each model finishes, its epoch checkpoints and predictions should become visible under its run directory. When the cell exits, confirm the printed `PRIVATE BUNDLE` path and use Kaggle's output download to save that ZIP locally. Then verify the ZIP contains the campaign manifest, logs, completed run metadata, checkpoints, predictions, and result JSON before relying on it.

Before closing the laptop, confirm that the archive has actually downloaded and can be opened locally. Even then, reopening the notebook and rerunning the cell will start a new campaign; use the saved artifacts for evaluation/recovery, not as automatic training-resume state.
