# Research crosscheck and defensible claims

Review date: 2 October 2026 (Asia/Dhaka).

Implementation follow-up on the same date: see the
[controlled neural specification](loop_controlled_neural_experiments.md).
The loader/content/checkpoint guards and revised input variants are now
implemented. CPU neural/integration tests passed, and the recovered checkpoint
reproduced 192 saved predictions from three participants. The findings below
record the initial audit; CUDA execution, new research-scale controls and the
remaining scientific gates are still outstanding.

## Verdict

The research direction remains defensible. The recovered GRU validation run is
a usable retrospective development result. The work is not mistake-free, and
neither event-specific benefit nor a novel graph contribution has been
established. Preserve the completed predictions and negative results; address
the findings below before expanding the training campaign.

The present defensible result is: **the joint CGM/event GRU outperformed the
selected two-feature CGM logistic predictor on the same outer-0 validation
participants and windows.** Architecture, optimizer and information differ
between these models, so this comparison cannot isolate the value of events.

## Scope and evidence checked

This review inspected the proposal, protocol, experiment specification,
manifest, cache/sequence builders, Kaggle recovery runner, paired comparison
tool, result records and recovered local artifacts. It refreshed selected
primary prior-work sources. It did not repeat the 111-million-row source
audit, retrain a model, load a checkpoint with PyTorch, or perform an exhaustive
systematic literature review.

The downloaded ZIP is
`/Users/pronabchandraroy/Downloads/loop_gru_outer0_validated_outputs.zip`:
126,364,134 bytes; SHA256
`444435614d216fe7914b625bebc008f18e5d6b068fd12e0b7fc21b3300f6e554`.
The earlier local content check parsed all prediction JSON rows. This review
additionally checked the extracted predictions against the expected manifest
and baseline, including probability validity and strictly increasing times.

| Check | Verified result |
|---|---|
| Development / locked participant sets | 652 / 183, with zero overlap |
| Outer-0 train / validation / internal test | 395 / 130 / 127; pairwise disjoint |
| Manifest checksum | `69b41e4acfae7d2afc990c8cd15d8fc3f969784d4e5f6534a9263033d341ad52` |
| ZIP contents | 134 files: two records, two checkpoints, 130 prediction files |
| Prediction participants | Exactly the outer-0 validation set; no train or locked participants |
| Paired participant/time/label identities | All 8,885,621 rows matched the selected CGM baseline |
| Positive labels | 274,044 |
| Invalid probabilities, labels, duplicate/non-increasing times, mixed-patient files | Zero in the checked GRU archive |
| Checkpoint file structure | Both PyTorch ZIP containers passed integrity checks; tensor storages and model/optimizer/configuration fields are present |
| Checkpoint execution | Not verified: PyTorch is unavailable in the current local Python environment |
| Repository checks | 98 tests passed; recovery runner and comparison tool compile |

The tests cover the common pipeline and selected synthetic cases. They do not
exercise a CUDA forward pass, multi-GPU training, checkpoint reload, or every
release-level condition. File integrity is distinct from executable
checkpoint reproducibility.

## Result that survives the review

The saved paired report is
`audit/loop_gru_vs_cgm_outer0_validation.json`. Its metric policy is
`threshold-grouped-ap-v2`, with 2,000 participant resamples and seed
`20260915`. AP tie handling is covered by regression tests.

| Metric | Joint GRU | CGM logistic | GRU minus logistic |
|---|---:|---:|---:|
| Participant-macro AP | 0.471797 | 0.457055 | +0.014742 |
| Participant-macro Brier | 0.021461 | 0.023214 | -0.001753 |
| Pooled Brier | 0.021107 | 0.022880 | -0.001773 |

The macro-AP difference interval is `[+0.012150, +0.017206]`; 111 of 130
participants have higher AP. The macro-Brier difference interval is
`[-0.002015, -0.001501]`. These are descriptive intervals for fixed predictions
on a development population that informed choices. They do not incorporate
model refitting or remove selection effects. Macro and pooled Brier must
remain distinct. A 30-minute prediction horizon does not guarantee 30 minutes
of warning.

## Findings and required responses

