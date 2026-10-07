"""Build a complete, code-only Kaggle cell/notebook; no late script upload needed."""
from pathlib import Path
import base64
import hashlib
import io
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = Path(__file__).resolve().parent


def build():
    files = [*ROOT.joinpath("src").rglob("*.py"), *ROOT.joinpath("scripts").glob("*.py"), PACKAGE / "train_gru_recovery.py", PACKAGE / "train_controlled.py"]
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(files):
            info = zipfile.ZipInfo(str(path.relative_to(ROOT)), date_time=(2026, 10, 2, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
    payload = stream.getvalue()
    encoded = base64.b64encode(payload).decode()
    cell = '''# Complete controlled comparison cell. Attach the EXISTING PRIVATE input dataset.
# No code-dataset update is needed. Run this cell once in a private T4 x2 notebook.
from pathlib import Path
from datetime import datetime, timezone
import base64, hashlib, io, json, os, shutil, subprocess, sys, uuid, zipfile

SEED = 20261002
VARIANTS = ["cgm-mlp", "clean-gru"]  # First gate; the ablations are implemented too.
EPOCHS = 2
WORKERS = 3
BATCH_SIZE = 4096
print("CONTROLLED COMPARISON CELL STARTED", datetime.now(timezone.utc).isoformat(), flush=True)
PAYLOAD = __PAYLOAD__
EXPECTED_SHA256 = "__DIGEST__"
raw = base64.b64decode(PAYLOAD)
assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256, "embedded code integrity failure"
root = Path("/kaggle/working") / ("loop_controls_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ_") + uuid.uuid4().hex[:8])
code = root / "code"
code.mkdir(parents=True)
with zipfile.ZipFile(io.BytesIO(raw)) as archive:
    for name in archive.namelist():
        assert not Path(name).is_absolute() and ".." not in Path(name).parts
    archive.extractall(code)
contracts = list(Path("/kaggle/input").rglob("input_contract.json"))
assert len(contracts) == 1, f"Attach exactly one private sequence-input dataset, found {len(contracts)}"
INPUT = contracts[0].parent
import torch
assert torch.cuda.is_available(), "Enable the T4 x2 accelerator"
print("GPUs:", [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())], flush=True)
print("Input:", INPUT, "Output:", root, flush=True)
runner = code / "kaggle_event_sequence_gru/train_controlled.py"
env = dict(os.environ, PYTHONPATH=str(code / "src") + os.pathsep + str(code / "scripts"), PYTHONUNBUFFERED="1")

def execute(arguments, log_path):
    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen([sys.executable, "-u", str(runner), *arguments], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        print("Started PID", process.pid, flush=True)
        try:
            for line in process.stdout:
                print(line, end="", flush=True); log.write(line); log.flush()
            status = process.wait()
            if status:
                raise RuntimeError(f"Runner exited {status}; inspect {log_path}")
        finally:
            if process.poll() is None:
                process.terminate(); process.wait(timeout=20)

state = {"complete": False, "seed": SEED, "variants": VARIANTS, "epochs": EPOCHS, "code_bundle_sha256": EXPECTED_SHA256, "completed_runs": []}
(root / "campaign.json").write_text(json.dumps(state, indent=2))
try:
    execute(["--self-test"], root / "model_preflight.log")
    for variant in VARIANTS:
        destination = root / f"{variant}_outer0_seed{SEED}"
        execute(["--mode", "train", "--input-directory", str(INPUT), "--code-directory", str(code), "--run-directory", str(destination), "--variant", variant, "--fold", "outer-0", "--seed", str(SEED), "--epochs", str(EPOCHS), "--workers", str(WORKERS), "--batch-size", str(BATCH_SIZE)], root / f"{variant}.log")
        result = json.loads((destination / "result.json").read_text())
        assert result["complete"] and result["prediction_identity_verified"]
        state["completed_runs"].append(destination.name)
        (root / "campaign.json").write_text(json.dumps(state, indent=2))
    state["complete"] = True
finally:
    (root / "campaign.json").write_text(json.dumps(state, indent=2))
    # Complete and interrupted runs both retain logs and available checkpoints.
    bundle = Path(shutil.make_archive(str(root) + "_bundle", "zip", root_dir=root.parent, base_dir=root.name))
    digest = hashlib.sha256()
    with bundle.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    print("PRIVATE BUNDLE:", bundle, "BYTES:", bundle.stat().st_size, "SHA256:", digest.hexdigest(), "COMPLETE:", state["complete"], flush=True)
    from IPython.display import FileLink, display
    display(FileLink(bundle.name))
'''
    chunks = "(\n" + "\n".join("    " + repr(encoded[start:start+100]) for start in range(0, len(encoded), 100)) + "\n)"
    cell = cell.replace("__PAYLOAD__", chunks).replace("__DIGEST__", hashlib.sha256(payload).hexdigest())
    compile(cell, "ONE_CELL_CONTROLLED_COMPARISON.py", "exec")
    (PACKAGE / "ONE_CELL_CONTROLLED_COMPARISON.py").write_text(cell)
    notebook = {"nbformat": 4, "nbformat_minor": 5, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}, "cells": [
        {"cell_type": "markdown", "id": "instructions", "metadata": {}, "source": ["# Loop controlled neural comparisons\n", "Private development data only. Attach the existing input dataset and enable T4 x2. This cell installs its complete code package, checks inputs, runs two-epoch CGM-only and provenance-masked GRU comparisons, and bundles protected checkpoints/predictions. Download the bundle before ending the session. Training is not launched by opening this notebook.\n"]},
        {"cell_type": "code", "id": "controlled-campaign", "metadata": {}, "source": cell.splitlines(keepends=True), "execution_count": None, "outputs": []},
    ]}
    (PACKAGE / "loop_controlled_comparison.ipynb").write_text(json.dumps(notebook, indent=1) + "\n")
    print(f"Built complete cell and notebook: {len(files)} code files, {len(payload)} compressed bytes; no private data")


if __name__ == "__main__":
    build()
