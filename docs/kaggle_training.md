# Kaggle training workflow

The current raw Loop commands are dominated by file parsing, participant
partitioning, external sorting, and repeated reconstruction of CGM histories.
Those operations are CPU and storage bound; attaching a Kaggle GPU will not
make them substantially faster.

Kaggle becomes useful after creating a compact private feature table with the
frozen window protocol. The notebook
`notebooks/kaggle_cgm_logistic_benchmark.ipynb` expects a private Kaggle input
dataset containing:

- `loop_cgm_features.parquet` with one row per frozen window and the columns
  `patient_id`, `cohort_group`, `fold_id`, `label`,
  `current_glucose_mg_dl`, and `recent_slope_mg_dl_per_5m`;
- `loop_model_manifest.json` with the frozen development folds and locked
  holdout.

It uses cuML when available and falls back to scikit-learn. The notebook only
selects the CGM baseline within development folds; it does not inspect the
locked holdout. Keep the Kaggle dataset private because participant IDs and
window rows are protected research artifacts.

For the current two-feature logistic model, a local SSD is usually sufficient
once the feature table exists. Kaggle is more useful for later learned event
sequence or graph models that genuinely use GPU tensor operations. Uploading
the 19 GB raw release alone will mostly move the same CPU bottleneck to a
different machine.
