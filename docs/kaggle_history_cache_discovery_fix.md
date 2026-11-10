# Kaggle history-cache discovery error

## Read-only recheck — 29 October 2026

The connected Kimi bridge did not expose the user's Kaggle tab: its tab list
was empty, and opening the previously supplied notebook URL returned Kaggle's
“We can't find that page” screen. I did not edit or stop any Kaggle session.
The local diagnosis and fix below remain valid. The verified private cache ZIP
is `private/loop_cgm_history_cache_upload.zip` (611 MiB; SHA-256
`07420a151888d15cc010ca1aaa69e5ac20976e4a971a7d0f4ba46339b233b2d5`). The
preferred input is the complete `private/kaggle_loop_full_history_input`
dataset; it already contains the extracted history-cache directory, so the
old cell's requirement for a ZIP is unnecessary. Use the directory-aware
preflight and do not rerun the archive-only cell. The bridge reported an
available update; per its instructions, it was not upgraded automatically.

## Follow-up to the `found 0` traceback — 19 October 2026

The new traceback confirms that the cell which actually ran is still the
archive-only version: it checks `len(history_archives) == 1` and finds none.
This is separate from model training and happens before a model is loaded. The
local source archive is present at
`private/loop_cgm_history_cache_upload.zip`; its SHA-256 is
`07420a151888d15cc010ca1aaa69e5ac20976e4a971a7d0f4ba46339b233b2d5`, its ZIP
integrity check passes, and it contains the expected 64-partition,
44,028,064-record history cache for 652 development participants. Kaggle
cannot read a local file automatically, so the traceback means that the old
cell's mounted `/kaggle/input` tree did not expose that archive.

Use the corrected importable notebook linked below, or replace the discovery
cell with the directory-aware block in this note. In Kaggle's **Add Input**
panel, attach either (a) the complete private full-history development input,
which contains `input_contract.json` and `loop_cgm_history_cache/metadata.json`,
or (b) both the base sequence input and a private dataset containing
`loop_cgm_history_cache_upload.zip`. Then run only the input/preflight cell
first. It must identify the full-history input or report one valid cache and
pass the manifest, partition, and window-identity checks before any training
cell is started. If the corrected code still finds zero, inspect its printed
`/kaggle/input` paths and fix the attached dataset; do not rerun training.

The latest read-only Kaggle status check found the draft session off and no
active events, with a near-exhausted quota warning. No session was stopped or
training started during this diagnosis. This status is time-sensitive; check
the live panel before resuming.

The assertion `Expected one history-cache archive, found 0` is an input-discovery
failure. The stale cell searches only ZIP archives even though Kaggle can expose
the full-history dataset as an extracted directory. This assertion occurs
before model loading or training; it does not indicate a CUDA, checkpoint, or
model failure.

The corrected notebook is
[`loop_full_history_comparison_input_fix.ipynb`](../kaggle_event_sequence_gru/loop_full_history_comparison_input_fix.ipynb).
It recognizes both a mounted cache directory (by its
`loop-cgm-history-cache-v1` metadata), a ZIP archive, and a complete
`loop-full-history-input-v1` directory. An earlier draft showed the full-history
development dataset in its input panel, but the newer `found 0` traceback came
from an archive-only cell in the notebook that actually ran. Treat the traceback
as evidence about that run's mounted inputs; verify the current draft's Add Input
panel before assuming the dataset is attached. Keep prior outputs intact; use
the corrected notebook or replace the stale discovery cell, then run input
preflight before starting training.

## Replace the archive-only discovery block

In the failing cell, replace the section that asserts
`len(history_archives) == 1` and extracts that ZIP with this block. Keep the
existing `base_input` selection and the later cache-contract checks.

