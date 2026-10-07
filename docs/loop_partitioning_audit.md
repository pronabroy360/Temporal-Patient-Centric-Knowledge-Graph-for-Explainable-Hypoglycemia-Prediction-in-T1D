# Loop participant-contiguity audit

Status: completed 10 September 2026. The identifier-free report is [loop_participant_runs.json](../audit/loop_participant_runs.json), produced by `scripts/audit_loop_participant_runs.py`.

## Finding

Loop source files are **not participant-contiguous**. A one-pass group-by-participant transform would omit later runs for nearly every participant and is invalid for the duplicate and coverage audit.

| Modality | Rows | Participants | Participants with more than one source run | Total source runs | Largest number of runs for one participant |
|---|---:|---:|---:|---:|---:|
| CGM | 111,118,148 | 851 | 850 | 131,979 | 286 |
| Basal | 48,301,308 | 845 | 840 | 113,559 | 285 |
| Bolus | 2,722,513 | 845 | 840 | 113,000 | 283 |
| Food | 1,406,204 | 837 | 831 | 110,675 | 285 |
| Exercise | 51,728 | 493 | 422 | 15,877 | 245 |

This confirms that the previous source-adjacent duplicate counts are lower bounds and that a participant-sorted audit remains necessary.

## Consequence and safe next implementation

The release occupies about 19 GB. A full raw duplicate is prohibited. The completed [minimal-column footprint audit](loop_partition_footprint.md) measured 9.70 GiB of projected partition data with 48 GiB free, permitting a one-modality-at-a-time local audit with a two-copy safety allowance. It must use only canonical-key fields, UTC time, `RecID`, and provenance IDs; delete only disposable partitions after each aggregate report; and stop if the safety floor is reached.

Do not construct windows, labels, or models until that partitioned audit has produced final duplicate, conflicting-CGM, and coverage counts. The availability-time sensitivity analysis remains a prespecified simulated delay of auxiliary events; it cannot use Loop upload timestamps as observed arrival times.
