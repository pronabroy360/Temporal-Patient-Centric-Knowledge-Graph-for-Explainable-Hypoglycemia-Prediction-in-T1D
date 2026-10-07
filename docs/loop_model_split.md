# Loop model-selection and locked-test split

The ±1-second logical-grid tolerance was selected using 652 development
participants. To preserve the original 183-participant tolerance holdout for
final evaluation, model selection uses five deterministic patient-disjoint
development folds. Each fold has separate training, validation, and internal
development-test participants.

| Fold | Train | Validation | Development test |
|---|---:|---:|---:|
| 0 | 395 | 130 | 127 |
| 1 | 381 | 141 | 130 |
| 2 | 387 | 124 | 141 |
| 3 | 398 | 130 | 124 |
| 4 | 395 | 127 | 130 |

The final selected pipeline will be fitted on all 652 development participants
and evaluated once on the 183 locked holdout participants. No performance
result from the holdout may guide range policy, temporal tolerance, features,
architecture, tuning, or alert thresholds.

Protected manifest checksum:
`69b41e4acfae7d2afc990c8cd15d8fc3f969784d4e5f6534a9263033d341ad52`.
