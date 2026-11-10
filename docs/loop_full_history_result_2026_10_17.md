# Loop full-history comparison: recovered and independently reproduced result

Checked 17 October 2026; local recheck 18 October 2026. The Kaggle runtime
artifacts were recovered, their archives passed integrity checks, and the
repository comparator reproduced the saved epoch-2 validation comparison. On
18 October, both the history-only versus history-plus-events comparison and the
history-plus-events versus event-disabled comparison were recomputed again from
the extracted participant predictions. Their AP, macro and pooled Brier,
cohort counts, seed, manifest hash, and window-identity hash exactly matched
the 17 October results. The fresh outputs are
`audit/loop_full_history_paired_recheck_20261018.json` and
`audit/loop_full_history_event_ablation_recheck_20261018.json`.
An additional independent rerun of the history-only/event paired comparator
reproduced the same estimates and participant-bootstrap interval in
`audit/loop_full_history_independent_pair_reproduction_20261018.json`.

## Result

The outer-0 validation run compared two variants on the same 130 participants,
8,885,621 windows and 274,044 positive labels:

| Metric | History-only | History + events | Difference, first minus second |
|---|---:|---:|---:|
| Participant-macro AP | 0.471865 | 0.460532 | +0.011334 (95% participant-bootstrap interval +0.009345 to +0.013209) |
| Participant-macro Brier | 0.021357 | 0.021839 | −0.000482 (95% interval −0.000576 to −0.000394) |
| Pooled Brier | 0.021005 | 0.021467 | −0.000462 |

History-only had higher participant AP for 114/130 participants and lower
Brier for 123/130. The parameter counts were 36,607 and 36,609. Metrics and
paired intervals were recomputed from the saved predictions by
`scripts/compare_full_history_neural_archives.py`; output:
`audit/loop_full_history_paired_recovered_20261017.json`.

## Recovered artifacts and verification

The Kaggle file browser appeared empty because its listing was stale. The
runtime contained the completed run at
`/kaggle/working/loop_full_history_20261016T182943Z_68b02d56`. Its ZIPs were
downloaded through the authenticated Jupyter proxy and saved under the ignored
private directory `private/full_history_recovered_20261017/`.

| Archive | Bytes | SHA-256 | ZIP integrity |
|---|---:|---|---|
| `aggregate_bundle.zip` | 51,502 | `481e4c99a8782907f68da26a34f4270a53739c620f9080a2125ed787c3941f53` | passed |
| `history-only_bundle.zip` | 127,242,546 | `6166992210be11bea3f00773838cd8dd7c6dafb18262644f96d2d6af647b15eb` | passed |
| `history-event_bundle.zip` | 127,479,499 | `66e062fe8504bee7ed735825991ac43f4635780bdd37c2ec698ac2e5bff07116` | passed |

Each model archive contains epoch-1 and epoch-2 checkpoints, one `result.json`,
and 130 participant validation prediction files. The run metadata agree on
seed 20261003, outer-0, 24 history steps, 64-event cap, training membership,
input/source hashes, metric version, manifest and frozen window identity. Both
reports identify the same prediction set with SHA-256
`a68ad87255e8b8944b269a6995489640ee6b37576799e917d548a0d161700224`.
The locally recomputed results match the console report to rounding precision.

## Interpretation and limits

This is a verified development-validation result for one fold and one seed.
The participant bootstrap resamples fixed predictions and does not quantify
variation from retraining. Similar parameter counts do not make the two model
architectures equivalent: the history-only model has a wider CGM encoder,
while the joint model allocates capacity to an event encoder. Therefore this
comparison does not isolate event information, causal relations, or graph
structure. It does not show that events or knowledge-graph relations are
inherently unhelpful. The earlier two-feature CGM-only MLP (AP about 0.482)
remains a stronger reference. Event timing used retrospective occurrence-time
replay with immediate availability assumed, not measured. The locked holdout
remains unopened.

The original model archives contain epoch-1 and epoch-2 checkpoints and only
epoch-2 predictions. Both history-only and history-event epoch-1 checkpoints have now been
replayed and recovered on the same frozen validation windows. Their paired
results are reported below. Two epochs are a fixed-budget pilot, not
convergence evidence.

