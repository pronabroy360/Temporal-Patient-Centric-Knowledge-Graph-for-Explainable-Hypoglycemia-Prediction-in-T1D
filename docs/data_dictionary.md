# Canonical data dictionary v0.2

This is a proposed normalization contract, not an audited description of OhioT1DM or T1DEXI. Raw field mappings remain pending dataset access.

| Field | Type / meaning | Rule |
|---|---|---|
| dataset_id, release_id | Strings | Preserve provenance and release version. |
| patient_id | Pseudonymous string | Unique within dataset; never a numeric predictive feature. |
| event_id | Unique string | Deterministic within release; traceable to source record. |
| event_type | CGM, bolus, basal, meal, exercise, context | Unknown types require an explicit adapter decision. |
| event_time | Source event instant or interval start | Preserve original time and source precision. |
| end_time | Nullable interval end | Include in a model only once available; elapsed duration can be computed as of t. |
| available_time | Nullable first time record/field could be used | Do not silently fill unknown with event_time. |
| availability_assumption | observed, assumed_immediate, unknown | Document per source and field; test reporting delays. |
| value, unit | Nullable number and unit | CGM mg/dL; bolus units; basal units/hour; carbohydrate grams; duration minutes. Preserve original unit/value. |
| source_type, source_record_id | Device, pump, self-report, derived and record pointer | No source pointer may retrieve future features during training. |
| quality_status | observed_valid, missing, invalid, imputed | Separate measurement validity from imputation. |
| capture_status | known_captured, unavailable, unknown | Needed before interpreting no event as zero. |
| field_version_id, supersedes_version_id | Nullable version identifiers | Preserve revised values and select the latest admissible version per field at t. |
| field_available_time | Nullable first usable time for a particular field | Overrides coarse record availability when individual fields arrive at different times. |
| derivation_id | Nullable transform version | Derived features carry dependencies and as-of cutoff. |
| source_split | Original released partition | Retain even when creating new grouped folds. |

Timezone handling: preserve source-local/deidentified chronology. Convert to UTC only when a reliable timezone/offset is available. Do not fabricate a timezone for shifted dates or use calendar date as a patient identifier. Preserve time-of-day meaning when harmonizing data.

Bolus dose and basal rate are different quantities; integrate a basal rate over known delivered intervals before combining doses. A configured basal schedule is not automatically delivered basal. IOB and COB are optional modeled quantities with separate parameters and provenance, not measured ground truth.

Separate output table:

```text
sample_id, patient_id, index_time, history_start, horizon_minutes,
input_eligible, eligibility_reason, future_observed_count,
label_status [known|unknown], label [0|1|null], source_split, fold_id
```

Outcome tables and episode annotations never enter node features, topology, fitted imputers or graph embeddings. Use sample_id to join predictions to outcomes only in training loss/evaluation.

Before adapter implementation, document raw field name, source meaning, units, clock precision, duplicate policy, interval semantics, availability metadata, and missingness behavior for each release. Verify timestamp monotonicity, patient separation, dose/rate units, record duplication and source split boundaries.

Additional source check from the novelty investigation: OhioT1DM's published patient weight of 99 is a placeholder, not a measured weight; exclude it from phenotype inputs. Event timestamps in the described XML schema do not establish first-usable timestamps for every field. Verify the actual release before claiming a measured arrival-time study. [Dataset paper, section 3](https://webpages.charlotte.edu/rbunescu/data/ohiot1dm/bglp/OhioT1DM-dataset-paper.pdf).
