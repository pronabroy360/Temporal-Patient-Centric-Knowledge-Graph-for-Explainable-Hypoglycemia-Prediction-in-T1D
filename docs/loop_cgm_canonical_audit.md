# Loop participant-sorted CGM canonical audit

Status: completed 13 September 2026. The identifier-free [aggregate report](../audit/loop_cgm_canonical_audit.json) was produced by `scripts/audit_loop_partitioned_cgm.py` using a 64-way participant-hashed projection, UTC sorting within each partition, and automatic temporary-file cleanup.

## Final CGM canonicalization counts

| Measure | Count |
|---|---:|
| Raw CGM-table rows | 111,118,148 |
| Exact duplicates removed | 19,628,647 |
| Canonical rows, including calibration | 91,489,501 |
| Canonical calibration rows excluded | 58,403 |
| Ambiguous CGM timestamps excluded | 2,226,685 |
| Usable canonical CGM timestamps | 86,977,148 |
| Participants with non-conflicting canonical CGM | 851 |

All 851 observed CGM participants retain non-conflicting canonical CGM. Counts range from 3,757 to 258,190 timestamps per participant. The largest within-participant gap ranges from 10,501 seconds to 17,711,929 seconds, confirming that later patient-level eligibility and gap rules are necessary. These are not yet clinical-validity or exact-grid eligibility counts.

## Frozen rule and consequence

Exact re-exports are collapsed to the lowest `RecID`; calibration rows are excluded; and every same-participant, same-UTC timestamp with differing canonical CGM values is excluded from primary inputs, targets, recovery checks, episode confirmation, and grid alignment. This rule is now supported by a complete participant-sorted audit rather than the earlier source-adjacent lower bound.

The CGM audit is complete, but patient windows cannot yet be built: the basal, bolus, food, and exercise tables still need the same complete canonical duplicate audit, followed by the combined modality and coverage eligibility audit. Upload timestamps remain unsuitable as observed availability times.