```python
from pathlib import Path
import json
import zipfile

input_root = Path("/kaggle/input")
working_root = Path("/kaggle/working")

# Kaggle datasets can expose the cache as a directory, so identify it by its
# metadata contract rather than by a guessed dataset or archive name.
history_caches = {}
for metadata_path in input_root.rglob("metadata.json"):
    try:
        metadata = json.loads(metadata_path.read_text())
    except (OSError, json.JSONDecodeError):
        continue
    if metadata.get("cache_version") == "loop-cgm-history-cache-v1":
        history_caches[str(metadata_path.parent.resolve())] = metadata_path.parent

history_archives = []
for archive_path in input_root.rglob("*.zip"):
    try:
        with zipfile.ZipFile(archive_path) as archive:
            for member in archive.namelist():
                if not member.endswith("metadata.json"):
                    continue
                try:
                    metadata = json.loads(archive.read(member))
                except (KeyError, json.JSONDecodeError):
                    continue
                if metadata.get("cache_version") == "loop-cgm-history-cache-v1":
                    history_archives.append(archive_path)
                    break
    except (OSError, zipfile.BadZipFile):
        continue

if len(history_caches) == 1 and not history_archives:
    history_cache = next(iter(history_caches.values()))
elif not history_caches and len(history_archives) == 1:
    extract_root = working_root / "loop_full_history_cache_upload"
    if extract_root.exists():
        raise FileExistsError(
            f"Refusing to overwrite {extract_root}; inspect or remove the old extraction first"
        )
    with zipfile.ZipFile(history_archives[0]) as archive:
        root = extract_root.resolve()
        for member in archive.infolist():
            target = (extract_root / member.filename).resolve()
            if root not in target.parents:
                raise ValueError(f"Unsafe path in history-cache archive: {member.filename}")
        archive.extractall(extract_root)
    candidates = {}
    for metadata_path in extract_root.rglob("metadata.json"):
        try:
            metadata = json.loads(metadata_path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if metadata.get("cache_version") == "loop-cgm-history-cache-v1":
            candidates[str(metadata_path.parent.resolve())] = metadata_path.parent
    if len(candidates) != 1:
        raise RuntimeError(
            "Expected exactly one history cache in the ZIP; found "
            f"{len(candidates)} under {extract_root}"
        )
    history_cache = next(iter(candidates.values()))
else:
    raise FileNotFoundError(
        "Expected exactly one history cache directory or one cache ZIP. "
        f"Found {len(history_caches)} cache directories and "
        f"{len(history_archives)} cache ZIPs. Attach the private history-cache "
        "dataset, or attach its ZIP."
    )

history_metadata_path = history_cache / "metadata.json"
assert history_metadata_path.is_file(), f"Missing cache metadata: {history_metadata_path}"
history_metadata = json.loads(history_metadata_path.read_text())
print("History cache:", history_cache)
print("Cache version:", history_metadata["cache_version"])
print("Partitions:", history_metadata["partitions"])
print("Records:", history_metadata["records"])
```

This replacement only locates the cache and reports its metadata. Continue with
the notebook's existing manifest, window-identity, participant-count and
partition-digest checks before any training or inference. Do not rerun a model
cell merely to test input discovery.

## Input to attach

The preferred input is the attached full-history development dataset, whose
contract binds the base CGM/event caches and all `history-*.tsv` partitions.
When only the base input is attached, provide a separate history-cache dataset
or one ZIP containing the cache. The preflight checks the cache metadata and
frozen-window identity before any model work starts.

## Live Kaggle check (18 October 2026)

The open `Loop Sequence T1D Controlled Comparison` notebook was inspected
read-only. Its input sidebar lists `loop-full-history-development-input-20261016`,
`loop-full-history-kaggle-runner-20261016`, and
`loop-full-history-corrected-runner-20261017`, in addition to the earlier
sequence inputs. The development input is the complete directory-form contract
`loop-full-history-input-v1`; locally it contains the `loop-cgm-history-cache-v1`
cache, all 64 partitions, 44,028,064 records, and excludes the locked holdout.
Therefore the reported zero-archive assertion is from the stale archive-only
cell, not evidence that the history data are absent. Use the directory-aware
full-history notebook above; it recognizes a complete input directory directly
and does not require a separate history ZIP. On the latest read-only check, the
live draft reported `Draft saved` and `Draft Session off`; no model was running.
The notebook editor view was blank while its embedded editor loaded, so the cell
contents could not be compared directly from the browser. The attached full-history
input is nevertheless present, and the local corrected notebook is validated.

