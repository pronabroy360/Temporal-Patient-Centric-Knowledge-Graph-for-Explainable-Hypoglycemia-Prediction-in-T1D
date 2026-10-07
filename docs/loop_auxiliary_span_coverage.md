# Loop auxiliary-event coverage within CGM spans

Status: completed 13 September 2026. The identifier-free [aggregate report](../audit/loop_event_span_coverage.json) uses protected CGM observation spans from the final patient-level audit.

| Modality | Participants with at least one record | Raw records within CGM spans | Median records per participant | Range |
|---|---:|---:|---:|---:|
| Basal | 835 / 835 | 47,943,156 | 55,528 | 36–149,175 |
| Bolus | 835 / 835 | 2,684,815 | 2,608 | 3–34,640 |
| Nonempty reported carbohydrate | 835 / 835 | 1,398,879 | 1,573 | 2–10,499 |

No malformed UTC timestamps were found in the selected auxiliary-event rows. The protected per-participant counts are stored in `private/loop_multimodal_span_summary.json`.

These are raw source-event counts within a participant's overall CGM observation span. They do not establish that every event is aligned with an eligible prediction index, that it was available at prediction time, or that duplicate/version resolution has been applied at the event level. The release lacks adequate observed arrival timestamps, so the primary benchmark continues to use the explicit `assumed_immediate` availability assumption and reserves delayed auxiliary events for simulation.
