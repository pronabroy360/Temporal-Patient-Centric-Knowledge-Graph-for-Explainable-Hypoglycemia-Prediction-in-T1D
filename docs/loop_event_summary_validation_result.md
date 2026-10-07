# Loop recorded-event summary validation result

The first corrected recorded-event summary model was evaluated on the same
outer-0 validation participants and exact windows as the selected two-feature
CGM logistic model. It used the conservative
`recorded-events-v2-open-history-normal-bolus` contract and the CGM-selected
optimizer without further event-model tuning.

| Model | Participant-macro AP | Pooled Brier |
|---|---:|---:|
| CGM logistic | 0.457055 | 0.022880 |
| CGM + recorded-event summary logistic | 0.425768 | 0.023462 |

The paired event-minus-CGM AP difference is −0.031288. Its 95% percentile
interval from 2,000 participant resamples is [−0.037799, −0.025438]. Event AP
is higher for 17 participants and lower for 113. The pooled Brier difference
is +0.000582, where a positive difference is worse. Participant-macro Brier
is worse for 114 participants and better for 16; its paired difference
interval is [+0.000461, +0.000703].

The comparison covers 130 participants, 8,885,621 windows, and 274,044
positive labels. The archive comparator verified identical participant,
timestamp, and label rows before calculation. The interval reflects fixed
prediction variation across participants and does not include model-refitting
uncertainty.

This is negative evidence for this specific fourteen-feature summary model.
It does not establish that recorded events or relations contain no predictive
information. The representation compresses event sequences, the optimizer was
selected for a two-feature CGM model, and actual event availability is not
measured. Do not evaluate it on other development-test folds or the locked
holdout in its current form.

The next diagnostic must retain the same CGM rows and event records while
testing whether individual-event timing improves over these summaries. A
nested event contribution or sequence comparator should begin from the frozen
CGM predictor, so adding event inputs cannot be confused with relearning a
worse CGM decision surface. Any event-model tuning remains development-only
and must be recorded before wider evaluation.

Sources: `audit/loop_event_logistic_outer0_validation_v2.json` and the corrected
paired comparison `audit/loop_event_vs_cgm_outer0_validation_v3.json`.
The earlier `v2` comparison file has correct numerical differences but
ambiguous direction labels for Brier and is superseded by `v3`.
