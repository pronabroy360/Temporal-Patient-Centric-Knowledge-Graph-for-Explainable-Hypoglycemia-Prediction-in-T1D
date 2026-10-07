#!/usr/bin/env python3
"""Stage the protected derived inputs for one private Kaggle dataset."""
import argparse
import json
import shutil
from pathlib import Path

import hashlib

def manifest_digest(path):
    return hashlib.sha256(json.dumps(json.loads(path.read_text()),sort_keys=True,separators=(',',':')).encode()).hexdigest()

def main():
    p=argparse.ArgumentParser(); p.add_argument('--feature-cache',type=Path,required=True); p.add_argument('--event-cache',type=Path,required=True); p.add_argument('--model-manifest',type=Path,required=True); p.add_argument('--destination',type=Path,required=True); a=p.parse_args()
    if a.destination.exists(): raise FileExistsError('destination must be new')
    feature=json.loads((a.feature_cache/'metadata.json').read_text()); event=json.loads((a.event_cache/'metadata.json').read_text())
    if feature['manifest_sha256'] != event['manifest_sha256'] or feature['manifest_sha256'] != manifest_digest(a.model_manifest): raise ValueError('cache and manifest checksums differ')
    if event['cgm_window_identity_sha256'] != feature['window_verification']['window_identity_sha256']: raise ValueError('cache window identities differ')
    a.destination.mkdir(parents=True); shutil.copytree(a.feature_cache,a.destination/'loop_cgm_feature_cache'); shutil.copytree(a.event_cache,a.destination/'loop_event_instance_cache'); shutil.copy2(a.model_manifest,a.destination/'loop_model_manifest.json')
    (a.destination/'input_contract.json').write_text(json.dumps({'manifest_sha256':feature['manifest_sha256'],'window_identity_sha256':feature['window_verification']['window_identity_sha256'],'partitions':feature['partitions'],'max_events':64,'history_minutes':120,'contains_locked_holdout':False},indent=2)+'\n')
    print(a.destination)
if __name__=='__main__': main()
