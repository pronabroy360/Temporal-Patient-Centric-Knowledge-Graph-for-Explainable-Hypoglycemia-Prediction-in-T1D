# Loop bolus, food, and exercise canonical audits

Status: completed 13 September 2026. Identifier-free reports: [bolus](../audit/loop_bolus_canonical_audit.json), [food](../audit/loop_food_canonical_audit.json), and [exercise](../audit/loop_exercise_canonical_audit.json). Each used the bounded 64-way participant-hashed audit and removed its temporary minimal-column partitions at completion.

| Modality | Raw rows | Exact duplicates removed | Canonical rows retained | Differing same-time timestamps retained |
|---|---:|---:|---:|---:|
| Bolus | 2,722,513 | 304,614 | 2,417,899 | 4,337 |
| Food | 1,406,204 | 13,549 | 1,392,655 | 2,281 |
| Exercise | 51,728 | 4,800 | 46,928 | 794 |

Differing same-time non-CGM records remain distinct. This avoids unsupported assumptions about corrected carbohydrate reports, planned versus delivered boluses, or concurrent exercise records. The later adapter must map their release-specific semantics with explicit provenance; it must not merge them just because their timestamps match.

All five modality-specific canonical audits are now complete. The remaining data gate is a cross-modality participant-level coverage audit that applies the frozen CGM exclusion policy and reports eligible observation periods and event counts without constructing prediction windows.
