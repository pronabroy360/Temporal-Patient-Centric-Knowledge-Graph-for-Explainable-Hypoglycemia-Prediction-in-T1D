# Kaggle package: Loop 64-event GRU comparator

**Current entry point (2 October 2026):** use
`loop_controlled_comparison.ipynb` or paste all of
`ONE_CELL_CONTROLLED_COMPARISON.py` into the existing private notebook. The
cell embeds its complete code package; attach the existing private input
dataset and enable T4 x2. No code-dataset update is needed. See the
[controlled experiment specification](../docs/loop_controlled_neural_experiments.md).
It runs two epochs each for the CGM-only neural control and the GRU with
export-provenance inputs masked, saves checkpoints/predictions, and creates a
downloadable private ZIP. Opening the notebook does not start training.

The historical recovery cell and examples below document the completed run.
The old checkpoint format lacks a training-fold contract; new experiments
must use `train_controlled.py`. Legacy evaluate mode is now rejected. The
sampled historical verifier binds the local run record, final checkpoint,
frozen inputs and recovered predictions. The unchanged embedded historical
source remains in `ONE_CELL_KAGGLE_RECOVERY.py` for provenance.

This folder is the private Kaggle handoff for the next development-only model.
It implements the frozen input contract: the current CGM feature cache, the
canonical event-instance cache, the existing model manifest, a 120-minute
history and the 64 most recent event instances. It must never contain the
locked-holdout predictions or source identifiers in public output.

## Create the private Kaggle input dataset

Run the staging command below from the repository root. It copies only the
already protected derived caches and model manifest to a new directory; it
does not copy the raw Loop release.

```bash
PYTHONPATH=src python3 kaggle_event_sequence_gru/stage_private_input.py \
  --feature-cache private/loop_cgm_feature_cache \
  --event-cache private/loop_event_instance_cache \
  --model-manifest private/loop_model_manifest.json \
  --destination private/kaggle_loop_sequence_input
```

Upload `private/kaggle_loop_sequence_input` as a **private** Kaggle dataset,
then attach it to the notebook under `/kaggle/input/t1d-loop-sequence-input`.
Also upload this repository as a second private Kaggle dataset and attach it as
`/kaggle/input/t1d-tkg-code`; this provides the tested cache readers and
sequence contract.

## Notebook contract

Use a Kaggle GPU notebook with internet disabled. Copy
`kaggle_event_sequence_gru/notebook_setup.py` into its first code cell. It
validates the cache/manifest checksums before importing project code. The GRU
must train only on `outer-0` train participants, select on outer-0 validation,
and write predictions/results only to `/kaggle/working` for download.

The notebook must report: exact manifest/window hashes, seed, number of train
and validation participants/windows, positive labels, max-events=64,
truncation counts, participant-macro AP, pooled and participant-macro Brier,
and the saved prediction-artifact path. Do not attach the locked holdout.

`train_gru.py` and `train_gru_parallel.py` are retained as historical pilots.
The historical `train_gru_recovery.py` creates a new run directory,
writes an atomic run record, saves a checkpoint after every epoch, and exports
one private hashed prediction file per evaluated participant. Use the new
controlled runner for checkpoint recovery with fold and content checks.

Historical training invocation (not the current admissible input policy):

```python
!python /kaggle/input/t1d-tkg-code/kaggle_event_sequence_gru/train_gru_recovery.py \
  --mode train --fold outer-0 --evaluation-scope validation \
  --epochs 2 --batch-size 4096 --workers 3 --hidden 64 --seed 20260920 \
  --run-directory /kaggle/working/runs/outer0_seed20260920
```

For a **controlled-v1** checkpoint, recover without fitting into a new directory
with the same variant, fold, seed, epochs, batch size, workers, code and input:

```python
!python CAMPAIGN_CODE_PATH/kaggle_event_sequence_gru/train_controlled.py \
  --mode evaluate --fold outer-0 --variant clean-gru --seed 20261002 \
  --epochs 2 --workers 3 --batch-size 4096 --hidden 64 \
  --input-directory INPUT_PATH --code-directory CAMPAIGN_CODE_PATH \
  --checkpoint COMPLETED_RUN_PATH/checkpoint-epoch-2.pt \
  --run-directory NEW_RECOVERY_PATH
```

Keep every run directory private and save it as a Kaggle output/version before
ending the session. `result.json` reports pooled and participant-macro Brier
separately; compare GRU and baseline only through archives scored on identical
participants and windows.

## Data handling

Both caches and the manifest are protected research artifacts. Keep every
Kaggle dataset, notebook and output private. Delete Kaggle copies when the
study retention policy requires it. Prediction filenames are hashed, but their
JSON rows contain study participant IDs for pairing. Treat the predictions and
output bundles as protected; hashed filenames do not anonymize them.
