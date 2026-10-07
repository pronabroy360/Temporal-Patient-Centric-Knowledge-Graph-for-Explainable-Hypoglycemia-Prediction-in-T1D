"""Kaggle GPU trainer for the frozen 64-event Loop sequence comparator.

Run from a Kaggle notebook after the validation cell. It uses outer-0 train
participants for fitting and outer-0 validation participants for scoring.
"""
from pathlib import Path
import argparse, json, sys, gzip
from collections import defaultdict
import numpy as np
import torch
from torch import nn
from sklearn.metrics import average_precision_score, brier_score_loss

# Kaggle expands attached .gz files into plain text files.  Keep the runner
# compatible with both local compressed caches and Kaggle's mounted inputs.
_REAL_GZIP_OPEN = gzip.open
def _kaggle_gzip_open(filename, mode="rb", *args, **kwargs):
    path = Path(filename)
    if "r" in mode and path.suffix != ".gz":
        return open(path, mode, *args, **kwargs)
    return _REAL_GZIP_OPEN(path, mode, *args, **kwargs)
gzip.open = _kaggle_gzip_open

ROOT=Path('/kaggle/input'); INPUT=next(p.parent for p in ROOT.rglob('input_contract.json')); CODE=next(p.parents[1] for p in ROOT.rglob('src/t1d_tkg')); sys.path.insert(0,str(CODE/'scripts')); sys.path.insert(0,str(CODE/'src'))
from run_loop_event_sequence_linear_pilot import sequence_partition
from t1d_tkg.manifest import load_manifest, manifest_checksum

class SequenceGRU(nn.Module):
    def __init__(self, event_width=17, hidden=64):
        super().__init__(); self.event=nn.Sequential(nn.Linear(event_width,32),nn.ReLU()); self.gru=nn.GRU(32,hidden,batch_first=True); self.cgm=nn.Sequential(nn.Linear(2,16),nn.ReLU()); self.head=nn.Sequential(nn.Linear(hidden+16,32),nn.ReLU(),nn.Linear(32,1))
    def forward(self,cgm,events):
        encoded=self.event(events); _,state=self.gru(encoded); return self.head(torch.cat([state[-1],self.cgm(cgm)],1)).squeeze(1)

def batches(cgm_cache,event_cache,patients,max_events,batch_size,partitions):
    cgms=sorted([*cgm_cache.rglob('features-*.tsv'), *cgm_cache.rglob('features-*.tsv.gz')]); events={m:sorted([*event_cache.rglob(f'events-{m}-*.jsonl'), *event_cache.rglob(f'events-{m}-*.jsonl.gz')]) for m in ('basal','bolus','food')}
    if len(cgms) != partitions or any(len(paths) != partitions for paths in events.values()):
        raise RuntimeError(f"cache partition mismatch: cgm={len(cgms)}, events={ {m: len(paths) for m, paths in events.items()} }, expected={partitions}")
    for i in range(partitions):
        rows=defaultdict(list); paths=[events[m][i] for m in ('basal','bolus','food')]
        for patient,_,cgm,seq,label,_,_ in sequence_partition(cgms[i],paths,max_events):
            if patient in patients: rows[patient].append((cgm,seq,label))
        for patient,items in rows.items():
            for start in range(0,len(items),batch_size):
                part=items[start:start+batch_size]; yield patient,np.asarray([x[0] for x in part],np.float32),np.asarray([x[1] for x in part],np.float32).reshape(-1,max_events,17),np.asarray([x[2] for x in part],np.float32)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--epochs',type=int,default=2); ap.add_argument('--batch-size',type=int,default=2048); ap.add_argument('--hidden',type=int,default=64); ap.add_argument('--seed',type=int,default=20260919); ap.add_argument('--output',type=Path,default=Path('/kaggle/working/loop_sequence_gru_result.json')); a=ap.parse_args()
    torch.manual_seed(a.seed); np.random.seed(a.seed); device=torch.device('cuda' if torch.cuda.is_available() else 'cpu'); manifest=load_manifest(INPUT/'loop_model_manifest.json'); fold=next(x for x in manifest['folds'] if x['fold_id']=='outer-0'); train=set(fold['train_patients']); valid=set(fold['validation_patients']); model=SequenceGRU(hidden=a.hidden).to(device); opt=torch.optim.AdamW(model.parameters(),lr=2e-4,weight_decay=1e-4); loss_fn=nn.BCEWithLogitsLoss()
    cgm=INPUT/'loop_cgm_feature_cache'; event=INPUT/'loop_event_instance_cache'; partitions=int(json.loads((cgm/'metadata.json').read_text())['partitions'])
    model.train()
    for epoch in range(a.epochs):
        total=0
        for _,x,e,y in batches(cgm,event,train,64,a.batch_size,partitions):
            opt.zero_grad(set_to_none=True); pred=model(torch.as_tensor(x,device=device),torch.as_tensor(e,device=device)); loss=loss_fn(pred,torch.as_tensor(y,device=device)); loss.backward(); opt.step(); total+=len(y)
        print({'epoch':epoch+1,'training_windows':total,'device':str(device)},flush=True)
    model.eval(); by_patient=defaultdict(lambda:[[],[]]);
    with torch.no_grad():
        for patient,x,e,y in batches(cgm,event,valid,64,a.batch_size,partitions):
            score=torch.sigmoid(model(torch.as_tensor(x,device=device),torch.as_tensor(e,device=device))).cpu().numpy(); by_patient[patient][0].extend(y.tolist()); by_patient[patient][1].extend(score.tolist())
    aps=[]; briers=[]; windows=positives=0
    for labels,scores in by_patient.values():
        windows+=len(labels); positives+=sum(labels); briers.append(brier_score_loss(labels,scores));
        if len(set(labels))>1: aps.append(average_precision_score(labels,scores))
    result={'model':'64-event-sequence-gru','seed':a.seed,'epochs':a.epochs,'hidden':a.hidden,'batch_size':a.batch_size,'device':torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu','fold':'outer-0','participants':len(by_patient),'windows':windows,'positive_labels':positives,'participant_macro_ap':float(np.mean(aps)),'participant_macro_brier':float(np.mean(briers)),'manifest_sha256':manifest_checksum(manifest),'window_identity_sha256':json.loads((cgm/'metadata.json').read_text())['window_verification']['window_identity_sha256'],'max_events':64,'availability_policy':'retrospective occurrence-time replay; immediate availability assumed, not measured'}
    a.output.write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))
if __name__=='__main__': main()