An earlier import attempt in a newly created empty draft remained on
`Loading file...`; neither the corrected notebook nor preflight was imported in
that attempt. Keep using the existing notebook's attached datasets only after
replacing the stale discovery cell with the validated directory-aware code.

The standalone [preflight cell](../kaggle_event_sequence_gru/loop_full_history_input_preflight.py)
checks only metadata and contracts; it does not launch training. It passed
against the local full-history bundle, confirming the expected manifest hash,
window identity, history-cache version, 64 partitions, 652 development
participants, 44,028,064 windows and locked-holdout exclusion. On Kaggle, run
that cell first with its default `/kaggle/input` root. Only proceed to model
training if it prints `PREFLIGHT PASSED`.

## Read-only live check — 19 October 2026

The live `Loop Sequence T1D Controlled Comparison` editor showed `Draft Session
Running (19h:12m)`. Its Active Events control showed **0 Active Events**, and
the visible console contained the completed 18 October history-only versus
history-event comparison at `/kaggle/working/loop_full_history_20261018T055557Z_b268393f/paired_comparison.json`.
I selected “Continue editing” in Kaggle's inactivity dialog because the user
explicitly asked to leave the session running; I did not stop, reset, or launch
another cell. The cell source visible in the editor was already using the
staged full-history input path, while the reported assertion belongs to the
older archive-only discovery block. The corrected local notebook remains
`loop_full_history_comparison_input_fix.ipynb`. The stale cell should not be
rerun; no new training result was produced during this check.

A separate fresh tab of the exact notebook URL loaded the saved draft with the
input panel showing `kaggle_loop_sequence_input`, the epoch-1 replay input, the
corrected full-history runner, and the full-history development input datasets
attached. That tab showed `Draft Session off` and a console `Failed to fetch`
message; it did not start a runtime. This separate tab view does not establish
that the earlier open runtime stopped. I left that runtime untouched. The
attached input list confirms that a directory-form full-history dataset is
available, but the stale archive-only assertion must still be replaced or the
corrected directory-aware notebook used before another training run.

The standalone preflight was rerun locally on 19 October against
`private/kaggle_loop_full_history_input`. All 13 contract checks passed:
manifest and window identity agree across the base and history caches, all 64
partitions and 44,028,064 windows are accounted for, and the locked holdout is
excluded. It printed `PREFLIGHT PASSED`; this verifies the local bundle, not the
contents mounted in a live Kaggle process.

## Live rerun after the directory-discovery failure — 18 October 2026

After confirming the mounted history cache is a directory and not a ZIP, a
directory-aware runner was launched in the existing Kaggle session. It used a
fresh path, `/kaggle/working/loop_full_history_input_run_20261018`, and left the
pre-existing incomplete `/kaggle/working/loop_full_history_input` untouched.
The full-history input preflight passed for 652 development participants; the
locked holdout remains excluded. CPU and CUDA model smoke checks passed, and
the session reports GPU T4 x2. At the latest read-only browser check, the
`Loop Sequence T1D Controlled Comparison` draft session was still running and
the history-only validation prediction workers had emitted output through
partition 63/64, then the second model branch entered epoch 1 training and
passed 1,200 batches (about 4.78 million windows). This run has not yet printed
final metrics or a completed bundle; its result must not be inferred from the
earlier recovered run.

The local corrected notebook JSON and code cells compile. The current Kaggle
execution is a separately staged corrected runner; the old notebook draft's
archive-only cell has not been edited while that execution is active. Keep the
session running, then verify and recover its completed artifacts before
editing or saving the draft.

## Later live-page recheck — 18 October 2026

