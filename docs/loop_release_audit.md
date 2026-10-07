# Loop release chronology and field audit

Audit date: 10 September 2026. Release: `data/Loop study public dataset 2023-01-31/`. Status: full streaming field scan completed; canonical deduplication, upload-time linkage and label-window construction remain pending.

## Current decision

Loop remains the provisional primary dataset. It has the event types required for the controlled relation study and explicit UTC-oriented fields. Its repeated-upload structure is both a data-engineering risk and a potentially valuable source of observed information-availability metadata.

Do not train on the raw tables. First reconstruct canonical clinical events across uploads, assign the earliest verified upload time to each event version, sort by participant and UTC event time, and freeze duplicate/version rules.

## Full-table findings

| Modality | Rows | Participants | Key findings |
|---|---:|---:|---|
| CGM | 111,118,148 | 851 | 111,059,420 `CGM` records and 58,728 calibrations; all values labeled `mmol/L`; no missing/malformed UTC fields; 7,103,736 adjacent repeated participant/timestamp records in source order |
| Basal | 48,301,308 | 845 | Mostly `temp` records; scheduled, automated and suspend types also present; no missing/malformed UTC fields |
| Bolus | 2,722,513 | 845 | Normal, square and dual/square types; no missing/malformed UTC fields |
| Food | 1,406,204 | 837 | 1,406,199 numeric carbohydrate values, almost all labeled grams |
| Exercise | 51,728 | 493 | Duration present in nearly every record; mixed seconds/minutes require conversion; reported intensity is not numeric and needs categorical inspection |
| Wizard | 119,354 | 215 | Carb input, BG input, insulin-on-board and recommendation fields are variably present |

The six CGM files are contiguous record-ID shards: 1–20,000,000 through 100,000,001–113,024,901. The three basal files likewise cover record IDs 1–49,365,092 in contiguous shards. This rules out overlap caused solely by splitting the tables into files. It does not rule out repeated clinical events created by multiple device uploads.

Source order is not chronological. The scan found extensive backward timestamp transitions and millions of adjacent repeated participant/timestamp records, especially in CGM. These counts are diagnostics of raw export structure, not final duplicate counts or monitoring gaps.

## Unit and validity rules to freeze

- Exclude calibration rows from the CGM outcome stream unless a separate calibration analysis is specified.
- Convert glucose from mmol/L to mg/dL with one documented factor after raw-value validation; preserve the original value and unit.
- Interpret basal and bolus duration fields only after confirming their glossary/source units. Large raw duration values must not be treated as minutes.
- Preserve bolus type and distinguish delivered normal/extended components. Do not replace missing optional components with zero until source semantics are verified.
- Convert exercise duration according to its per-row unit. Treat reported intensity as categorical unless the glossary establishes a numeric scale.
- Treat food values of zero separately from missing values and inspect whether duplicates arise from repeated uploads.

## Observed availability-time opportunity

Every device-event table contains `ParentLOOPDeviceUploadsID`. `LOOPDeviceUploads.txt` contains `UploadUTCDtTm`, described in the glossary as the UTC time of upload to Tidepool. The subsequent [upload-linkage audit](loop_upload_linkage_audit.md) found that the release does **not** support an observed first-usable-time study across the primary multimodal cohort: most linked events lack a usable upload UTC, and many of the remaining upload times precede their event timestamps. Treat upload records as provenance, not transaction time.

## Next audit gate

Partition by pseudonymous participant without emitting identifiers into reports. For each participant:

1. derive candidate canonical keys separately for CGM, basal, bolus, food and exercise;
2. quantify exact duplicates, conflicting versions and simultaneous distinct events;
3. retain provenance for repeated source records without treating upload time as availability;
4. compute sorted modality overlap, CGM gaps, confirmed lows and complete 30/60-minute label windows; and
5. summarize distributions across participants before choosing folds or models.

The identifier-free raw scan is [audit/loop_chronology.json](../audit/loop_chronology.json). It is reproducible with `scripts/audit_loop_chronology.py`.
