# Event-input ablation in the temporal graph model

## Result — outer-0, seed 20261004

The generic temporal graph was compared with an otherwise matched branch that
zeros all event features before constructing the graph. Both were trained for
one epoch on the same outer-0 development split with the same seed, optimizer,
batch size, source-code digest, 36,883 declared parameters, and 8,885,621
validation windows from 130 participants. Both run archives report complete
training and verified prediction-window identity. The locked holdout was not
used.

The generic graph scored participant-macro AP **0.473613** and macro Brier
**0.022045**. The event-disabled branch scored AP **0.470813** and Brier
**0.022246**. The paired generic-minus-disabled AP difference was **+0.002800**
(10,000-draw participant-bootstrap 95% interval **[+0.001996, +0.003609]**);
AP was higher for the generic model on 94/130 participants. The paired macro-
Brier difference was **−0.0002003** (interval **[−0.0002411, −0.0001597]**);
Brier was lower for the generic model on 111/130 participants.

This is preliminary evidence that recorded event inputs help this generic
graph predictor on this fold. It is not evidence that clinical relation
semantics help: the control removes all event information and all event-to-CGM
edges at once. The models have equal declared parameter counts, but the
disabled model's event encoder and edge experts receive no event-derived
gradients, so their effective trained capacity differs. The participant
bootstrap conditions on these fixed fits and does not quantify retraining,
seed, fold, or study uncertainty. Event availability is replayed by occurrence
time with immediate availability assumed, not measured.

The protected run archives are under
`private/mps_research/outer0_seed20261004_graph_generic_event_ablation_v2`
and
`private/mps_research/outer0_seed20261004_graph_event_disabled_v1`. The
identifier-free paired result is
[`audit/loop_relation_event_ablation_outer0_seed20261004_paired_20261025.json`](../audit/loop_relation_event_ablation_outer0_seed20261004_paired_20261025.json).
The exact comparison command was:

```bash
PYTHONPATH=src:scripts python scripts/compare_full_history_relation_ablation.py \
  private/mps_research/outer0_seed20261004_graph_generic_event_ablation_v2 \
  private/mps_research/outer0_seed20261004_graph_event_disabled_v1 \
  --draws 10000 --seed 20261020 \
  --output audit/loop_relation_event_ablation_outer0_seed20261004_paired_20261025.json
```

## Next discriminating experiment

Replicate the event ablation on additional patient-disjoint folds and at least
one additional seed. Separately compare the real event-to-CGM endpoint
assignment with a prespecified causal endpoint perturbation that retains the
same event records, event timestamps, CGM history, model capacity, and training
budget. This can test whether the chosen temporal connectivity contributes
beyond event content. The current result does not establish the novelty of a
temporal patient-centric knowledge graph; continue to withhold that claim until
relation-specific controls and explanation-faithfulness evaluation are done.