## History-only epoch-1 checkpoint replay

The saved history-only epoch-1 checkpoint was evaluated without retraining on
the same 130 outer-0 validation participants, 8,885,621 windows and 274,044
positive labels. Its report passed the prediction identity check. The private
bundle `private/full_history_recovered_20261017/history-only-epoch1-replay_bundle.zip`
was downloaded, its SHA-256 matched Kaggle's
`3a098bfd76c9b591257d9992baf306bf16f4f7306ff30d1fd0f8dd21ac62bf1b`,
and ZIP integrity passed. The independent paired comparison against the saved
history-only epoch-2 predictions matched every patient, timestamp and label:

| Metric | Epoch 1 | Epoch 2 | Epoch 2 minus epoch 1 |
|---|---:|---:|---:|
| Participant-macro AP | 0.430144 | 0.471865 | +0.041721 |
| Participant-macro Brier | 0.023318 | 0.021357 | −0.001961 |
| Pooled Brier | 0.022962 | 0.021005 | −0.001957 |

The participant-macro AP gain has a fixed-prediction participant-bootstrap
95% interval of +0.036776 to +0.046508. This is a training diagnostic for
one model fit; it does not establish convergence. The strict comparison also
matched the replayed checkpoint SHA-256 to the original epoch-1 checkpoint,
checked the model/input/source contract, and recomputed both reports from
saved predictions. Its aggregate output is
`audit/loop_full_history_history_only_epoch1_vs_epoch2_strict_20261017.json`.

## Next steps

1. The same-architecture event-disabled branch is now complete for outer-0,
   seed 20261003, two epochs. It favors the disabled branch, but the disabled
   event encoder receives no gradients; this does not isolate relation value
   or equalize effective capacity. Treat it as a pilot control.
2. Compare event sequence, generic-edge graph, typed-relation graph and
   endpoint-type/time controls with the same information, windows, timing and
   closely aligned capacity and optimization budget. This is the next model
   experiment; graph relations have not yet been tested.
3. Replicate the selected comparisons across at least three seeds and all
   development outer folds. Freeze choices before the single locked-holdout
   evaluation. Event-availability sensitivity and explanation
   fidelity/stability remain required.

## History-event epoch-1 checkpoint replay — 17 October 2026

The saved `history-event` epoch-1 checkpoint was evaluated without retraining
on the same frozen outer-0 validation windows as the completed epoch-2 model.
Before inference, the selected event loader was checked against the original
loader on partitions 2 and 3: feature rows were identical for 140,253 windows
from 3 participants. Because Kaggle split the sequence and full-history caches
across two mounted datasets, a temporary development-only input tree was
assembled with symlinks and the existing holdout-excluding contract. The
canonical manifest hash matched, and full cache contents were revalidated
against the original 652-participant preflight receipt.

The replay completed for 130 validation participants, 8,885,621 windows and
274,044 positive labels. Prediction identity matched the frozen set
(`a68ad87255e8b8944b269a6995489640ee6b37576799e917d548a0d161700224`), and the
replayed checkpoint SHA-256 matched the saved source checkpoint
(`0b430e7c5a4b4e5c8f3f4695d6d6f0b937e57ae50981dac42de38a1b963b66df`). The
bundle `private/full_history_recovered_20261017/history-event-epoch1-replay_bundle.zip`
is 126,361,188 bytes; its local SHA-256 matches Kaggle's report
(`4600bc3b55b7066d5b5c8a2de68c75c6e2687c834c172188d431585d191d1c46`) and ZIP
integrity passes.

| Metric | History-event epoch 1 | History-event epoch 2 | Epoch 2 minus epoch 1 |
|---|---:|---:|---:|
| Participant-macro AP | 0.397077 | 0.460532 | +0.063455 (95% fixed-prediction participant-bootstrap interval +0.057791 to +0.068603) |
| Participant-macro Brier | 0.024211 | 0.021839 | −0.002372 (interval −0.002700 to −0.002077) |
| Pooled Brier | 0.023819 | 0.021467 | −0.002352 |

