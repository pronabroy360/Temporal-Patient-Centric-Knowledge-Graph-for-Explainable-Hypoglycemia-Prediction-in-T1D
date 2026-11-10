# Frozen Loop CGM model transfer to DCLP3 and DCLP5

**Date:** 31 October 2026  
**Status:** exploratory no-refit CGM-only transfer diagnostic; not a graph replication  
**Holdout:** the protected Loop holdout remains unopened

## Purpose and protocol

Five complete two-epoch Loop outer-fold logistic models, each using current CGM
and recent CGM slope, were replayed without fitting, tuning, or recalibration
on DCLP3 and DCLP5. The models share the same feature contract, training
source digest, manifest digest, and optimizer configuration. Each DCLP cohort
was parsed once per timestamp policy. Candidate examples require a contiguous
two-hour five-minute CGM history and a fully observed 30-minute future; the
label is any future CGM below 70 mg/dL. Participant-macro average precision
(AP) and Brier score are reported, with fixed-prediction participant bootstrap
intervals. Comparisons are paired within participant against a persistence-
slope rule and a constant training-prevalence reference.

The DCLP5 raw and adjusted-preferred runs are policy sensitivities. Neither
timestamp policy is established as correct. DCLP3 uses its available raw CGM
timestamps. No patient identifier is emitted in the public aggregate outputs.

## Results

| Cohort / CGM timestamp policy | Eligible windows | Positive labels | Positive prevalence | Frozen-model participant-macro AP, folds 0–4 (range) | Persistence AP | Frozen-model participant-macro Brier, folds 0–4 (range) | Persistence Brier |
|---|---:|---:|---:|---:|---:|---:|---:|
| DCLP3 / raw | 7,930,123 | 241,856 | 3.05% | 0.688–0.738 | 0.355 | 0.01619–0.01689 | 0.03632 |
| DCLP5 / raw | 5,113,177 | 168,370 | 3.29% | 0.506–0.576 | 0.239 | 0.01977–0.02041 | 0.06132 |
| DCLP5 / adjusted-preferred | 5,123,158 | 168,656 | 3.29% | 0.505–0.575 | 0.239 | 0.01976–0.02041 | 0.06132 |

Every one of the five frozen models has higher participant-macro AP and lower
participant-macro Brier than persistence in each cohort/policy run. In all
three cohort/policy runs, the participant-paired AP improvement and Brier
reduction intervals exclude zero for each of the five models. These intervals
describe participant resampling conditional on each saved model and fixed
predictions; they do not represent model refitting, independent-cohort, or
timestamp-policy uncertainty.

Outer-2 is consistently weaker in AP than the other folds, while preserving
the direction against persistence. The five fold replays use the same external
participants and are not five independent replications. Report the per-fold
spread; do not average folds as though they were independent studies.

## Interpretation and limits

This supports a narrow statement: a frozen Loop CGM logistic predictor
transfers some ranking and probability skill to these DCLP release-local CGM
endpoints, relative to the specified persistence rule, under the audited
eligibility policies. It does **not** establish clinical utility, comparable
labels across studies, or transportability of insulin/event relations. The
models only consume CGM level and slope, so these results do not validate the
temporal graph or knowledge-graph hypothesis.

The target is a release-specific future-CGM threshold, not an adjudicated
clinical hypoglycemia episode. DCLP clock semantics, event-time mapping,
basal-state reconstruction, event availability, and exact event feature
parity remain unresolved. DCLP3/DCLP5 have no usable carbohydrate records in
the screened Roche meter tables. Do not select timestamp policy or revise the
model based on these external scores.

## Reproduction artifacts

- Evaluator: [`scripts/evaluate_frozen_loop_cgm_logistic_on_jaeb.py`](../scripts/evaluate_frozen_loop_cgm_logistic_on_jaeb.py)
- Evaluator SHA-256 recorded in each output: `a0fed2d0d9822cea5ed3f6798c6d4a6a4a54a943d992ddd6bab8518e7f411ee8`
- DCLP3 raw: [`audit/dclp3_frozen_loop_cgm_logistic_transfer_raw_20261031_v3.json`](../audit/dclp3_frozen_loop_cgm_logistic_transfer_raw_20261031_v3.json)
- DCLP5 raw: [`audit/dclp5_frozen_loop_cgm_logistic_transfer_raw_20261031_v3.json`](../audit/dclp5_frozen_loop_cgm_logistic_transfer_raw_20261031_v3.json)
- DCLP5 adjusted-preferred: [`audit/dclp5_frozen_loop_cgm_logistic_transfer_adjusted_20261031_v3.json`](../audit/dclp5_frozen_loop_cgm_logistic_transfer_adjusted_20261031_v3.json)

The earlier v2 artifacts preserve the single-fold outer-0 analysis. The v3
artifacts supersede them for the five-fold frozen-model comparison.
