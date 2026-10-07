"""Protected pilot artifacts and exact eligible-window reconciliation."""
import gzip
import hashlib
import json
import subprocess
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from .metrics import METRIC_VERSION
from .temporal_eligibility import logical_grid_window_metadata
from .window_index import iter_window_index


def identity(time, label):
    return (datetime.fromisoformat(str(time)).isoformat() + '|' + str(int(label)) + '\n').encode()


def eligible_metadata(readings):
    for row in logical_grid_window_metadata(readings, threshold=70.0, tolerance_seconds=1):
        if row['input_eligible'] and row['label_status'] == 'known':
            yield row


def verify_windows(index_directory, sorted_partitions, reader, patients):
    """Compare ordered timestamp/label identities per development participant."""
    paths = sorted(Path(index_directory).glob('*.jsonl.gz'))
    if len(paths) != len(sorted_partitions):
        raise ValueError('frozen window-index partition count mismatch')
    expected = {}
    counts = {}
    for path in paths:
        for row in iter_window_index(path):
            patient = str(row['patient_id'])
            if patient not in patients:
                continue
            if row['horizon_minutes'] != 30 or not row['input_eligible'] or row['label_status'] != 'known':
                raise ValueError('unexpected frozen window contract')
            expected.setdefault(patient, hashlib.sha256()).update(identity(row['index_time'], row['label']))
            counts[patient] = counts.get(patient, 0) + 1
    seen = set()
    for path in sorted_partitions:
        for patient, readings in reader(path):
            if patient not in patients:
                continue
            if patient in seen:
                raise ValueError('participant occurs in multiple CGM partitions')
            seen.add(patient)
            digest = hashlib.sha256()
            count = 0
            for row in eligible_metadata(readings):
                digest.update(identity(row['index_time'], row['label']))
                count += 1
            if count != counts.get(patient, 0) or digest.digest() != expected.get(patient, hashlib.sha256()).digest():
                raise ValueError('regenerated windows differ from frozen index')
    if set(expected) - seen:
        raise ValueError('frozen-index participants missing from CGM')
    fingerprint = hashlib.sha256()
    for patient in sorted(expected):
        fingerprint.update(json.dumps([patient, counts[patient], expected[patient].hexdigest()]).encode())
    return {'verified_participants': len(seen), 'verified_windows': sum(counts.values()),
            'window_identity_sha256': fingerprint.hexdigest(),
            'contract': 'per-participant ordered timestamp and label SHA256 equality'}


class PilotArtifacts:
    def __init__(self, path, configuration):
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=False)
        root = Path(__file__).resolve().parents[2]
        revision = subprocess.run(['git', '-C', str(root), 'rev-parse', 'HEAD'], capture_output=True, text=True)
        sources = sorted([*(root/'src/t1d_tkg').glob('*.py'), *(root/'scripts').glob('*.py')])
        source_digest = hashlib.sha256()
        for source in sources:
            source_digest.update(str(source.relative_to(root)).encode())
            source_digest.update(source.read_bytes())
        self.metadata = {**configuration, 'metric_version': METRIC_VERSION,
                         'python': sys.version, 'git_revision': revision.stdout.strip(),
                         'source_sha256': source_digest.hexdigest(), 'complete': False}
        self.write_metadata()

    def write_metadata(self):
        (self.path / 'run.json').write_text(json.dumps(self.metadata, indent=2) + '\n')

    def model(self, model):
        (self.path / 'model.json').write_text(json.dumps(asdict(model), indent=2) + '\n')

    def predictions(self, group, patient, times, labels, scores, rule_scores):
        token = hashlib.sha256(str(patient).encode()).hexdigest()
        path = self.path / f'{group}-{token}.jsonl.gz'
        with gzip.open(path, 'xt', encoding='utf-8') as handle:
            for time, label, score, rule in zip(times, labels, scores, rule_scores, strict=True):
                handle.write(json.dumps({'patient_id': patient, 'index_time': time,
                                         'label': label, 'score': score, 'rule_score': rule}) + '\n')

    def complete(self, report):
        self.metadata['complete'] = True
        self.metadata['report'] = report
        self.write_metadata()
