# Corrected pilot recovery

The 15 September review found a tied-score AP defect. The code corrections are
implemented and tested. Corrected outer-0 release-backed validation is now
complete and again selects two epochs at learning rate 0.002. Historical AP
reports remain superseded and their original JSON files are preserved. See the
[corrected validation result](loop_cgm_corrected_validation_result.md).

## Implemented corrections

- Threshold-grouped AP (`threshold-grouped-ap-v2`); reports include each
  model's AP-defined participant denominator. Fold aggregation rejects old
  metric reports and weights AP by that denominator.
- Both pilots include a constant training-prevalence Brier reference, with its
  probability estimated exclusively from training rows. The binary rule is
  not a calibrated probability model.
- Manifest validation enforces holdout separation and complete fold coverage.
- Both pilots verify ordered participant/timestamp/label hashes against the
  frozen 30-minute window index before fitting and report the verified hash.
- Both pilots save model coefficients, standardization, source hash, revision,
  arguments, and compressed participant predictions under `private/pilot_runs`.
  Existing reports and run directories cannot be overwritten. Incomplete
  archives cannot be rescored. `scripts/rescore_loop_pilot.py` supports future
  metric corrections without repeating training.
- Missing source files fail before partitioning. Partition writes check free
  space every 10,000 rows; sorting retains its safety check. Thresholds are
  safety margins, not predictions of the required disk footprint.
- Tests are no longer ignored by Git. New tests include both complete pilot
  executions on a tiny synthetic release and equality after archive rescoring.

## Conservative event contract

Policy `recorded-events-v2-open-history-normal-bolus` uses `(t−120 minutes,t]`.
There are two CGM features and twelve recorded-event features. Extended bolus
totals are excluded; only the recorded normal component contributes to dose
summaries. Missing amounts are accompanied by missing-count features.
Unsupported carbohydrate units preserve event presence but contribute no
known grams and increase the missing-count feature.

The latest reported basal rate is used only if all retained records at its
timestamp agree on a known numeric rate. Otherwise a zero placeholder and an
explicit unresolved indicator are emitted. It is a reported rate, not a
reconstruction of delivered basal insulin. Distinct retained meal/bolus
records remain recorded entries, not verified unique physiological events.

After sorting records, running sums and queues avoid repeated active-window
summation. This changes the feature policy and requires fresh event results.
Earlier inclusive-boundary event-coverage counts remain historical audits;
do not claim they measure this new feature contract exactly.

Actual record availability is not recoverable from this release's failed
upload linkage. These features therefore remain an explicitly optimistic,
retrospective occurrence-time replay. This code change cannot establish real
availability; simulated delays and deployment claims remain separate studies.

## Completed recovery and next computation

Corrected validation, feature-cache construction, all five development-test
folds, prediction archives, and aggregation are complete. The corrected CGM
reference is participant-macro AP 0.446938 and pooled Brier 0.021590; see the
[five-fold result](loop_cgm_corrected_development_result.md). The old AP-based
reports remain suspended.

The next computation is the outer-0 recorded-event validation in
[the event-pilot protocol](loop_event_logistic_pilot.md). The event runner now
reuses the verified CGM cache and only partitions the auxiliary event tables.

The five-fold summary is exploratory because global choices used development
participants. Holdout records have been scanned for aggregate audits, but
must remain excluded from model fitting and predictive evaluation until the
complete protocol is frozen.

After correction, planned scientific work still includes stronger baselines,
calibration, paired participant intervals,
episode metrics, capacity-matched graph controls and external validation.
Those experiments were not completed by the software fixes.
