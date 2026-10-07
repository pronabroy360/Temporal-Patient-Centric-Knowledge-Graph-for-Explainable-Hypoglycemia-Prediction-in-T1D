# Loop cross-modality eligibility gate

Status: completed 13 September 2026. This gate combines the original identifier-free [modality intake](../audit/jaeb_modality_coverage.json) with the complete [canonical-audit validation](loop_canonical_audit_validation.md).

## Cohort flow

| Requirement | Participants retained |
|---|---:|
| Loop roster | 919 |
| Any CGM source rows | 851 |
| Non-conflicting canonical CGM after calibration/conflict exclusions | 851 |
| CGM plus basal source presence | 845 |
| CGM plus bolus source presence | 845 |
| CGM plus nonempty reported carbohydrate presence | 837 |
| **CGM, basal, bolus, and nonempty reported carbohydrate presence** | **835** |
| Exercise presence, a secondary modality | 493 |

The **835 participants** are the provisional multimodal candidate pool. This is an availability and source-presence gate, not the final analytic cohort.

## Why the canonical audits preserve this inference

For basal, bolus, food, and exercise, canonicalization removes only exact duplicates and retains one representative, so it cannot remove a participant with at least one qualifying raw record. Differing same-time non-CGM records are also retained. The independent CGM audit establishes non-conflicting canonical readings for all 851 source-CGM participants. This does not establish numeric or physiological validity. Therefore the earlier source-presence intersection is still valid after the frozen canonical policies.

## Remaining eligibility gate

The candidate pool must next be filtered by participant-level temporal criteria: sufficient usable-CGM observation span, acceptable gaps, valid history and future-label windows, and non-censored confirmed low episodes. Event presence is not evidence that an event was recorded throughout the observation period, and no current result claims that all 835 participants will supply valid prediction windows.
