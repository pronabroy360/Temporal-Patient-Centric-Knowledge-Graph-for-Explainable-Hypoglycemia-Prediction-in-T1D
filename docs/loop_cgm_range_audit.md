# Loop CGM numeric-range audit

Status: completed 13 September 2026. The full raw chronology scan found 111,118,148 parseable CGM-table values in mmol/L, with no missing or nonnumeric values. The observed range is **0.05551–32.8604 mmol/L**, equivalent to approximately **1–592 mg/dL**.

This is not a clinical plausibility rule. The release combines device-originated records and the available source materials do not justify a universal device-specific lower or upper exclusion threshold. Automatically excluding values near either extreme could alter low-event labels and episode counts.

The primary audit therefore retains finite numeric values after canonical conflict handling and marks adapter CGM events as `observed_pending_range_validation`. Before model training, freeze a development-only range sensitivity plan that reports the impact of any proposed lower/upper screen on patient inclusion, labels, episodes, and model comparisons. Do not use the same observed outcomes to select a screen that improves model results.
