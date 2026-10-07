# Loop 64-event GRU validation run

The outer-0 validation run completed on Kaggle on 30 September 2026 with two
Tesla T4 GPUs. It used the protected development input, 64-event histories,
hidden size 64, batch size 4096, three producer workers, seed `20260920`, and
two training epochs.

The run evaluated 130 validation participants, 8,885,621 windows, and 274,044
positive labels. It reported participant-macro AP `0.47179712967070503`,
participant-macro Brier `0.021461022423620902`, and pooled Brier
`0.021107150434739704`. The manifest checksum was
`69b41e4acfae7d2afc990c8cd15d8fc3f969784d4e5f6534a9263033d341ad52` and the
window identity checksum was
`26036d7d3d27c21a4407d15aacd916b98ba598dfded5da319288a74b54a592aa`.

The completed run was recovered from the Kaggle Draft workspace under
`loop_gru_recovery_20260930T045712Z_01c1aa0f`. Its artifact bundle is now
downloaded locally as
`/Users/pronabchandraroy/Downloads/loop_gru_outer0_validated_outputs.zip`.
The ZIP passed an integrity check and contains 134 files: `result.json`,
`run.json`, two epoch checkpoints, and 130 participant prediction archives.
The ZIP size is 126,364,134 bytes. This preserves the completed validation
run despite the Kaggle draft's `ConcurrencyViolation` during save.

Content validation confirmed that all 130 prediction archives decompress and
parse, none are empty, and they contain exactly 8,885,621 prediction rows in
total. The run and result records agree, carry `complete: true`, and reproduce
the frozen manifest and window-identity checksums above. The predictions were
then paired against the selected two-epoch CGM logistic baseline by hashed
participant, timestamp, and label; all rows matched.

The paired outer-0 validation comparison favors the 64-event GRU. Its
participant-macro AP was `0.471797` versus `0.457055` for CGM, a difference of
`+0.014742` with a 2,000-draw paired-participant bootstrap interval of
`[+0.012150, +0.017206]`. AP improved for 111 of 130 participants. Its
participant-macro Brier was `0.021461` versus `0.023214`, a difference of
`-0.001753` with interval `[-0.002015, -0.001501]`; pooled Brier was `0.021107`
versus `0.022880`, a difference of `-0.001773`. The machine-readable comparison
is `audit/loop_gru_vs_cgm_outer0_validation.json`.

The separate stale-script failure in the notebook came from its input
discovery: `train_gru_fixed.py` searched for compressed `.tsv.gz` and
`.jsonl.gz` partitions, while Kaggle mounted the attached dataset as expanded
`.tsv` and `.jsonl` files. It consequently found zero partitions and later
raised `IndexError`; the missing `train_gru_parallel.pid` was a downstream
diagnostic-cell assumption, not a training failure. Frozen-module debugger
warnings were informational. Do not use that stale script for another run.
The recovery runner succeeded on expanded Kaggle files. The 2 October review
reproduced a metadata-name mismatch for compressed mounts. That check is now
repaired and covered for both forms. New experiments use the guarded
[controlled runner and specification](loop_controlled_neural_experiments.md).

This is positive development evidence that the joint CGM/event GRU
outperformed the selected two-feature CGM logistic predictor under the
retrospective immediate-availability assumption. Neural capacity, optimizer
and event information differ, so the result does not isolate event value or
establish graph-relation value. A fixed-prediction bootstrap does not measure
model-refitting uncertainty. Before finalizing the model family, resolve the
input-provenance findings, prospectively declare future replication seeds,
run the information/capacity controls, and freeze the full decision rule.
Keep the locked participants excluded from model fitting and predictive
evaluation until those development decisions are complete. See the
[2 October research crosscheck](research_crosscheck_2026_10_02.md).
