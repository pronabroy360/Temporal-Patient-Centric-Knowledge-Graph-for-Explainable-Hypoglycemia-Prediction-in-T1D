# Loop temporal eligibility audit specification

Status: frozen audit contract, 13 September 2026. This applies the general [research protocol](research_protocol.md) to the completed Loop canonical policies. It is not yet a patient-window result.

## Inputs

Use only non-conflicting canonical CGM timestamps from the [CGM audit](loop_cgm_canonical_audit.md): `RecordType=CGM`, excluding calibration and every conflicting same-participant/UTC reading. Numeric and physiological validity, cadence, and final eligible-window counts are separate audit outputs. Treat `UTCDtTm` as UTC occurrence time. Retain native timestamps exactly; do not round or interpolate readings onto the 5-minute grid.

Loop CGM values are recorded in mmol/L. Convert to mg/dL using 18.0182 only after canonicalization and preserve the original value/unit in provenance. The primary low threshold is therefore strictly below 3.88497 mmol/L, equivalent to strictly below 70 mg/dL; a value exactly at the converted threshold is not low.

## Audit quantities per participant

1. First and last usable canonical CGM timestamp; elapsed observation span.
2. Count of usable CGM readings; adjacent gaps; longest gap; count and duration of gaps exceeding 15 minutes.
3. Native five-minute grid timestamps. The completed cadence audit shows frequent 299/301-second device-clock jitter, so exact 300-second matching is retained as a strict sensitivity diagnostic. Select a one-reading-per-slot assignment tolerance on development participants before the primary audit, retain the observed offset and provenance, and reject ambiguous ties. Do not interpolate values or create targets.
4. Candidate 30- and 60-minute labels: all six or twelve exact future slots must exist. Missing futures remain unknown.
5. Input eligibility at each candidate index: 24 history slots from `t−115` through `t`, at least 22 observed, no more than two consecutive missing, and observed recovery readings at `t−10`, `t−5`, and `t` all at or above threshold.
6. Confirmed and censored low episodes using the protocol's three consecutive exact 5-minute low readings. A gap breaks confirmation.

## Cohort flow to report

Report only aggregate participant counts in the public audit artifact: 835 multimodal candidates; participants with at least one 30-minute complete-future candidate; participants with at least one input-eligible 30-minute index; participants with at least one known 30-minute label; and participants with at least one confirmed low episode. Repeat the complete-future and known-label counts for 60 minutes.

Record per-participant quantities only in a protected local derived artifact if needed for fold construction. Do not export participant identifiers or clinical timelines in public reports. No model, label file, or graph may be constructed until this audit has completed and its cohort flow is reviewed.
