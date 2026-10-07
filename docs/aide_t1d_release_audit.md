# AIDE T1D release audit

Audit date: 10 September 2026. Release path: `data/AIDET1D_Public_Dataset/`. Provenance: supplied from the Jaeb public diabetes dataset directory. This is a structural and chronology audit only; no model has been trained and no study result is claimed.

## Decision

AIDE T1D is a strong access-compatible source for a CGM benchmark, treatment-period sensitivity analysis, and possible external validation. It is **not sufficient by itself for the core clinical-event relation claim** because the release contains no identified timestamped meal table, activity table, or insulin-delivery event table. `AIDEInsulin.txt` is an insulin-type inventory with start/stop fields and usual frequency, not a bolus/basal delivery stream.

Keep the core question unchanged. Use AIDE only for a CGM-only or treatment-context study unless another authorized source supplies timestamped clinical events. Do not label treatment-period assignment as an insulin event.

## Inventory findings

The release contains 109 roster records: all are marked eligible, 77 have status `Completed`, and 32 have status `Dropped`. The roster has six randomized treatment orders plus 27 records without a treatment-group value. The main analysis CGM table contains 7,648,308 rows across 82 participants; the extension CGM table contains 1,310,662 rows across 74 participants.

The raw device tables provide Dexcom Clarity and Tandem pump CGM records. The glossary describes `AIDEDeviceCGM` as a Dexcom Clarity CGM export and `AIDETandemCGMDATAGXB` as CGM data from the Tandem pump. The glossary describes `AIDEInsulin` as a list of insulin types for each patient. No table in the supplied Data Tables directory is identified as timestamped meal, activity, bolus, or basal delivery data.

The readme says that patient IDs and dates are de-identified and that each participant’s treatment dates receive a random offset of up to 365 days. Therefore dates can support within-participant chronology, but calendar alignment, timezone, and cross-dataset date comparisons must not be assumed.

## CGM quality findings

The streaming audit found, in `cgmAnalysis.txt`:

- 7,648,308 rows, 82 participants, and no missing or nonnumeric glucose values;
- glucose values from 39 to 401 mg/dL, with 158,728 rows below 70 and 30,630 below 54;
- a dominant nominal five-minute cadence, with small timestamp jitter around five minutes;
- 3,510 backward adjacent timestamp transitions and one adjacent duplicate timestamp in source row order.

In `cgmAnalysisExt.txt` it found 1,310,662 rows across 74 participants, no missing or nonnumeric glucose values, 21,389 rows below 70, 3,784 below 54, and no backward or duplicate adjacent transitions. The extension table still has timestamp jitter and must be sorted by participant and timestamp before window construction.

The backward transitions occur within the same participant and treatment period, so source row order cannot be used as chronological order. A release-specific duplicate policy and stable timestamp sort are mandatory before labels, episodes, or windows are generated. The audit report’s large gaps are source-order diagnostics and must not be interpreted as physiologic monitoring gaps until sorted coverage is recomputed.

## Protocol implications

1. Do not pass AIDE directly to the Ohio XML adapter. Create an AIDE adapter that preserves the source table, period, treatment, device/status fields and de-identified time basis.
2. Require an explicit de-identified floating-time convention for relative chronology. Do not invent a geographic timezone or first-usable time.
3. Sort within participant and define duplicate handling on development data. Keep the raw duplicate count and resolution rule in the audit.
4. Treat the CGM endpoint as recorded sensor glucose. Do not use retrospective period summaries, `gluIndices`, or hypoglycemia CRF outcomes as prediction inputs for the same outcome.
5. Use treatment/period as a covariate only after confirming that its availability at each prediction time is known. Otherwise use it for stratification and analysis, not input.
6. Build complete 30- and 60-minute future-label windows only after sorted coverage and participant-level episode counts are recomputed.
7. Report AIDE as a CGM-only benchmark or external validation source unless another dataset supplies timestamped insulin, meal and activity events. A positive AIDE result cannot establish that clinical event relations help.

The machine-readable inventory is [audit/aide_t1d_release_inventory.json](../audit/aide_t1d_release_inventory.json). It contains aggregate counts and category distributions, not model predictions.
