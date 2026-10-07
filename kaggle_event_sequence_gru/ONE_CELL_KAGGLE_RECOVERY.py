# Paste this entire cell into the existing Loop Sequence T1D Kaggle notebook.
# It writes the reviewed trainer into /kaggle/working and starts a fresh outer-0 validation run.
from pathlib import Path
from datetime import datetime, timezone
import base64, hashlib, json, shutil, subprocess, sys, uuid, zlib

print('KAGGLE CELL STARTED', datetime.now(timezone.utc).isoformat(), flush=True)
payload = (
    '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'
)
source = zlib.decompress(base64.b64decode(payload))
expected_sha256 = "e73e41c696ffcc9c2b1f7d624936e3782c23768dd95aa848ef007514462c896b"
assert hashlib.sha256(source).hexdigest() == expected_sha256
runner = Path('/kaggle/working/train_gru_recovery.py')
runner.write_bytes(source)
print('Trainer installed:', runner, 'SHA256:', expected_sha256, flush=True)

import torch
assert torch.cuda.is_available(), 'Enable the Kaggle GPU accelerator before running this cell.'
print('Torch loaded; scanning attached datasets...', flush=True)
root = Path('/kaggle/input')
contracts = list(root.rglob('input_contract.json'))
code_roots = list(root.rglob('src/t1d_tkg'))
assert len(contracts) == 1, f'Expected one attached input dataset; found {contracts}'
assert len(code_roots) == 1, f'Expected one attached project-code dataset; found {code_roots}'
private_input = contracts[0].parent
code_root = code_roots[0].parents[1]
contract = json.loads(contracts[0].read_text())
assert contract['max_events'] == 64 and not contract['contains_locked_holdout']
run_dir = Path('/kaggle/working') / ('loop_gru_recovery_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '_' + uuid.uuid4().hex[:8])
print('GPU(s):', [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())], flush=True)
print('Run directory:', run_dir, flush=True)
subprocess.run([
    sys.executable, '-u', str(runner),
    '--mode', 'train', '--run-directory', str(run_dir),
    '--input-directory', str(private_input), '--code-directory', str(code_root),
    '--fold', 'outer-0', '--evaluation-scope', 'validation',
    '--epochs', '2', '--batch-size', '4096', '--workers', '3',
    '--hidden', '64', '--seed', '20260920',
], check=True)
bundle = Path('/kaggle/working') / (run_dir.name + '_bundle')
archive = Path(shutil.make_archive(str(bundle), 'zip', root_dir=run_dir.parent, base_dir=run_dir.name))
print('Bundle created:', archive, 'bytes:', archive.stat().st_size, flush=True)
 print('Completed:', run_dir / 'result.json', flush=True)
