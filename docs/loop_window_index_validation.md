# Loop protected window-index validation

The protected Loop index was generated from the canonical participant-sorted
CGM pass using the frozen `observed_numeric` range policy and logical-grid
tolerance of ±1 second. It contains only windows that are both input-eligible
and have a known 30-minute future label.

| Measure | Result |
|---|---:|
| Gzip partitions | 64 |
| Participants across partitions | 835 |
| Indexed windows | 56,375,850 |
| Positive future-low labels | 1,671,803 |
| Positive prevalence | 2.966% |
| Partition-digest SHA-256 | `258ab6e8b6d7c1b50da2225b4d2bc18ca52f292b743b04606c70771e6474e83d` |

The validator confirmed required metadata, timestamp and label invariants,
unique sample IDs within each partition, and well-formed compressed files.
The current index does not contain final model-fold assignments; its
`analysis_group` records the earlier protected development/holdout designation.
Final evaluation folds must be added before model fitting.

Source artifact: `audit/loop_window_index_validation.json`.
