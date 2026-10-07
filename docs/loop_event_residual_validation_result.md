# Frozen-CGM event residual: outer-0 validation result

Status date: 16 September 2026. This is a development-only result. The
development-test and locked-holdout participants were not scored.

## Design

The residual diagnostic used the protected CGM feature cache and canonical
event-instance cache, both tied to model-manifest checksum
`69b41e4acfae7d2afc990c8cd15d8fc3f969784d4e5f6534a9263033d341ad52` and
frozen window identity
`26036d7d3d27c21a4407d15aacd916b98ba598dfded5da319288a74b54a592aa`.

It held the two-feature outer-0 CGM logistic predictor immutable and fitted an
additive event-only logit branch across the prespecified twelve combinations:
two variants, L2 values `1e-4`, `1e-3`, `1e-2`, and one or two epochs. All
used retrospective occurrence-time replay with immediate availability assumed,
not measured.

All candidates had the same 130 validation participants, 8,885,621 windows
and 274,044 positive labels. The archived frozen-CGM scores exactly reproduced
the prior validation reference: participant-macro AP 0.457055 and pooled
Brier 0.022880. This verifies that the residual cache join did not alter the
CGM cohort, labels or predictor.

## Selected development candidate

The prespecified validation rule selected the presence/quality residual with
L2 0.01 and two epochs:

| Model | Participant-macro AP | Pooled Brier |
|---|---:|---:|
| Frozen CGM | 0.457055 | 0.022880 |
| Selected event residual | 0.444091 | 0.022503 |
| Residual minus CGM | −0.012965 | −0.000377 |

The residual Brier improvement does not offset its ranking loss under the
prespecified selection priority of participant-macro AP.

The paired participant-bootstrap comparison used 2,000 draws of fixed,
aligned predictions. The AP difference (residual minus CGM) was −0.012965,
with a 95% interval of [−0.015520, −0.010363]; 115 of 130 participants had
lower AP under the residual. Participant-macro Brier changed by −0.000389,
with a 95% interval of [−0.000501, −0.000286]; 106 participants had lower
Brier. These are predictive associations under the recorded-event replay
contract, not causal effects or evidence of real-time availability.

The full selection table is in
`audit/loop_event_residual_outer0_selection.json`. The paired report is in
`audit/loop_event_residual_outer0_best_vs_frozen_cgm.json`. The source files
have an `outerv0` filename typo, but each report's embedded fold is `outer-0`;
the selection tool verified matching fold, manifest, window identity and
outcomes before accepting them.

## Interpretation and decision

Neither tested linear summary residual demonstrated incremental recorded-event
ranking value beyond the frozen CGM model. This closes the linear-residual
branch: do not evaluate it on the development-test or locked holdout.

The result does not yet decide whether individual event timing, subtype and
nonlinear interactions matter. The justified next experiment is the
prespecified individual-event sequence comparator on outer-0 validation. It
must use the same canonical instances, history window, cache compatibility
checks and occurrence-time availability limitation. A graph model remains
unjustified until that information-matched sequence comparator has been
tested.
