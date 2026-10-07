# Next gates after the verified controlled first gate

Updated: 5 October 2026. This is a **development-stage** plan informed by the
recovered outer-0, seed-20261002 first gate. It is not a retroactive
preregistration. The locked holdout remains untouched.

## What the first gate decides

The clean event GRU has lower participant-macro AP and higher Brier score than
the capacity-similar CGM-only MLP on identical validation windows. The paired
fixed-prediction interval favors CGM-only. Therefore the study cannot claim
that the present event representation improves prediction, and the earlier
comparison against a logistic CGM model does not isolate event information.
This result does not answer whether a better event architecture or explicit
relations can help, and it does not establish clinical-event absence or
real-time availability.

## Ordered work

1. **Preserve the first gate.** Keep the original ZIP, its SHA256, both model
   directories and the aggregate paired report private. Do not tune on the
   internal development-test or locked holdout. The recovered bundle is
   complete; this gate is done.
2. **Check optimization adequacy on development validation.** Evaluate the
   existing epoch-1 and epoch-2 checkpoints on the *same* outer-0 windows to
   see whether either model was still improving. Record runtime, producer/GPU
   throughput and any instability. These checks are development diagnostics,
   not independent test evidence. If training length or optimizer changes,
   version that as a new campaign and give both models equal tuning effort.
3. **Add a full-CGM-history control.** The current pair sees only current
   glucose and recent slope. Build a causal, masked 120-minute CGM history
   representation from the same frozen index times, with no future values or
   cross-patient leakage. Compare a CGM-only sequence model against a joint
   CGM-plus-event model under matched training, parameter budget, and
   validation windows. Keep the existing two-feature result as a separate
   baseline; do not silently replace its input contract.
4. **Test which event content matters.** Run the implemented recording-only,
   type/timing, and age ablations on the revised development setup. Add a
   separately specified order/relation perturbation that preserves event
   counts, types, values and timestamps as appropriate. Report both gains and
   losses, event coverage, and the assumed occurrence-time availability.
5. **Replicate before graph claims.** Use the previously declared seeds
   20261002, 20261003 and 20261004, then patient-disjoint development folds.
   Aggregate paired participant results with fold/seed variation made
   explicit. Fixed-prediction participant bootstrap intervals alone do not
   capture retraining variation.
6. **Only then isolate graph relations.** Compare a relation-aware temporal
   graph against the same events and timing in a relation-free sequence or
   graph control, plus typed/generic/shuffled-relation controls. Match
   capacity, optimization and the exact prediction windows. The strongest
   CGM-only model remains a required comparator. Measure explanation fidelity
   separately from predictive ranking.
7. **Freeze and test.** Select the final configuration using development data,
   document every selection, then open the locked holdout once. External Jaeb
   cohorts can support later transportability checks only after their field,
   treatment-regime and label definitions are harmonized and independently
   audited.

Before any long Kaggle campaign, confirm a tiny file can be downloaded from
the active session. Save each completed model's `result.json`, checkpoints and
participant predictions promptly rather than relying on a single final ZIP.
Keep protected predictions out of Git. The current root-level extracted
campaign is ignored by `.gitignore`; the aggregate audits contain no patient
identifiers.
