# Loop CGM range sensitivity audit

The read-only scan covered all six Loop CGM tables. It found 111,118,148 raw
rows, of which 111,059,420 were numeric CGM rows in mmol/L. Counts below are
raw-row sensitivities; they precede calibration exclusion, exact-repeat
collapse, conflicting-timestamp exclusion, and temporal window construction.

| Policy | Retained numeric rows | Excluded numeric rows |
|---|---:|---:|
| `observed_numeric` | 111,059,420 | 0 |
| `sensitivity_20_600` | 111,059,418 | 2 |
| `sensitivity_40_400` | 110,685,276 | 374,144 |

The unfiltered policy remains primary because the broad 20–600 mg/dL bounds
remove only two raw rows and no device-validity justification has been
established for the stricter 40–400 mg/dL bound. The bounded policies remain
available for development sensitivity analysis. Final impact must be measured
after canonicalization and logical-grid window construction.

Source artifact: `audit/loop_cgm_range_sensitivity.json`.
