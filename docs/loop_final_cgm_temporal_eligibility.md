# Loop final CGM temporal eligibility audit

Status: completed 13 September 2026. The [machine report](../audit/loop_cgm_final_temporal_eligibility.json) applies the development-frozen ±1-second cadence rule to the 835-person multimodal candidate pool. It contains no participant identifiers and removed all temporary partitions after completion.

| Metric | Count |
|---|---:|
| Non-conflicting numeric CGM timestamps in the candidate pool | 86,418,499 |
| Complete 30-minute future labels | 69,115,895 |
| Protocol-style input-eligible indices | 61,446,087 |
| Positive 30-minute future-low labels | 4,139,028 |
| Positive-label prevalence among complete futures | 5.99% |

Every one of the 835 candidate participants has at least one logical-grid input-eligible index at both 30 and 60 minutes. The 60-minute audit yields 63,027,387 complete labels and 5,411,877 positive future-low labels (8.59% prevalence). Input eligibility is identical by horizon because it depends only on information at the prediction index.

The input-eligible count is 71.1% of retained candidate-pool CGM timestamps. This establishes strong CGM outcome feasibility after the frozen chronology rule.

## Limits of this result

This is a CGM eligibility result, not a final analytic cohort or model result. Confirmed/censored low episodes, physiological range exclusions, and time-aligned basal/bolus/food coverage remain required before the shared final window manifest can be frozen.
