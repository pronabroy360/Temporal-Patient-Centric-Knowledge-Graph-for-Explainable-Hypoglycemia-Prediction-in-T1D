# Controlled neural experiments after the research crosscheck

Specification date: 2 October 2026. This revised **development** plan was
written after inspecting seed-20260920 results. It is not a retroactive
preregistration or evidence of graph novelty.

The fixed first gate has since completed and its recovered archives have been
paired locally. See [verified first-gate result](loop_controlled_first_gate_result_2026_10_05.md)
and [ordered next gates](next_steps_after_controlled_first_gate.md). The result
favors the CGM-only MLP for this fold and seed.

## Implemented corrections

Compressed and Kaggle-expanded partitions now resolve to the same logical
names. Missing, duplicate or misaligned partitions fail before training.
New runs verify headers, uncompressed record counts and content SHA256 hashes.
CGM participant membership, finite features, ordered timezone-aware timestamps
and per-participant timestamp/label identities are independently reconstructed.
Prediction completion requires exact validation membership and matching window
identities, binary labels and finite probabilities.

New inputs zero the export-derived same-time-variant and duplicate counts
(channels 15 and 16). Those fields remain in the protected audit cache.
Historical encoding, results and the embedded historical trainer are preserved;
the new policy is a separate experiment. This removes these predictive channels,
but does not make the full-export canonicalization process a measured online
availability pipeline.

New checkpoints bind variant, fold, training membership, window/content hashes,
seed, optimizer, batch size, workers, planned epochs and code digest. Legacy
checkpoints do not satisfy this contract; general legacy evaluation is refused.
The historical sampled verifier checks the colocated run record and final
checkpoint against the frozen inputs and saved predictions.

Event-cache rebuilds require all three basal source tables plus bolus and food,
and record source-file hashes. Alternate exports require an explicit filename
inventory. The two currently missing basal files were not restored. This
campaign uses the existing verified caches; it requires no raw-data rebuild.
Newly recorded hashes are source fingerprints, not proof against a separately
published release checksum.

## Verification actually performed

PyTorch 2.10 CPU checks exercise all six variants: forward/backward operations,
padding and empty histories, masked-input invariance, and model/optimizer reload.
Tiny fixtures exercise two-epoch training, parallel producers, exact prediction
verification, evaluation-only recovery and wrong-fold rejection with both
compressed and expanded input. These fixture outputs are not study results.

The isolated interpreter is
`/private/tmp/t1d-neural-check-20261002/bin/python` (Python 3.12, PyTorch 2.10.0,
NumPy 2.4.3). The default local Python lacks PyTorch. CUDA and dual-GPU checks
remain unexecuted locally; the runner executes them in Kaggle before fitting.

The recovered epoch-2 checkpoint was replayed on 192 frozen windows from three
validation participants. All sampled identities and scores matched. Maximum
absolute probability error was `3.2782554626464844e-07`, within the declared
absolute/relative tolerance `1e-5`. Twelve input partitions passed full content
checks. This is sampled CPU replay, not full-archive execution or a CUDA
reproducibility claim. Evidence is in
`audit/loop_gru_historical_checkpoint_cpu_replay.json`. No new research-scale
model or locked-holdout prediction was run during implementation.

The complete suite passes **124 tests** in the isolated PyTorch environment,
including execution of the embedded code package outside the local project.

## Admissible information and models

Every variant receives the existing **two** CGM features: current glucose and
recent slope. It does not receive the full 24-reading CGM history. Event variants
use the same 64 most recent retained records in `(t−120m,t]`, newest first, with
padding and explicit known-value masks. Masking occurs at model input.

| Variant | Additional inputs | Parameters | Purpose |
|---|---|---:|---|
| `cgm-mlp` | None | 22,047 | Nonlinear CGM control with approximately the GRU's parameter budget |
| `cgm-gru-mask` | Event tensor zeroed | 22,065 total; inactive event branch | Same-architecture diagnostic; effective capacity is not matched |
| `clean-gru` | Record/modality/subtype, age, numeric value, known-value mask; provenance zeroed | 22,065 | Revised joint model |
| `recording-gru` | Record/modality and known-value masks; subtype, age, numeric value zeroed | 22,065 | Recorded-event/quality diagnostic |
| `type-timing-gru` | Clean inputs with numeric value zeroed; known-value mask retained | 22,065 | Numerical-value diagnostic |
| `no-age-gru` | Clean inputs with age zeroed | 22,065 | Explicit-age diagnostic; ordinal recency and retention still convey timing |

