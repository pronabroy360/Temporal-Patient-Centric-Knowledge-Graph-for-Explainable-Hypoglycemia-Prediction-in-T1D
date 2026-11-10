# Exploratory event-attribution sensitivity audit

Updated: 29 October 2026.

## Question and scope

This exploratory audit asks whether a small set of event tokens selected by
single-event deletion sensitivity changes the frozen graph model's prediction
differently from equally sized event sets matched on modality composition.
It is not a clinical explanation study or an independent test of attribution
faithfulness: top events are selected using the same single-event deletion
measure that motivates the subsequent joint-deletion comparison.

The audit used the `graph-generic` epoch-1 checkpoint for outer-0, seed
`20261005`. The deterministic sample contains at most two event-containing
windows per participant and label, selected by hash priority. It includes 518
windows (258 positive, 260 negative) from all 130 validation participants.
The full validation scan reconciled 8,885,621 windows and 274,044 positive
labels with the saved run. The development cache/window identity matched the
checkpoint contract; no locked holdout was used and no identifiers were
emitted.

## Method

For each sampled window, each active event was removed individually and the
change in predicted probability was measured. The three events with the
largest absolute single-event deletion effect were selected. Their joint
deletion and retention effects were compared with 20 random sets of the same
size and exact modality counts. Random sets were not matched on event age,
value magnitude, or other event attributes. Participant-cluster bootstrap
intervals condition on this sample and the one fitted model.

The first implementation attempted gradient-times-input attribution, but
back-propagation fails through the model's in-place graph aggregation. That
attempt produced no report. The completed analysis uses deletion sensitivity
instead; the method and result below do not use gradient attribution.

## Result

For joint deletion, the participant-average absolute probability change was
0.003943 larger for the top-attribution sets than for modality-matched random
sets (participant-cluster bootstrap 95% interval 0.003266 to 0.004665). The
window-average difference was 0.003957. This comparison is selection-
conditioned because individual deletion effects were used to select the top
events; it should not be read as an independent faithfulness test.

For retention, the participant-average absolute difference from the original
prediction was 0.003841 larger for random retained sets than for top sets
(95% interval 0.003203 to 0.004525); the window-average difference was
0.003856. This is evidence that the selected tokens are locally sufficient
for this model's output under this masking protocol, not evidence that the
tokens are clinically correct or complete. The mean signed change
`p(original) - p(after deleting top events)` was −0.004740, so deleting those
events raised predicted risk on average in this selected sample. This signed
average is not an effect on actual hypoglycemia risk.

The results are one checkpoint, one fold, one seed, one sampling rule and a
retrospective immediate-availability assumption. They measure model
sensitivity, not causal effects, explanation completeness, patient
understanding, clinical usefulness or graph-relation benefit. Source digests
differ from the historical training source, although input contracts and
validation window identity were verified. Do not generalize beyond this fixed
checkpoint.

## Artifact and reproduction

Aggregate output:
[`loop_graph_event_explanation_faithfulness_outer0_seed20261005_20261029_v2.json`](../audit/loop_graph_event_explanation_faithfulness_outer0_seed20261005_20261029_v2.json).

Implementation:
[`audit_graph_event_explanation_faithfulness.py`](../scripts/audit_graph_event_explanation_faithfulness.py).

Run from the repository root with the verified private cache and epoch-1
checkpoint using the command recorded in the implementation history. The
report contains aggregate metrics and contract digests only; it does not save
patient-level or event-level scores.

## Next research gate

Treat this as a development diagnostic. A stronger explanation evaluation
should use an attribution score independent of the perturbation metric, or a
prespecified split between attribution selection and perturbation evaluation;
match random controls on recency and value as well as modality; replicate
across folds and seeds; and separately assess provenance correctness and
blinded clinical usefulness. Keep the locked holdout sealed until the
explanation protocol and model selection are frozen.