### 1. Event benefit is confounded with model capacity — high scientific priority

The logistic reference uses current glucose and recent slope. The GRU uses
these same two CGM features through a nonlinear branch plus an event encoder
and risk head. Its optimizer also differs. A better score cannot establish
that event information caused the improvement.

Required response: train a neural CGM-only control with the same two admissible
CGM inputs and a declared effective parameter/training/search budget. Report
architecture differences. A later full-CGM-history comparator needs a new
shared cache contract; the current two-feature cache is not a 24-reading CGM
sequence. Do not manufacture a CGM sequence from the two summary features.

### 2. Export provenance enters model inputs — high scientific priority

`scripts/build_loop_event_instance_cache.py:47` computes exact-repeat and
same-time-variant counts from the complete source export.
`src/t1d_tkg/event_sequence_cache.py:37` encodes both counts as numeric inputs.
Their availability at prediction time has not been demonstrated. An export
repeat or correction collected later could alter a feature attached to an
earlier event.

This is a proven dependence on completed-export metadata, **not proof that
future outcome labels actually leaked in this run**. The occurrence-time
cutoff alone does not resolve this question. Until measured arrival/version
times are available, retain the run as an export-based retrospective pilot.

Required response: keep these fields for auditing, remove them from prediction
inputs in a newly versioned contract, and run a matched removal sensitivity.
If retained, justify when each count could have been known. A simulated delay
experiment must filter records before computing any derived counts.

### 3. Compressed input support is broken — reproduced implementation defect

`kaggle_event_sequence_gru/train_gru_recovery.py:208` strips `.gz` from expected
metadata names, but compares them to unnormalized actual filenames. A minimal
fixture passes for `.tsv`/`.jsonl` files and fails for equivalent `.gz` files
with `ValueError: staged CGM files do not match cache metadata`.

This does not invalidate the recovered run on expanded Kaggle mounts. It does
contradict the claim that the recovery runner currently supports both forms.
Normalize expected and actual names, reject duplicate logical partitions,
and test expanded, compressed and missing-partition cases before reuse.

### 4. Checkpoint and input-content provenance are incomplete — high operational priority

The saved checkpoints include epoch, model, optimizer, seed, hidden width,
maximum event count and manifest hash. They omit fold, training-participant
identity, window/content hashes and source/environment identities. In
evaluation mode, the runner checks hidden width, event count and manifest,
but cannot reject a checkpoint trained on another fold of that manifest.
The currently reviewed result was produced in training mode on outer-0; this
gap does not establish that its validation participants were used for fitting.

The staged loader checks versions, manifest and filenames, but does not
recompute partition `content_sha256` values. The metadata checksums therefore
identify the declared inputs; they do not independently authenticate all
mounted numeric feature/event values.

Required response: bind future checkpoints to fold, training membership,
input-content hashes, model/configuration and executed source/environment.
Record per-epoch training counts. Reject incompatible evaluation checkpoints
and altered partitions. Reload the preserved checkpoint in a compatible
PyTorch environment. Existing checkpoints do not promise exact interrupted
training resume because random/sampler state is absent.

### 5. Raw-source rebuild is incomplete locally — confirmed reproducibility limitation

Git reports `LOOPDeviceBasal1.txt` and `LOOPDeviceBasal2.txt` as deleted; only
`LOOPDeviceBasal3.txt` was found under the current data folder. No original
Loop ZIP was found by the checked filename patterns there. This does not
alter the recovered predictions or existing derived caches.

The event builder requires at least one table per modality, rather than the
complete release inventory. It could accept the remaining basal table and
build a silently incomplete new cache. Verify or restore the complete raw
release and enforce its inventory/checksums before any source rebuild. This
review did not restore or delete user data.

### 6. Development results and seeds must be described accurately

Outer-0 validation has guided architecture/representation choices and overlaps
another rotating fold's internal test population. The broader development
results are not untouched nested-CV confirmation. The 183-person holdout is
excluded from fitting and predictive scoring, but aggregate coverage/label
audits have inspected its records. Avoid saying it has never been read.

