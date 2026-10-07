# Loop CGM development feature cache

The protected cache materializes only the two CGM predictors, window time,
label, and participant identifier for the 652 development participants. It
excludes the 183-person locked holdout. The builder regenerates the windows
from canonical CGM and verifies each participant's ordered timestamps and
labels against the frozen window index before publishing the cache.

Build it once:

```bash
PYTHONPATH=src python3 scripts/build_loop_cgm_feature_cache.py \
  'data/Loop study public dataset 2023-01-31' \
  --model-manifest private/loop_model_manifest.json \
  --window-index-directory private/loop_window_index \
  --output-directory private/loop_cgm_feature_cache \
  --summary-output audit/loop_cgm_feature_cache.json
```

This is the one expensive CGM partition-and-sort pass. The command refuses to
overwrite either output. The cache remains under `private/` because it contains
participant identifiers and row-level labels. Its public summary contains
aggregate counts and the window-identity verification only.

Subsequent CGM pilots can omit the raw release:

```bash
PYTHONPATH=src python3 scripts/run_loop_cgm_logistic_pilot.py \
  --feature-cache-directory private/loop_cgm_feature_cache \
  --model-manifest private/loop_model_manifest.json \
  --fold outer-0 --epochs 1 --learning-rate 0.002 \
  --output audit/loop_cgm_corrected_epochs1_validation.json
```

Cache metadata is tied to the model-manifest checksum and lists every expected
partition. The cache builder and both raw/cached pilot paths are tested on a
small synthetic release; the test requires them to produce identical reports.
## Completed release-backed build

The full development cache was built successfully. It contains 64 compressed
partitions totaling 411,894,904 bytes, 44,028,064 records, 1,296,297 positive
labels, and all 652 development participants. Its manifest and window-identity
hashes match the corrected validation runs. The aggregate evidence is
`audit/loop_cgm_feature_cache.json`.

Corrected validation was completed from raw CGM before this cache was added.
The cache is now intended for the five frozen development-test folds and later
matched CGM comparisons. It contains development participants only.
