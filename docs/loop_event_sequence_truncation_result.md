# Event-sequence truncation decision

Status date: 17 September 2026. The audit used all 44,028,064 frozen development windows and the canonical event cache tied to the frozen model manifest and CGM window identity.

The number of admissible events in the 120-minute history had median 13, 90th percentile 28, 95th percentile 36, 99th percentile 45 and maximum 306.

| Recent-event limit | Windows truncated | Fraction of windows |
|---:|---:|---:|
| 16 | 17,290,614 | 39.272% |
| 32 | 3,039,710 | 6.904% |
| 64 | 17,720 | 0.040% |
| 128 | 130 | 0.0003% |

The 16-event trial was inadequate as the final individual-event representation: it dropped 159,564,454 active instances, including 4,550,968 bolus and 2,701,960 food instances. Basal records were most frequent, but no modality-specific deletion rule is justified from this audit alone.

The frozen sequence contract is **the most recent 64 admissible event instances**. It keeps one common information set for sequence and future graph models while making truncation rare enough to report as a sensitivity rather than a dominant confound. The 130 windows above 128 events remain in scope; no patient or window is excluded.

A dependency-free position-aware linear sequence control at 64 events would have 1,088 event features and is computationally impractical under the local per-row Python optimizer. The next comparator is a GPU-trained GRU with the same 64-event contract, using a private Kaggle dataset containing protected cache-derived sequence shards. It must use outer-0 validation only for configuration work, record three fixed seeds after freezing, and keep development-test and locked holdout closed.