Parameter similarity does not establish equal function class, convergence or
search effort. `recording-gru` still observes modality order/count, so it does
not isolate missingness alone. A true order perturbation is a later specified
control, not implemented here. Document eight-bucket subtype hash collisions.

Availability remains retrospective occurrence-time replay with immediate
availability assumed, not measured. Basal rate is a reported pump state; bolus
values use Normal and food uses gram-valued CarbsNet. No retained event does
not establish clinical absence.

## Fixed first gate and interpretation

The notebook runs `cgm-mlp` and `clean-gru` on outer-0 validation, seed `20261002`,
two epochs, hidden size 64, batch size 4096, three producer workers, AdamW
learning rate `2e-4`, weight decay `1e-4`, unweighted BCEWithLogitsLoss. Train
on the manifest's 395 participants and predict its 130 validation participants
and 8,885,621 windows. Do not score the 127 internal-test or 183 locked-holdout
participants.

Report participant-macro AP, its defined denominator, macro Brier and pooled
Brier separately. Pair participant/time/label identities through the existing
archive comparison tool. Compare clean-GRU with the new CGM neural control
before interpreting event gain. Preserve every result, including failures.

Fits run sequentially; each uses both available GPUs through DataParallel and
concurrent CPU producers. CGM controls bypass event reconstruction. Full input
checks run before GPU allocation and print progress. Event construction can
still limit GPU utilization. Measure throughput; no runtime guarantee is made.
Producer timeouts report every 30 seconds and retain the declared round-robin
batch order rather than changing optimizer order with worker timing. Numerical
reproducibility across CPU/CUDA versions and devices is still not guaranteed.

Declare replication seeds `20261002`, `20261003`, `20261004` now. If this first
gate changes architecture or optimization, version the plan before remaining
fits and describe that campaign as development selection. The observed seed
`20260920` remains a pilot, not a future prespecified seed. Participant bootstrap
intervals for fixed predictions do not measure training variability.

## Run the complete Kaggle package

Import `kaggle_event_sequence_gru/loop_controlled_comparison.ipynb`, or paste all
of `ONE_CELL_CONTROLLED_COMPARISON.py` into the existing private notebook.
Attach the existing private sequence-input dataset and enable T4 x2; Internet
can remain off. The cell embeds every project code dependency, so no code-dataset
update or extra script upload is needed. The old attached code is not used.
Opening the notebook does not launch training.

Run the new cell alone. Remove stale training and missing-PID diagnostic cells
from any notebook used with Save & Run All. The dedicated notebook contains
one executable cell. Do not launch it twice concurrently in one session.

Each campaign has a unique directory; each fit saves atomic run/result records,
one checkpoint per epoch and protected participant predictions. Subprocess
output appears live and is saved to logs. A ZIP is built after completion or a
caught failure. Session loss can still prevent the final ZIP: download outputs
before ending the session. A partial ZIP is not a completed experiment; inspect
`campaign.json` and each `result.json`. Hashed filenames contain study IDs in
JSON rows. Keep data, notebook, outputs and bundle private.

The ZIP includes executed code. Preserve runtime versions, input hashes and
seed. Regenerate the cell after code changes with
`python3 kaggle_event_sequence_gru/build_controlled_notebook.py`. Generated files
contain code only and no saved predictions or private cache data.

## Subsequent research gates

1. Validate downloaded bundles; compare clean-GRU/CGM-neural paired predictions
   and record training counts, runtime, input contract and selection history.
2. Complete declared event ablations and seed replications; separately specify
   an order control without silently changing timing attributes.
3. Check optimization adequacy and add a stronger full-CGM-history comparator
   from frozen windows before making a broad event-information claim.
4. Freeze B4 and capacity/search budgets, then implement G0/G1/G2 on identical
   retained events. This GRU campaign does not establish relation benefit.
5. Complete calibration, alert/episode/lead-time evaluation, explanation fidelity
   and explicit simulated-delay sensitivity on allowed development data.
6. Freeze the final procedure; evaluate the locked holdout once; carry out
   release-specific external transfer with AIDET1D/DCLP3/DCLP5/FLAIR where audited
   fields permit. Those cohorts have not supplied Loop model results.
