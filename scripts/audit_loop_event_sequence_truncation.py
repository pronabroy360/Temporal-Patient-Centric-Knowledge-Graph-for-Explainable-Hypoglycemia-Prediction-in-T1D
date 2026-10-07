#!/usr/bin/env python3
"""Audit modality retention under a fixed cached-event sequence length."""
import argparse
import json
from collections import Counter
from pathlib import Path

from run_loop_event_sequence_linear_pilot import sequence_partition
from t1d_tkg.event_cache import load_metadata as load_event_metadata
from t1d_tkg.feature_cache import load_metadata as load_cgm_metadata
from t1d_tkg.manifest import load_manifest, manifest_checksum


def main():
    p=argparse.ArgumentParser(); p.add_argument("--feature-cache-directory",type=Path,required=True); p.add_argument("--event-cache-directory",type=Path,required=True); p.add_argument("--model-manifest",type=Path,default=Path("private/loop_model_manifest.json")); p.add_argument("--max-events",type=int,required=True); p.add_argument("--output",type=Path,required=True); a=p.parse_args()
    if a.output.exists(): raise FileExistsError("choose a new output path")
    manifest=load_manifest(a.model_manifest); checksum=manifest_checksum(manifest); cgm=load_cgm_metadata(a.feature_cache_directory,manifest_sha256=checksum); event=load_event_metadata(a.event_cache_directory,manifest_sha256=checksum)
    if event.get("cgm_window_identity_sha256") != cgm["window_verification"]["window_identity_sha256"]: raise ValueError("cache window identities differ")
    n=int(cgm["partitions"]); cgms=sorted(a.feature_cache_directory.glob("features-*.tsv.gz")); events={m:sorted(a.event_cache_directory.glob(f"events-{m}-*.jsonl.gz")) for m in ("basal","bolus","food")}
    totals=Counter(); active=Counter(); retained=Counter(); active_histogram=Counter()
    for i in range(n):
        paths=[events[m][i] for m in ("basal","bolus","food")]
        for _,_,_,_,_,count,dropped,active_mod,retained_mod in sequence_partition(cgms[i],paths,a.max_events,include_modality_counts=True):
            totals["windows"]+=1; totals["active_events"]+=count; totals["dropped_events"]+=dropped; totals["windows_truncated"]+=int(dropped>0); active_histogram[count]+=1
            active.update(active_mod); retained.update(retained_mod)
    def quantile(probability):
        target=(totals["windows"]-1)*probability; cumulative=0
        for count in sorted(active_histogram):
            cumulative += active_histogram[count]
            if cumulative > target: return count
    caps=(16,32,64,128)
    report={"audit_type":"cached event-sequence truncation by modality","max_events":a.max_events,"windows":totals["windows"],"windows_truncated":totals["windows_truncated"],"fraction_windows_truncated":totals["windows_truncated"]/totals["windows"],"active_events":totals["active_events"],"dropped_events":totals["dropped_events"],"active_event_count_quantiles":{"p50":quantile(.5),"p90":quantile(.9),"p95":quantile(.95),"p99":quantile(.99),"max":max(active_histogram)},"expected_windows_truncated_by_max_events":{str(cap):sum(value for count,value in active_histogram.items() if count>cap) for cap in caps},"active_by_modality":dict(active),"retained_by_modality":dict(retained),"dropped_by_modality":{m:active[m]-retained[m] for m in ("basal","bolus","food")},"manifest_sha256":checksum,"window_identity_sha256":cgm["window_verification"]["window_identity_sha256"],"identifiers_emitted":False}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n"); print(json.dumps(report,indent=2,sort_keys=True))
if __name__=="__main__": main()
