# Loop confirmed and censored hypoglycemia episode audit

Status: completed 13 September 2026. The identifier-free [aggregate report](../audit/loop_cgm_episode_cohort_flow_v2.json) applies the development-frozen ±1-second cadence rule to the 835-person multimodal candidate pool. Protected per-participant counts remain in `private/`.

| Low-run category | Count |
|---|---:|
| Confirmed episode onsets | 250,639 |
| Boundary-censored low runs | 432,023 |
| Fully observed but short unconfirmed low runs | 68,282 |

Confirmed episodes require three consecutive low readings, an observed preceding non-low reading, and three observed non-low readings for recovery. Boundary-censored runs lack sufficient observed onset or recovery context. Short unconfirmed runs have observed boundaries but do not meet the three-reading definition.

Confirmed episodes occur for 834 of the 835 candidate participants. These counts establish sufficient observed outcome events for later patient-level evaluation. They do not indicate symptomatic events, intervention need, or a model result.

The categories reconcile to the earlier combined non-confirmed count: 432,023 + 68,282 = 500,305.