The completed seed `20260920` is already observed. It cannot retrospectively
be called prespecified. Freeze future configurations and seeds before running
them; three prospectively declared seeds are preferable. A pilot plus two
new seeds can also be reported, with its selection history made explicit.

### 7. Claims and specifications have drifted

The protocol still says experiments have not begun; the proposal still
describes nested CV and potential upload linkage. These are historical design
statements, whereas the executed workflow is a retrospective Loop development
benchmark with an unavailable observed-arrival clock. Use the executed
contract and selection history in any manuscript; version changes without
rewriting old choices as if they preceded the results.

The actual event order is newest-first; the selected GRU state includes only
valid positions, and empty sequences are explicitly zeroed. Static inspection
found no padding-induced future-data use, but GPU padding/empty-history tests
remain needed. Removing age attributes while retaining recency-based selection
or order does not remove all timing information. Shuffling order while keeping
ages does not remove temporal information either.

Prediction filenames are hashes, but JSON rows retain study participant IDs
for pairing. These are protected research archives, not anonymous public
outputs. Preserve that distinction in documentation and distribution.

## Novelty crosscheck and defense

The broad idea of a semantic patient-specific hypoglycemia graph is already
present in the [ESWC 2024 manuscript](https://2024.eswc-conferences.org/wp-content/uploads/2024/05/77770363.pdf)
and its [2025 Springer chapter](https://link.springer.com/chapter/10.1007/978-3-031-78955-7_4).
The former describes a semantic integration and prediction research plan.
It prevents a defensible claim that this project is the first such proposal.

The [GAT-BiGRU publication](https://pubmed.ncbi.nlm.nih.gov/42314749/)
already describes multimodal temporal-neighborhood graphs, recurrent learning,
30/60-minute hypoglycemia risk and explanation tools. Its full publisher route
still redirected to the abstract in this review. Its headline scores cannot
be compared directly with our participant-macro AP because cohorts, targets
and evaluation may differ.

Targeted passages of the [Onwuchekwa dissertation](https://dspace-backend.ub.uni-siegen.de/server/api/core/bitstreams/1e658634-a368-49e9-93b2-4491e750edb8/content)
also discuss semantic schema integration, temporal glucose relations and
patient-specific knowledge. A complete methods comparison remains necessary;
this targeted inspection is not an exhaustive extraction or a reproduced
equivalent benchmark.

Our potentially distinct contribution is an empirical decomposition of
individual-event representation, relation parameterization and availability
assumptions with matched inputs, windows, capacity and explanation-fidelity
checks. That remains a research objective, not an achieved novelty certificate.
The current GRU is a comparator, not a novel graph algorithm.

When relations are constructed from endpoint types and timestamps, they do not
create additional information. Test whether they provide useful inductive
bias. B4/G0/G1/G2 on identical retained events and declared capacity/search
budgets are necessary to answer this question. Preserve the earlier summary,
residual and truncated-sequence negative results rather than reporting only
the positive GRU run.

## Ordered completion gates

1. Correct claim wording and archive this review; preserve completed artifacts.
2. Repair input/checkpoint/content checks, resolve the export-provenance inputs,
   test model padding/empty histories and reload the old checkpoint.
3. Freeze a revised admissible input contract and selection history. Verify the
   full source inventory only if rebuilding the caches is required.
4. Run the neural CGM-only control and event presence/value/time/order controls
   under declared budgets; prospectively declare replication seeds.
5. Freeze B4, then evaluate G0/G1/G2 with the same retained event membership,
   attributes, windows and comparable effective capacity.
6. Complete calibration, episode alerts, lead time, explanation fidelity and
   simulated availability sensitivity on allowed development data.
7. Freeze the final procedure, then evaluate the locked participant holdout.
8. Audit common-field cohort mappings and perform external transfer separately.

AIDET1D, DCLP3, DCLP5 and FLAIR have release-specific feasibility roles in the
existing documents. They did not supply the recovered Loop GRU's training or
validation results. Confirmable multi-cohort evidence and graph-explanation
evidence are still outstanding.

The project does not need to restart. Its verified retrospective predictions
can be retained while the unresolved implementation and scientific gates are
completed. This review itself ran no new training and evaluated no holdout
predictions.
