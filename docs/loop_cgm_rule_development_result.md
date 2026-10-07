# Development CGM persistence/slope reference

The non-learned CGM-only persistence/slope rule was evaluated on the 652
development participants only. It projects the latest observed CGM slope for
30 minutes and assigns a positive score when the projection crosses below
70 mg/dL. The locked 183-person holdout was not used.

| Measure | Result |
|---|---:|
| Windows | 44,028,064 |
| Positive labels | 1,296,297 |
| Participant-macro AP | 0.2252 |
| Brier score of binary rule output | 0.0551 |
| True positives | 906,905 |
| False positives | 2,037,942 |
| False negatives | 389,392 |
| True negatives | 40,693,825 |

The rule identifies 69.96% of positive windows but is not calibrated and does
not yet apply refractory suppression or an alert-burden threshold. Its Brier
score therefore describes a binary reference score, not a calibrated risk
probability. This result is a development benchmark for matched models; it is
not the final held-out performance claim.

Source artifacts: `audit/loop_cgm_rule_development.json` and
`audit/loop_cgm_rule_development_audit.json`.
