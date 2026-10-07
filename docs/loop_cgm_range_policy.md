# CGM range policy

The Loop audit found numeric values from approximately 1 to 592 mg/dL. That
range alone does not establish a device-validity cutoff, so the primary policy
is `observed_numeric`: retain every numeric value after the release-specific
duplicate and calibration rules.

The code also defines `sensitivity_20_600` and `sensitivity_40_400`. These are
development comparisons only. They quantify how a bounded-value rule changes
window eligibility, prevalence, and episode counts; they are not clinical
validity claims. A bounded rule can become primary only after a documented
device/domain justification and a pre-specified development decision.

`filter_cgm_events` applies a selected policy as a streaming operation. It
filters only CGM events and passes insulin/meal/other modalities through
unchanged, so sensitivity analyses cannot accidentally alter auxiliary-event
capture or provenance.