The epoch-1 history-only model scored AP 0.430144 and macro Brier 0.023318 on
the same windows. Its paired advantage over history-event epoch 1 was 0.033068
AP (95% interval +0.030376 to +0.035755) and 0.000893 macro Brier (interval
−0.001016 to −0.000774), favoring history-only. This remains an optimization
diagnostic: both branches improve substantially by epoch 2, with the event
branch improving more in AP. It does not establish convergence, an event
benefit or harm at convergence, or a knowledge-graph relation effect. The
strict machine-readable outputs are
`audit/loop_full_history_history_event_epoch1_vs_epoch2_strict_20261017.json`
and `audit/loop_full_history_history_only_vs_event_epoch1_20261017.json`.

## Same-architecture event-disabled control — 17 October 2026

The `history-event` and `history-event-zero` prediction archives were recovered
from Kaggle, checksum-verified, and independently compared locally. Both used
the same seed (20261003), outer-0 validation cohort, 8,885,621 windows, 274,044
positive labels, and frozen window identity
`26036d7d3d27c21a4407d15aacd916b98ba598dfded5da319288a74b54a592aa`. The
archives declare 36,609 parameters each. The event-enabled model scored
participant-macro AP 0.460532 and macro Brier 0.021839; the event-disabled
model scored AP 0.469458 and macro Brier 0.021566. Paired AP difference
(event-enabled minus event-disabled) was −0.008926 (95% fixed-prediction
participant-bootstrap interval −0.010402 to −0.007357); event-disabled won on
AP for 111 of 130 participants. Macro Brier difference was +0.000273 (interval
+0.000205 to +0.000342), with lower Brier favoring event-disabled. The pooled
Brier scores were 0.021467 and 0.021220, respectively.

The local ZIP
`private/full_history_recovered_20261017/loop_event_zero_ablation_outer0_seed20261003_retry3.zip`
matches Kaggle's SHA-256
`d3182e91fba30236e6dd683fe12186c3688ade7c61eafd0290abab924c31513f`, is
127,683,734 bytes, and passes `unzip -t`. The independently recomputed paired
result is in
`audit/loop_full_history_event_zero_ablation_outer0_seed20261003_20261017.json`.

This control removes event information, but also removes event-encoder
gradients; equal declared parameter counts do not establish equal effective
capacity. It is one seed, one fold and two epochs, and it does not test graph
relations. Do not make a general claim that events or relations help or harm
until the relation-specific controls and replication gates are complete.

## Corrected directory-aware same-seed rerun — 18 October 2026

The directory-aware runner completed a second execution of the history-only
and history-event branches on the same outer-0 validation set and seed
20261003. Kaggle's paired report again contained 130 participants, 8,885,621
windows, 274,044 positive labels, the original manifest hash and frozen
window-identity hash. It reported history-only versus history-event AP of
0.471865 versus 0.460532 (paired difference +0.011334; 95% fixed-prediction
participant-bootstrap interval +0.009345 to +0.013209). Macro Brier was
0.021357 versus 0.021839, respectively. These values exactly reproduce the
earlier recovered comparison at the reported precision.

The history-event bundle SHA-256 printed by the Kaggle run is
`3e1b9d9fe613458c0267e344bc2191e44a657fa7bf43efaadbe940109a10a546`. The
authenticated browser exposed the paired JSON and bundle paths. The complete
aggregate archive and both branch prediction bundles were later recovered to
`private/loop_full_history_20261018T055557Z_b268393f/`. The local bundle hashes
are `59efd7eefde01fbc73b3e7a9d8f4c57e76ad244dcc6fb49fb10a500ec272ff59` for
the aggregate, `7122f06333beaeef74173ce49e88b587c2aac82d46d66b2026a1b93503f448a9`
for history-only, and
`c3383c745cf48c1cd86201f1c8c1f26a4402e804a6d476d0016acd8da53a0d52` for
history-event. All ZIP integrity checks pass. Recomputing the paired metrics
from both sets of saved participant predictions reproduces Kaggle's report
within 1e-15; see
`audit/loop_full_history_corrected_rerun_reproduced_20261018.json`. This
confirms execution and archive integrity, not new independent evidence: the
rerun reused the same seed, fold, cohort and configuration. It does not
increase seed or fold replication, establish convergence, or test graph
relations.
