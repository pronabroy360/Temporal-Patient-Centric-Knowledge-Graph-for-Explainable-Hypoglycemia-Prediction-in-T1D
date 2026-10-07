import gzip
import importlib.util
import json
import sys
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from run_loop_event_logistic_pilot import canonical_records
from audit_loop_window_event_alignment import SPECS
from t1d_tkg.pilot_artifacts import PilotArtifacts, verify_windows
from t1d_tkg.logistic import LogisticModel
from t1d_tkg.manifest import build_hashed_kfold_manifest, save_manifest
from t1d_tkg.pilot_artifacts import eligible_metadata
from audit_loop_partitioned_cgm import bucket, FIELDS
from rescore_loop_pilot import rescore
from select_loop_cgm_configuration import select


class PilotCorrectionTests(unittest.TestCase):
    def test_configuration_selection_refuses_legacy_metric(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'legacy.json'
            path.write_text(json.dumps({'fold':'outer-0'}))
            with self.assertRaisesRegex(ValueError, 'corrected'):
                select([path, path])

    def test_window_gate_detects_changed_label_with_same_count(self):
        with tempfile.TemporaryDirectory() as directory:
            base = datetime(2026,1,1,tzinfo=timezone.utc)
            readings = {base+timedelta(minutes=5*i):100. for i in range(40)}
            rows = list(eligible_metadata(readings))
            path = Path(directory)/'part.jsonl.gz'
            with gzip.open(path,'wt') as handle:
                handle.write(json.dumps({'record_type':'window_index'})+'\n')
                for i,row in enumerate(rows):
                    handle.write(json.dumps(dict(row,patient_id='p',label=1 if i == 0 else row['label']))+'\n')
            with self.assertRaisesRegex(ValueError, 'differ'):
                verify_windows(directory,[Path('unused')],lambda _:iter([('p',readings)]),{'p'})
    def test_both_pilots_end_to_end_and_rescore(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            tables = work/'release'/'Data Tables'
            tables.mkdir(parents=True)
            patients = [str(i) for i in range(30)]
            manifest = build_hashed_kfold_manifest(patients, folds=3)
            save_manifest(work/'manifest.json', manifest)
            index = work/'index'
            index.mkdir()
            buckets = [[] for _ in range(3)]
            cgm = ['|'.join(FIELDS)]
            base = datetime(2026,1,1,tzinfo=timezone.utc)
            for patient in patients:
                readings = {}
                for i in range(40):
                    time = base+timedelta(minutes=5*i)
                    value = 3.0 if i >= 35 else 6.0
                    readings[time] = value*18.0182
                    cgm.append('|'.join([patient,str(len(cgm)),'upload',time.strftime('%Y-%m-%d %H:%M:%S'),'CGM',str(value),'mmol/L']))
                for row in eligible_metadata(readings):
                    buckets[bucket(patient.encode(),3)].append(dict(row, patient_id=patient))
            (tables/'LOOPDeviceCGM1.txt').write_text('\n'.join(cgm)+'\n')
            for n, rows in enumerate(buckets):
                with gzip.open(index/f'part-{n}.jsonl.gz','wt') as handle:
                    handle.write(json.dumps({'record_type':'window_index'})+'\n')
                    for row in rows:
                        handle.write(json.dumps(row)+'\n')
            for kind, (pattern, fields) in SPECS.items():
                name = pattern.replace('*','1')
                lines = ['|'.join(['PtID','RecID','UTCDtTm',*fields])]
                values = {'Rate':'1', 'Normal':'2', 'Extended':'99', 'CarbsNet':'30','CarbUnits':'grams'}
                for patient in patients:
                    lines.append('|'.join([patient,patient,'2026-01-01 02:00:00',*[values.get(f,'') for f in fields]]))
                (tables/name).write_text('\n'.join(lines)+'\n')
            cache_command = [sys.executable, str(root/'scripts/build_loop_cgm_feature_cache.py'), str(work/'release'),
                             '--model-manifest',str(work/'manifest.json'),'--window-index-directory',str(index),
                             '--output-directory',str(work/'cache'),'--summary-output',str(work/'cache.json'),
                             '--partitions','3','--minimum-free-before-gib','0','--minimum-free-during-gib','0']
            cache_result = subprocess.run(cache_command,cwd=work,env={**os.environ,'PYTHONPATH':str(root/'src')},capture_output=True,text=True)
            self.assertEqual(cache_result.returncode,0,cache_result.stderr)
            cache_summary = json.loads((work/'cache.json').read_text())
            self.assertEqual(cache_summary['development_participants'],30)
            for kind in ('cgm','event'):
                output = work/f'{kind}.json'
                command = [sys.executable, str(root/f'scripts/run_loop_{kind}_logistic_pilot.py'), str(work/'release'),
                           '--model-manifest',str(work/'manifest.json'),'--window-index-directory',str(index),
                           '--partitions','3','--epochs','1','--minimum-free-before-gib','0',
                           '--minimum-free-during-gib','0','--output',str(output)]
                result = subprocess.run(command,cwd=work,env={**os.environ,'PYTHONPATH':str(root/'src')},capture_output=True,text=True)
                self.assertEqual(result.returncode,0,result.stderr)
                report = json.loads(output.read_text())
                self.assertEqual(report['window_verification']['verified_participants'],30)
                rescored = rescore(work/report['artifacts'])
                self.assertEqual(rescored['groups'],report['groups'])
            cached_output = work/'cgm-cached.json'
            cached_command = [sys.executable, str(root/'scripts/run_loop_cgm_logistic_pilot.py'),
                              '--feature-cache-directory',str(work/'cache'), '--model-manifest',str(work/'manifest.json'),
                              '--fold','outer-0','--epochs','1','--minimum-free-before-gib','0','--output',str(cached_output)]
            cached_result = subprocess.run(cached_command,cwd=work,env={**os.environ,'PYTHONPATH':str(root/'src')},capture_output=True,text=True)
            self.assertEqual(cached_result.returncode,0,cached_result.stderr)
            self.assertEqual(json.loads(cached_output.read_text())['groups'], json.loads((work/'cgm.json').read_text())['groups'])
            event_cached_output = work/'event-cached.json'
            event_cached_command = [sys.executable, str(root/'scripts/run_loop_event_logistic_pilot.py'), str(work/'release'),
                                    '--feature-cache-directory',str(work/'cache'), '--model-manifest',str(work/'manifest.json'),
                                    '--partitions','3','--fold','outer-0','--epochs','1',
                                    '--minimum-free-before-gib','0','--minimum-free-during-gib','0','--output',str(event_cached_output)]
            event_cached_result = subprocess.run(event_cached_command,cwd=work,env={**os.environ,'PYTHONPATH':str(root/'src')},capture_output=True,text=True)
            self.assertEqual(event_cached_result.returncode,0,event_cached_result.stderr)
            self.assertEqual(json.loads(event_cached_output.read_text())['groups'], json.loads((work/'event.json').read_text())['groups'])
            test_output = work/'cgm-development-test.json'
            test_command = [sys.executable, str(root/'scripts/run_loop_cgm_logistic_pilot.py'),
                            '--feature-cache-directory',str(work/'cache'), '--model-manifest',str(work/'manifest.json'),
                            '--fold','outer-0','--epochs','1','--evaluation-scope','development-test',
                            '--minimum-free-before-gib','0','--output',str(test_output)]
            test_result = subprocess.run(test_command,cwd=work,env={**os.environ,'PYTHONPATH':str(root/'src')},capture_output=True,text=True)
            self.assertEqual(test_result.returncode,0,test_result.stderr)
            self.assertEqual(set(json.loads(test_output.read_text())['groups']), {'development_test'})

    def test_extended_amount_excluded_and_unknown_unit_preserves_presence(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'events.sorted'
            fields = SPECS['bolus'][1]
            values = {'Normal': '2', 'Extended': '100'}
            path.write_text('|'.join(['p','1','2026-01-01 12:00:00', *[values.get(f,'') for f in fields]])+'\n')
            self.assertEqual(canonical_records(path, 'bolus')['p'][0][2], 2.0)
            path.write_text('p|1|2026-01-01 12:00:00|30|exchanges\n')
            self.assertIsNone(canonical_records(path, 'food')['p'][0][2])

    def test_archive_rejects_overwrite_and_saves_rescorable_predictions(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'run'
            archive = PilotArtifacts(path, {})
            archive.model(LogisticModel((0.,),(1.,),(1.,),0.))
            archive.predictions('validation','p',['2026-01-01T12:00:00+00:00'],[1],[0.8],[1.])
            archive.complete({'ok': True})
            self.assertTrue(json.loads((path/'run.json').read_text())['complete'])
            with gzip.open(next(path.glob('*.gz')), 'rt') as handle:
                self.assertEqual(json.loads(handle.readline())['score'], 0.8)
            with self.assertRaises(FileExistsError):
                PilotArtifacts(path, {})

    def test_window_gate_rejects_absent_cgm_for_index_participant(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'part.jsonl.gz'
            with gzip.open(path,'wt') as handle:
                handle.write(json.dumps({'record_type':'window_index'})+'\n')
                handle.write(json.dumps({'patient_id':'p','index_time':'2026-01-01T12:00:00+00:00',
                                         'horizon_minutes':30,'input_eligible':True,'label_status':'known','label':1})+'\n')
            with self.assertRaisesRegex(ValueError, 'missing'):
                verify_windows(directory, [Path('unused')], lambda _: iter([]), {'p'})
