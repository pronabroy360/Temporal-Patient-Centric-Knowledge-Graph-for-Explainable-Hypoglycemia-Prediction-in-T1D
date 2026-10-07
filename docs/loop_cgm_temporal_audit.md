# Loop CGM cadence and temporal eligibility audit

Status: completed 13 September 2026. The identifier-free [machine report](../audit/loop_cgm_temporal_audit.json) was generated from the full participant-hashed, UTC-sorted canonical CGM scan. Temporary partitions were removed on completion.

## What the audit establishes

After exact duplicate removal, calibration exclusion, same-timestamp conflict exclusion, and finite mmol/L parsing, the release contains **86,977,148 non-conflicting numeric CGM timestamps**. This is a numeric/unit check, not a physiological-validity assessment.

The most common adjacent cadence is 300 seconds (52,299,755 transitions), but 299 seconds (14,367,919) and 301 seconds (12,048,771) are also frequent. Smaller one-, two-, and five-second transitions and occasional approximately ten-minute gaps occur as well. Therefore an exact-300-second grid is a useful strict diagnostic but is not an acceptable unexamined final rule: it would turn ordinary device-clock jitter into apparent missingness.

| Strict exact-grid 30-minute diagnostic | Result |
|---|---:|
| Participants with at least one complete-future candidate | 850 / 851 |
| Participants with at least one input-eligible index | 849 / 851 |
| Complete future labels | 21,215,215 |
| Input-eligible indices | 13,064,186 |
| Positive future-low labels | 1,315,978 |

These counts cover the CGM cohort, not the 835-person multimodal intersection. They establish that the outcome task is feasible, but they do not yet select the final analytic cohort or prove simultaneous event coverage.

## Required correction before window construction

Choose and document a per-interval cadence tolerance using development participants only, then rerun the temporal audit with that frozen tolerance and an exact-grid sensitivity analysis. Do not anchor a participant's series to a global clock phase: the first development implementation exposed that this would reject valid series with a different phase. The tolerance must retain observed timestamps and offsets, reject unresolved duplicate timestamps, and apply identically to every model. No interpolation may create targets or labels.
