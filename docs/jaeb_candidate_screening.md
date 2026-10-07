# Jaeb candidate screening

Screening date: 10 September 2026. These are file-inventory findings, not final suitability decisions. Every candidate still requires sorted chronology, duplicate, coverage, event-capture and permissions audits.

| Release | Roster records | Main evidence in supplied files | Preliminary role | Blocking checks |
|---|---:|---|---|---|
| Loop study (2023-01-31) | 919 | Six CGM tables; three basal tables; bolus, food, exercise and wizard tables; local and UTC timestamps plus timezone-offset fields | Provisional primary candidate for the core event-relation benchmark | Very large files; de-identification and per-participant clock consistency; duplicate/overlap across CGM tables; exact semantics of basal and wizard records; lawful attribution |
| DCLP3 release 3 | 170 | CGM tables; `Pump_BasalRateChange`; `Pump_BolusDelivered`; Roche meter table whose `Carbs` field is entirely empty | Insulin–CGM relation replication/ablation cohort | UTF-16 encoded CRF tables; source-table overlap; timestamp alignment; no usable meal records; study-period availability |
| DCLP5 release | 101 | Tandem and Dexcom CGM; `DCLP5TandemBASALRATECHG_b`; completed Tandem bolus table; Roche meter table whose `Carbs` field is entirely empty | Insulin–CGM relation replication/ablation cohort | Duplicate/overlap between raw and `_b` tables; timestamp semantics and adjusted times; no usable meal records; participant-period coverage |
| FLAIR | 126 | CGM table and `FLAIRInsulinDelivery` with daily total/programmed/auto/meal/correction percentages | CGM benchmark or daily-treatment-context study | No event-level bolus/basal/meal table identified; daily summaries cannot support individual-event relation claims |
| AIDE T1D | 109 | CGM tables and participant-level insulin inventory | CGM benchmark/validation candidate | No timestamped insulin delivery, meal or activity stream; source-order anomalies documented in the [AIDE audit](aide_t1d_release_audit.md) |

The participant-level modality scan found that Loop has 851 participants with CGM, 845 with basal and bolus, 837 with nonempty food records, and 835 present in all four sets. Exercise appears for 493 participants and bolus-wizard records for 215. These are presence intersections, not proof of simultaneous temporal coverage.

DCLP3 has 168 CGM participants and 125 with both pump basal and bolus records. DCLP5 has 100 participants in each of its selected CGM, basal and bolus tables. Neither release has a nonempty `Carbs` value in its Roche meter table. They can test insulin–CGM relations, but cannot independently reproduce a meal-aware graph comparison from these files.

## Selection order

1. Use Loop as the provisional primary candidate because it has the broadest event inventory, 835 participants with all four mandatory modality presences, and the largest roster. Process its multi-gigabyte tables in streaming or chunked form.
2. Audit DCLP3 and DCLP5 as independent insulin–CGM replication cohorts; do not imply that an empty carbohydrate column supplies meal information.
3. Use FLAIR and AIDE for CGM-only or treatment-context comparisons unless additional event-level tables are discovered.
4. Choose the primary cohort only after comparing participant-level usable windows and event coverage, not by roster size alone.

The public Jaeb directory lists these releases and their download files; retain each release’s own readme attribution and disclaimer. Shared column names or study labels do not establish shared semantics.

The aggregate, identifier-free modality report is [audit/jaeb_modality_coverage.json](../audit/jaeb_modality_coverage.json). It does not resolve duplicates, timestamps, simultaneous coverage or prediction-time availability.
