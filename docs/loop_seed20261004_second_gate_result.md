# Loop controlled second-seed comparison: 20261004

Verified 15 October 2026. This is an outer-0 **development-validation** result, not a locked-holdout or external-cohort result.

The prespecified two-epoch CGM-only MLP and clean event-sequence GRU were compared on the same 130 participants, 8,885,621 prediction windows and 274,044 positive labels. Both saved prediction archives passed the paired participant/time/label check. The campaign now records both seeds (`20261003`, `20261004`) and `complete: true`.

| Metric | CGM-only MLP | Clean event GRU | Paired MLP − GRU difference |
|---|---:|---:|---:|
| Participant-macro AP | 0.482129 | 0.473504 | +0.008626; 95% participant-bootstrap interval +0.006917 to +0.010288 |
| Participant-macro Brier | 0.021152 | 0.021366 | −0.000215; 95% interval −0.000264 to −0.000164 |
| Pooled Brier | 0.020790 | 0.021008 | −0.000218 |

The MLP had higher AP for 107 participants and lower AP for 23. It had lower Brier for 110 and higher Brier for 20. Lower Brier is better. The earlier seed `20261003` showed the same direction; these are two fits on the **same cohort**, so the participant-bootstrap intervals do not measure training-seed uncertainty or transportability.

## Report reconciliation and verification

The seed-20261004 MLP's CPU checkpoint replay matched all saved GPU prediction identities, with maximum absolute score difference `3.2782554626464844e-07`. That small score change altered a few ranks: the replay-written report gave macro AP `0.48212832335835`, while the unchanged saved prediction files give `0.4821292038152405`. Its macro and pooled Brier values also differed by approximately `2.5e-10`. The strict paired comparator correctly rejected the mismatch.

The original `run.json` and `result.json` were backed up in the MLP archive's `metric_reconciliation_backup_20261015T173540Z` directory. The tested reconciliation helper updated only aggregate report metrics from the saved prediction files and recorded the previous values in the report. Participant, window, positive-label and AP-denominator counts were unchanged (`130`, `8,885,621`, `274,044`, `130`). The clean-GRU report already agreed with its saved predictions to floating-point precision. After reconciliation, the unmodified strict comparator passed and produced the paired report. Both model archives retained 130 participant prediction files; the locked holdout was not evaluated.

The pair uses metric version `threshold-grouped-ap-v2`, manifest SHA-256 `69b41e4acfae7d2afc990c8cd15d8fc3f969784d4e5f6534a9263033d341ad52`, and window-identity SHA-256 `26036d7d3d27c21a4407d15aacd916b98ba598dfded5da319288a74b54a592aa`. The final checks confirmed matching `run.json`/`result.json` records, both seed entries in `campaign.json`, the MLP backup, the cohort counts, and the aggregate paired/completion reports.

The aggregate-only ZIP is [seed20261004_verified_aggregate_bundle.zip](../audit/seed20261004_verified_aggregate_bundle.zip) (3,417 bytes; SHA-256 `d4a86918c1497b7b93599ba81a711527928549cfb341f0f94b096b9a051f0db4`). Its five JSON members passed a local ZIP integrity test. The same bundle and the private model archives remain in the user's Drive campaign directory `loop_seed_replication_20261013T095921Z_42ed4995`. The ZIP is under ignored `audit/`; this document records its checksum even if the local copy is moved.

## Research implication

For this fixed first-gate model pair, adding the recorded event sequence did not improve prediction over the capacity-similar two-feature CGM-only MLP in either seed. This does **not** test whether explicit graph relations help. The two models differ in architecture, neither uses full CGM history, event availability is assumed at occurrence time, and missing source records are not verified clinical absences. The next gate is a causal full-CGM-history control with matched prediction windows and training budget, followed by event-content and relation-specific ablations. Keep the locked holdout unopened until those development choices are frozen.
