# Loop protected window-index generation

The partitioned CGM audit can emit metadata-only records for windows that are
both input-eligible and have known 30-minute labels. Each gzip-compressed
partition contains a header followed by sample ID, patient ID, timestamp,
history start, horizon, eligibility, label, and the development/holdout group.
It contains no CGM history, future CGM values, or auxiliary-event payloads.

Run this only with at least 20 GiB free space. It uses the existing 64-way
temporary canonicalization partitions and removes them on successful
completion:

```bash
PYTHONPATH=src python3 scripts/audit_loop_partitioned_cgm.py \
  'data/Loop study public dataset 2023-01-31' \
  --development-manifest private/loop_development_manifest.json \
  --manifest-group all_candidates \
  --skip-tolerance-comparison \
  --logical-grid-tolerance 1 \
  --window-index-directory private/loop_window_index \
  --output audit/loop_window_index_generation.json
```

After a successful run, validate all partitions together:

```bash
PYTHONPATH=src python3 scripts/validate_window_index.py \
  private/loop_window_index \
  --output audit/loop_window_index_validation.json
```

The output has no final model folds yet. The `analysis_group` field records
the protected development/holdout designation used for tolerance selection;
the final evaluation manifest will be added before model training.
