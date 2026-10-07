# Controlled neural first gate: verified outer-0 result

The completed Kaggle bundle was recovered and independently checked against
its reported SHA256
`100f046deabaf733d2bc27f8ae1537dcc88f892da9d2a1f4d489544b03aa61bd`.
The ZIP passes its integrity test. All 386 extracted files match the archive
in size and CRC; none is missing. The campaign records both `cgm-mlp` and
`clean-gru` as complete after two epochs. Each model has 130 protected
participant-prediction files and epoch-1 and epoch-2 checkpoints. Both training
logs record the completed epochs without a reported error.

The protected predictions pair exactly on participant, index time, and label
for **8,885,621** outer-0 validation windows from **130** participants, with
274,044 positive labels. The comparison independently recomputes the metrics
from those predictions and reconciles them with both result records. The
models share the frozen manifest, window and input-content identities, seed
20261002, configuration, and source fingerprint.

| Development-validation metric | CGM-only MLP | Clean event GRU | CGM minus event |
|---|---:|---:|---:|
| Participant-macro average precision, higher better | 0.48160 | 0.46933 | +0.01227 |
| Participant-macro Brier, lower better | 0.02112 | 0.02158 | −0.00046 |
| Pooled Brier, lower better | 0.02076 | 0.02122 | −0.00047 |

For participant-macro AP, the paired 95% percentile interval for **CGM minus
event** is **[+0.01037, +0.01414]**; the CGM-only model is higher for 111 of
130 participants. For participant-macro Brier, the paired interval is
**[−0.00054, −0.00038]**; CGM-only is lower for 116 participants. These
intervals resample participants with **fixed predictions**. They do not account
for model-training variability, hyperparameter selection, or external cohorts.
The machine-readable aggregate outputs are
`audit/loop_controlled_first_gate_bundle_validation_2026_10_05.json` and
`audit/loop_controlled_first_gate_paired_2026_10_05.json`.

This one-fold, one-seed **development** gate provides no evidence that the
available event sequence improves prediction over a capacity-similar nonlinear
CGM control. It does not establish that clinical events are uninformative in
general. Both models receive only current glucose and recent slope, rather
than the complete CGM history; optimization and architecture adequacy remain
open. Neither model encodes explicit temporal knowledge-graph relations, so
this is not a test of the proposed graph contribution. The event availability
assumption remains retrospective occurrence-time replay, with immediate
availability assumed rather than measured. Keep the locked holdout closed.

Next, audit model convergence and implement a stronger full-CGM-history
comparator on the same frozen windows. Version any changed training plan as
development selection, then run the declared seed replications and diagnostic
event ablations before deciding whether to invest in graph relations. The
paired analysis can be reproduced with
`scripts/compare_controlled_neural_archives.py`, passing the `cgm-mlp` run
directory first and the `clean-gru` run directory second. The comparator's
fixture tests pass, and it has now run on the recovered research archives.
