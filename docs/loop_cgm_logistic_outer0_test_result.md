# Frozen CGM logistic outer-0 development-test result

After configuration selection on outer-0 validation, the two-epoch,
learning-rate-0.002 logistic model was evaluated on the disjoint outer-0
development-test group. The locked 183-person holdout was not used.

| Group | Participants | Windows | Macro AP | Brier |
|---|---:|---:|---:|---:|
| Validation | 130 | 8,885,621 | 0.4575 | 0.02288 |
| Development test | 127 | 8,193,251 | 0.4584 | 0.02325 |

The close validation/test values support configuration stability for this fold.
This is still an internal development result; the remaining four folds and the
locked holdout are required before any final performance claim.

Source artifact: `audit/loop_cgm_logistic_outer0_development_test.json`.
