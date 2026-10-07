"""First Kaggle notebook cell: validate private input before training."""
from pathlib import Path
import hashlib, json, sys

ROOT = Path('/kaggle/input')
input_contracts = list(ROOT.rglob('input_contract.json'))
code_roots = list(ROOT.rglob('src/t1d_tkg'))
assert len(input_contracts) == 1, f'Expected one attached sequence-input dataset, found: {input_contracts}'
assert len(code_roots) == 1, f'Expected one attached project-code dataset, found: {code_roots}'
INPUT = input_contracts[0].parent
CODE = code_roots[0].parents[1]
CONTRACT = json.loads((INPUT/'input_contract.json').read_text())
manifest = INPUT/'loop_model_manifest.json'
payload = json.dumps(json.loads(manifest.read_text()),sort_keys=True,separators=(',',':')).encode()
assert hashlib.sha256(payload).hexdigest() == CONTRACT['manifest_sha256']
feature = json.loads((INPUT/'loop_cgm_feature_cache'/'metadata.json').read_text())
event = json.loads((INPUT/'loop_event_instance_cache'/'metadata.json').read_text())
assert feature['manifest_sha256'] == event['manifest_sha256'] == CONTRACT['manifest_sha256']
assert event['cgm_window_identity_sha256'] == CONTRACT['window_identity_sha256']
assert CONTRACT['max_events'] == 64 and not CONTRACT['contains_locked_holdout']
sys.path.insert(0, str(CODE/'src'))
print('validated private development input:', CONTRACT)
