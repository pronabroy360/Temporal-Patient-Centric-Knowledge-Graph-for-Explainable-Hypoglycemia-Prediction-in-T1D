# Loop auxiliary-event alignment audit

Each result is computed against the same frozen set of 56,375,850 eligible
CGM prediction windows, using a 120-minute closed historical interval. Exact
event re-exports are collapsed; distinct same-time non-CGM events are
retained. Event availability is the documented `assumed_immediate` benchmark
assumption.

| Modality | Windows with one or more events | Coverage | Aligned event records |
|---|---:|---:|---:|
| Basal | 44,082,171 | 78.193% | 727,601,117 |
| Bolus | 18,897,333 | 33.520% | 33,550,484 |
| Food | 14,298,304 | 25.362% | 19,227,399 |

All 64 partitions completed and temporary event partitions were removed.
Coverage means at least one recorded event in the historical window; it does
not establish that all real-world meals or insulin actions were captured.

Source artifacts: `audit/loop_basal_window_alignment.json`,
`audit/loop_bolus_window_alignment.json`, and
`audit/loop_food_window_alignment.json`.
