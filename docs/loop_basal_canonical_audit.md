# Loop participant-sorted basal canonical audit

Status: completed 13 September 2026. The identifier-free [aggregate report](../audit/loop_basal_canonical_audit.json) was produced by `scripts/audit_loop_partitioned_events.py` with the `basal` modality.

| Measure | Count |
|---|---:|
| Raw basal rows | 48,301,308 |
| Exact duplicates removed | 108,998 |
| Canonical basal rows retained | 48,192,310 |
| Same-participant, same-UTC timestamps with differing basal records | 111,314 |

The 111,314 differing same-time records are retained as distinct candidate pump-state records. They may represent concurrent, superseded, scheduled, temporary, automated, or suspend states; merging them by timestamp would invent a source-version interpretation. Their clinical interval semantics remain an adapter and domain-review task before basal features are constructed.

Temporary minimal-column partitions were automatically removed. The remaining canonical audits are bolus, food, and exercise, followed by cross-modality coverage and patient-window eligibility.