The active browser tab is `Loop Sequence T1D Controlled Comparison`. Its input
sidebar visibly contains `loop-full-history-development-input-20261016` with a
`loop_cgm_history_cache` directory; it does not expose a history-cache ZIP.
That directly explains the user's `Expected one history-cache archive, found
0` assertion: the stale cell insists on an archive although the cache is
mounted as a directory. The complete full-history contract is present in the
local copy at `private/kaggle_loop_full_history_input`, and the directory-based
preflight passes all manifest, window identity, partition, participant and
holdout checks there. It finds one valid input, 652 development participants,
64 partitions and 44,028,064 aligned windows, with no locked holdout.

At this later browser check the editor's `Draft Session` was off and its
console showed `Session stopped`, while the page also showed `Failed to save
draft` and a `ConcurrencyViolation` sequence-number mismatch. The Kaggle Active
Events panel nevertheless still listed the separate interactive GPU T4 x2
session as `Running` at about five hours. The editor output is therefore not
evidence that the GPU slot is free. Per the user's instruction, leave that
active session untouched. The old cell should not be rerun as-is. Use the
validated directory-aware notebook
`kaggle_event_sequence_gru/loop_full_history_comparison_input_fix.ipynb` or
replace the archive-only discovery block with the directory-aware block above.
Run the input preflight only first; start a training run only after it prints
`PREFLIGHT PASSED`. The concurrency warning is separate from the missing
archive and can prevent an edit to the existing draft from being saved.

The recovered 17 October full-history prediction archives were independently
repaired in this audit turn: the same paired AP, macro-Brier, pooled-Brier,
cohort and identity values exactly match their existing reproduction reports.
All six locally recovered ZIP bundles pass CRC integrity checks. These checks
strengthen the existing event-encoding evidence but do not evaluate typed KG
relations.

## Current notebook repair and rerun — 18 October 2026

The directory-aware notebook was imported into the Kaggle draft and confirmed
visually; the attached input list includes the full-history development data.
Its first run passed the former archive-discovery point and stopped safely at a
separate guard: `/kaggle/working/loop_full_history_input` already existed from an
incomplete earlier attempt. No training began in that failed attempt. The stale
directory was left intact. The notebook builder, standalone cell source and
importable notebook now stage new combined inputs under a UUID-suffixed path
(`loop_full_history_input_run_<id>`), while still reusing the fixed path only
when it contains a complete, contract-valid staged input.

The patched notebook was re-imported and launched in the same Kaggle session
(two Tesla T4 GPUs). The trainer completed full input verification and began
the first training branch. Its visible console showed training batch progress
and loss; the model comparison and final bundles are not yet complete. Leave
this session running and record the resulting preflight receipt, logs,
checkpoints, paired report and checksums before making any research claim. The
locked holdout remains excluded.

Follow-up live checks: the history-cache pass completed and the trainer
advanced into aligned prior-input partition verification through approximately
partition 37/64, then printed its successful preflight and started the first
model branch. The live console advanced from about 4.78 million to 9.93 million
training windows, with a later batch loss of about 0.056. These are
intermediate optimization diagnostics, not validation results. The local
regression suite passes with 141 tests passed and 3 skipped.

## Latest live run

On 18 October, two browser tabs for `Loop Sequence T1D Controlled Comparison`
were open. One was a stale draft with the archive-only assertion and a failed
save notice. The separate active GPU T4 x2 session had run the corrected
directory-aware runner. Its output directory was
`loop_full_history_20261018T055557Z_b268393f`; it completed both two-epoch
branches and the paired comparison. The stale traceback therefore describes
the old draft tab, not the completed corrected run.

The aggregate ZIP and both prediction bundles were downloaded and copied into
`private/loop_full_history_20261018T055557Z_b268393f/`. All three archives pass
ZIP integrity checks. The prediction archives were compared locally with
`scripts/compare_full_history_neural_archives.py`; local paired metrics match
Kaggle's report within 1e-15, with participant/window identity checks passing.
The machine-readable independent verification is
`audit/loop_full_history_corrected_rerun_reproduced_20261018.json`; its
interpretation limits still apply. The active GPU event can now be left alone.
The locked holdout was not used.

