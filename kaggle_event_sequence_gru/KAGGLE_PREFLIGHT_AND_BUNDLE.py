"""Kaggle cell: validate mounted inputs and bundle completed recovery runs.

Paste this after a run, or after a session restart if /kaggle/working still
contains run artifacts. This cell never launches training.
"""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path('/kaggle/input')
contracts = list(ROOT.rglob('input_contract.json'))
assert len(contracts) == 1, f'Expected one input contract, found {contracts}'
INPUT = contracts[0].parent
CGM = INPUT / 'loop_cgm_feature_cache'
EVENT = INPUT / 'loop_event_instance_cache'
meta = json.loads((CGM / 'metadata.json').read_text())
partitions = int(meta['partitions'])
features = sorted([*CGM.glob('features-*.tsv'), *CGM.glob('features-*.tsv.gz')])
events = {m: sorted([*EVENT.glob(f'events-{m}-*.jsonl'), *EVENT.glob(f'events-{m}-*.jsonl.gz')]) for m in ('basal', 'bolus', 'food')}
counts = {m: len(paths) for m, paths in events.items()}
print({'input': str(INPUT), 'cgm_partitions': len(features), 'event_partitions': counts, 'expected_partitions': partitions}, flush=True)
assert len(features) == partitions and all(value == partitions for value in counts.values()), 'Mounted cache files are incomplete; do not start training.'
assert meta.get('manifest_sha256') == json.loads((INPUT / 'input_contract.json').read_text())['manifest_sha256'], 'Input manifest does not match the CGM cache.'

working = Path('/kaggle/working')
expected_manifest = meta['manifest_sha256']
expected_windows = meta['window_verification']['window_identity_sha256']

def sha256_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()

complete_runs = []
for run in sorted(working.glob('loop_gru_recovery_*')):
    result_path = run / 'result.json'
    if not result_path.is_file():
        continue
    try:
        report = json.loads(result_path.read_text())
        validation = report['groups']['validation']
    except (OSError, KeyError, json.JSONDecodeError):
        continue
    predictions = sorted((run / 'predictions').glob('validation-*.jsonl.gz'))
    checkpoints = sorted(run.glob('checkpoint-epoch-*.pt'))
    if not (
        report.get('complete') is True
        and report.get('manifest_sha256') == expected_manifest
        and report.get('window_identity_sha256') == expected_windows
        and validation.get('participants') == 130
        and validation.get('windows') == 8_885_621
        and validation.get('positive_labels') == 274_044
        and len(predictions) == 130
        and len(checkpoints) >= 2
    ):
        print({'skipped_incomplete_or_mismatched_run': run.name, 'prediction_files': len(predictions), 'checkpoints': len(checkpoints)}, flush=True)
        continue
    complete_runs.append((run, [result_path, run / 'run.json', *checkpoints, *predictions]))

if not complete_runs:
    raise FileNotFoundError('No complete matching outer-0 validation run is present in /kaggle/working.')

archive = working / 'loop_gru_outer0_validated_outputs.zip'
if archive.exists():
    archive = working / 'loop_gru_outer0_validated_outputs_recovery.zip'
manifest_rows = []
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
    for run, files in complete_runs:
        for path in files:
            archive_name = f'{run.name}/{path.relative_to(run).as_posix()}'
            bundle.write(path, archive_name)
            digest = sha256_file(path)
            manifest_rows.append({'file': archive_name, 'bytes': path.stat().st_size, 'sha256': digest})
    bundle.writestr('bundle_manifest.json', json.dumps({'runs': [run.name for run, _ in complete_runs], 'manifest_sha256': expected_manifest, 'window_identity_sha256': expected_windows, 'files': manifest_rows}, indent=2) + '\n')

with zipfile.ZipFile(archive) as check:
    bad_member = check.testzip()
    assert bad_member is None, f'Archive integrity check failed at {bad_member}'
print({'bundled_runs': [run.name for run, _ in complete_runs], 'archive': str(archive), 'bytes': archive.stat().st_size, 'entries': len(manifest_rows) + 1}, flush=True)
