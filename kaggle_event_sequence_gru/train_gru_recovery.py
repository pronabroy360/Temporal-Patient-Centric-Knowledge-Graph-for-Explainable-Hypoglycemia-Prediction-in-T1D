"""Recoverable Kaggle trainer/evaluator for the Loop 64-event GRU comparator.

This runner deliberately keeps the original ``train_gru_parallel.py`` pilot
unchanged.  Every new run has a unique directory, writes reloadable
checkpoints, and persists private participant-level predictions so metrics can
be recomputed without retraining.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import multiprocessing as mp
import os
import sys
from queue import Empty
from collections import Counter
from pathlib import Path

import numpy as np

try:  # Permit --help and static checks on the CPU-only development machine.
    import torch
    from torch import nn
except ModuleNotFoundError:  # Kaggle supplies PyTorch for actual execution.
    torch = None
    nn = None


MAX_EVENTS = 64
EVENT_WIDTH = 17
MODALITIES = ("basal", "bolus", "food")
_REAL_GZIP_OPEN = gzip.open


def kaggle_gzip_open(filename, mode="rb", *args, **kwargs):
    """Read Kaggle-expanded input streams while still compressing artifacts."""
    path = Path(filename)
    if "r" in mode and path.suffix != ".gz":
        return open(path, mode, *args, **kwargs)
    return _REAL_GZIP_OPEN(path, mode, *args, **kwargs)


# Cache readers now handle expanded files explicitly. Do not mutate gzip.open
# process-wide; artifact writers must continue to produce actual gzip streams.


class SequenceGRU(nn.Module if nn is not None else object):
    def __init__(self, hidden: int = 64):
        super().__init__()
        self.event = nn.Sequential(nn.Linear(EVENT_WIDTH, 32), nn.ReLU())
        self.gru = nn.GRU(32, hidden, batch_first=True)
        self.cgm = nn.Sequential(nn.Linear(2, 16), nn.ReLU())
        self.head = nn.Sequential(nn.Linear(hidden + 16, 32), nn.ReLU(), nn.Linear(32, 1))

    def forward(self, cgm, events):
        cgm = torch.stack((cgm[:, 0] / 100.0, cgm[:, 1] / 20.0), dim=1)
        events = events.clone()
        value_scale = (10.0 * events[:, :, 1] + 25.0 * events[:, :, 2] + 150.0 * events[:, :, 3]).clamp_min(1.0)
        events[:, :, 13] = events[:, :, 13] / value_scale
        lengths = events[:, :, 0].sum(dim=1).long()
        outputs, _ = self.gru(self.event(events))
        final = outputs[torch.arange(outputs.shape[0], device=outputs.device), (lengths - 1).clamp_min(0)]
        final = torch.where((lengths > 0).unsqueeze(1), final, torch.zeros_like(final))
        return self.head(torch.cat((final, self.cgm(cgm)), dim=1)).squeeze(1)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("train", "evaluate"), default="train")
    parser.add_argument("--run-directory", type=Path, required=True)
    parser.add_argument("--input-directory", type=Path)
    parser.add_argument("--code-directory", type=Path)
    parser.add_argument("--fold", default="outer-0")
    parser.add_argument("--evaluation-scope", choices=("validation", "development-test"), default="validation")
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=4096)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--hidden", type=int, default=64)
    parser.add_argument("--seed", type=int, default=20260920)
    return parser.parse_args()


def discover_paths(args):
    root = Path("/kaggle/input")
    if args.input_directory is None:
        contracts = list(root.rglob("input_contract.json"))
        if len(contracts) != 1:
            raise RuntimeError(f"expected one input_contract.json, found {contracts}")
        args.input_directory = contracts[0].parent
    if args.code_directory is None:
        roots = list(root.rglob("src/t1d_tkg"))
        if len(roots) != 1:
            raise RuntimeError(f"expected one project src/t1d_tkg directory, found {roots}")
        args.code_directory = roots[0].parents[1]
    if not (args.input_directory / "loop_model_manifest.json").is_file():
        raise FileNotFoundError("input directory lacks loop_model_manifest.json")
    sys.path.insert(0, str(args.code_directory / "scripts"))
    sys.path.insert(0, str(args.code_directory / "src"))


def paths(input_directory: Path, partitions: int):
    from t1d_tkg.cache_io import discover_cache_files
    cgm = discover_cache_files(input_directory / "loop_cgm_feature_cache", "features-*.tsv*")
    events = {modality: discover_cache_files(input_directory / "loop_event_instance_cache", f"events-{modality}-*.jsonl*") for modality in MODALITIES}
    if len(cgm) != partitions or any(len(value) != partitions for value in events.values()):
        raise RuntimeError("cache partition files do not match cache metadata")
    return cgm, events


def producer(worker, workers, patients, batch_size, cgm_paths, event_paths, output, cgm_only=False):
    from run_loop_event_sequence_linear_pilot import sequence_partition
    from t1d_tkg.feature_cache import iter_partition
    try:
        for partition in range(worker, len(cgm_paths), workers):
            rows = []
            current = None
            emitted = 0

            def flush(patient, values):
                nonlocal emitted
                for start in range(0, len(values), batch_size):
                    chunk = values[start : start + batch_size]
                    emitted += len(chunk)
                    event_array = np.zeros((len(chunk), 1, EVENT_WIDTH), dtype=np.float32) if cgm_only else np.asarray([row[2] for row in chunk], dtype=np.float32).reshape(-1, MAX_EVENTS, EVENT_WIDTH)
                    output.put(("batch", patient, [row[0] for row in chunk], np.asarray([row[1] for row in chunk], dtype=np.float32), event_array, np.asarray([row[3] for row in chunk], dtype=np.float32)))

            modality_paths = [event_paths[modality][partition] for modality in MODALITIES]
            if cgm_only:
                source = ((patient, time, cgm, (), label, 0, 0) for patient, time, label, cgm in iter_partition(cgm_paths[partition]))
            else:
                source = sequence_partition(cgm_paths[partition], modality_paths, MAX_EVENTS, eligible_patients=patients)
            for patient, time, cgm, sequence, label, _, _ in source:
                if patient not in patients:
                    continue
                if current is None:
                    current = patient
                if patient != current:
                    flush(current, rows)
                    current, rows = patient, []
                rows.append((time, cgm, sequence, label))
                if len(rows) >= batch_size:
                    flush(current, rows)
                    rows = []
            if current is not None:
                flush(current, rows)
            output.put(("partition", partition + 1, emitted))
        output.put(("done", worker))
    except BaseException as error:
        output.put(("error", worker, repr(error)))


def batches(patients, batch_size, workers, cgm_paths, event_paths, *, cgm_only=False):
    context = mp.get_context("spawn")
    queues = [context.Queue(maxsize=2) for _ in range(workers)]
    processes = [context.Process(target=producer, args=(worker, workers, patients, batch_size, cgm_paths, event_paths, queues[worker], cgm_only), daemon=True) for worker in range(workers)]
    for process in processes:
        process.start()
    active = [True] * workers
    try:
        while any(active):
            for worker, output in enumerate(queues):
                if not active[worker]:
                    continue
                while True:
                    try:
                        item = output.get(timeout=30)
                        break
                    except Empty:
                        if not processes[worker].is_alive():
                            raise RuntimeError(f"producer {worker} exited without reporting completion (exit code {processes[worker].exitcode})")
                        # Preserve the same round-robin batch order rather than
                        # changing SGD order according to which worker is slow.
                        print({"stage": "waiting_for_producer", "worker": worker}, flush=True)
                if item[0] == "batch":
                    yield item[1:]
                elif item[0] == "partition":
                    print({"partition": item[1], "windows_emitted": item[2]}, flush=True)
                elif item[0] == "done":
                    active[worker] = False
                else:
                    raise RuntimeError(f"producer {item[1]} failed: {item[2]}")
    finally:
        for process in processes:
            process.join(timeout=5)
            if process.is_alive():
                process.terminate()
        for output in queues:
            output.close()


def atomic_json(path: Path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def patient_filename(group, patient):
    return f"{group}-{hashlib.sha256(patient.encode()).hexdigest()}.jsonl.gz"


def load_staged_metadata(input_directory: Path, checksum: str):
    """Check cache metadata against files after Kaggle expands .gz inputs."""
    from t1d_tkg.event_cache import EVENT_CACHE_VERSION
    from t1d_tkg.feature_cache import CACHE_VERSION

    cgm_dir = input_directory / "loop_cgm_feature_cache"
    event_dir = input_directory / "loop_event_instance_cache"
    cgm = json.loads((cgm_dir / "metadata.json").read_text(encoding="utf-8"))
    event = json.loads((event_dir / "metadata.json").read_text(encoding="utf-8"))
    if cgm.get("cache_version") != CACHE_VERSION or event.get("cache_version") != EVENT_CACHE_VERSION:
        raise ValueError("unsupported staged cache version")
    if cgm.get("manifest_sha256") != checksum or event.get("manifest_sha256") != checksum:
        raise ValueError("staged caches do not match the model manifest")
    partitions = int(cgm["partitions"])
    cgm_paths, event_paths = paths(input_directory, partitions)
    def staged_name(name):
        return name[:-3] if name.endswith(".gz") else name
    expected_cgm = [staged_name(item["file"]) for item in cgm["partition_summaries"]]
    if expected_cgm != [staged_name(path.name) for path in cgm_paths]:
        raise ValueError("staged CGM files do not match cache metadata")
    expected_events = {staged_name(name) for name in event["files"]}
    actual_events = {staged_name(path.name) for modality in MODALITIES for path in event_paths[modality]}
    if expected_events != actual_events:
        raise ValueError("staged event files do not match cache metadata")
    for modality in MODALITIES:
        expected = [f"events-{modality}-{index:02d}.jsonl" for index in range(partitions)]
        if [staged_name(path.name) for path in event_paths[modality]] != expected:
            raise ValueError("staged event partition indices are misaligned")
    if [staged_name(path.name) for path in cgm_paths] != [f"features-{index:02d}.tsv" for index in range(partitions)]:
        raise ValueError("staged CGM partition indices are misaligned")
    return cgm, event, cgm_paths, event_paths


def append_predictions(directory, group, patient, times, labels, scores):
    path = directory / patient_filename(group, patient)
    with _REAL_GZIP_OPEN(path, "at", encoding="utf-8") as handle:
        for time, label, score in zip(times, labels, scores, strict=True):
            handle.write(json.dumps({"patient_id": patient, "index_time": time, "label": int(label), "score": float(score)}) + "\n")


def evaluate(model, patients, group, args, device, cgm_paths, event_paths, average_precision, *, cgm_only=False):
    prediction_dir = args.run_directory / "predictions"
    prediction_dir.mkdir(exist_ok=True)
    model.eval()
    with torch.no_grad():
        for patient, times, cgm, events, labels in batches(patients, args.batch_size, args.workers, cgm_paths, event_paths, cgm_only=cgm_only):
            scores = torch.sigmoid(model(torch.as_tensor(cgm, device=device), torch.as_tensor(events, device=device))).cpu().numpy()
            append_predictions(prediction_dir, group, patient, times, labels, scores)

    summary = Counter()
    digests = []
    for path in sorted(prediction_dir.glob(f"{group}-*.jsonl.gz")):
        labels = []
        scores = []
        digest = hashlib.sha256()
        with _REAL_GZIP_OPEN(path, "rt", encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                labels.append(int(row["label"]))
                scores.append(float(row["score"]))
                digest.update(f"{row['index_time']}|{row['label']}\n".encode())
        if not labels:
            raise RuntimeError("empty prediction file")
        summary["participants"] += 1
        summary["windows"] += len(labels)
        summary["positive_labels"] += sum(labels)
        squared_error = sum((label - score) ** 2 for label, score in zip(labels, scores, strict=True))
        summary["squared_error_sum"] += squared_error
        summary["participant_brier_sum"] += squared_error / len(labels)
        ap = average_precision(labels, scores)
        if ap is not None:
            summary["ap_sum"] += ap
            summary["ap_defined_participants"] += 1
        digests.append((path.name, len(labels), digest.hexdigest()))
    identity = hashlib.sha256(json.dumps(digests, separators=(",", ":")).encode()).hexdigest()
    if summary["participants"] != len(patients):
        raise RuntimeError("evaluation did not produce one prediction archive per selected participant")
    if not summary["ap_defined_participants"]:
        raise RuntimeError("AP is undefined for every evaluated participant")
    return {
        "participants": summary["participants"], "windows": summary["windows"], "positive_labels": summary["positive_labels"],
        "ap_defined_participants": summary["ap_defined_participants"],
        "participant_macro_ap": summary["ap_sum"] / summary["ap_defined_participants"],
        "pooled_brier": summary["squared_error_sum"] / summary["windows"],
        "participant_macro_brier": summary["participant_brier_sum"] / summary["participants"],
        "prediction_window_identity_sha256": identity,
    }


def main():
    args = parse_args()
    if args.epochs < 1 or args.batch_size < 1 or args.workers < 1 or args.hidden < 1:
        raise ValueError("epochs, batch size, workers, and hidden size must be positive")
    if args.mode == "evaluate" and args.checkpoint is None:
        raise ValueError("--checkpoint is required in evaluate mode")
    if args.mode == "evaluate":
        raise ValueError("legacy checkpoints lack a fold-bound training contract; use verify_recovered_gru_checkpoint.py for the preserved historical run, or train_controlled.py for new checkpoint evaluation")
    if args.run_directory.exists():
        raise FileExistsError("run directory already exists; use a new directory to preserve artifacts")
    args.run_directory.mkdir(parents=True)
    discover_paths(args)
    from t1d_tkg.manifest import load_manifest, manifest_checksum
    from t1d_tkg.metrics import METRIC_VERSION, average_precision

    manifest = load_manifest(args.input_directory / "loop_model_manifest.json")
    checksum = manifest_checksum(manifest)
    contract = json.loads((args.input_directory / "input_contract.json").read_text(encoding="utf-8"))
    if contract.get("manifest_sha256") != checksum or contract.get("max_events") != MAX_EVENTS or contract.get("contains_locked_holdout"):
        raise ValueError("private input contract does not match the declared development-only GRU protocol")
    fold = next((item for item in manifest["folds"] if item["fold_id"] == args.fold), None)
    if fold is None:
        raise ValueError("requested fold is not present in the protected manifest")
    train = set(fold["train_patients"])
    validation = set(fold["validation_patients"])
    development_test = set(fold["test_patients"])
    if train & validation or train & development_test or validation & development_test or train | validation | development_test != set(manifest["patients"]):
        raise ValueError("manifest fold groups are not a disjoint development partition")
    cgm_metadata, event_metadata, cgm_paths, event_paths = load_staged_metadata(args.input_directory, checksum)
    if event_metadata.get("cgm_window_identity_sha256") != cgm_metadata["window_verification"]["window_identity_sha256"]:
        raise ValueError("event and CGM caches have different frozen window identities")
    if contract.get("window_identity_sha256") != cgm_metadata["window_verification"]["window_identity_sha256"]:
        raise ValueError("input contract and CGM cache have different frozen window identities")
    group_name, evaluation_patients = ("validation", validation) if args.evaluation_scope == "validation" else ("development_test", development_test)
    configuration = {"model": "64-event-sequence-gru-recovery-v1", "mode": args.mode, "fold": args.fold, "evaluation_scope": args.evaluation_scope, "seed": args.seed, "epochs": args.epochs, "hidden": args.hidden, "batch_size": args.batch_size, "workers": args.workers, "max_events": MAX_EVENTS, "manifest_sha256": checksum, "window_identity_sha256": cgm_metadata["window_verification"]["window_identity_sha256"], "complete": False}
    atomic_json(args.run_directory / "run.json", configuration)
    if torch is None or nn is None:
        raise RuntimeError("PyTorch is required; run this trainer on the configured Kaggle GPU runtime")
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for this Kaggle runner")
    device = torch.device("cuda:0")
    base = SequenceGRU(hidden=args.hidden).to(device)
    checkpoint = None
    if args.mode == "evaluate":
        checkpoint = torch.load(args.checkpoint, map_location=device, weights_only=False)
        if checkpoint.get("hidden") != args.hidden or checkpoint.get("max_events") != MAX_EVENTS or checkpoint.get("manifest_sha256") != checksum:
            raise ValueError("checkpoint does not match hidden size, event contract, or manifest")
        base.load_state_dict(checkpoint["model"])
    model = nn.DataParallel(base) if torch.cuda.device_count() > 1 else base
    if args.mode == "train":
        optimizer = torch.optim.AdamW(model.parameters(), lr=2e-4, weight_decay=1e-4)
        loss_fn = nn.BCEWithLogitsLoss()
        for epoch in range(args.epochs):
            model.train(); total = batches_seen = 0
            for _, _, cgm, events, labels in batches(train, args.batch_size, args.workers, cgm_paths, event_paths):
                optimizer.zero_grad(set_to_none=True)
                loss = loss_fn(model(torch.as_tensor(cgm, device=device), torch.as_tensor(events, device=device)), torch.as_tensor(labels, device=device))
                loss.backward(); optimizer.step(); total += len(labels); batches_seen += 1
                if batches_seen % 100 == 0:
                    print({"stage": "train", "epoch": epoch + 1, "batches": batches_seen, "windows": total, "loss": float(loss.detach())}, flush=True)
            checkpoint_path = args.run_directory / f"checkpoint-epoch-{epoch + 1}.pt"
            temporary_checkpoint = checkpoint_path.with_suffix(".pt.tmp")
            torch.save({"epoch": epoch + 1, "model": base.state_dict(), "optimizer": optimizer.state_dict(), "seed": args.seed, "hidden": args.hidden, "max_events": MAX_EVENTS, "manifest_sha256": checksum}, temporary_checkpoint)
            temporary_checkpoint.replace(checkpoint_path)
            print({"stage": "checkpoint", "epoch": epoch + 1, "windows": total, "path": checkpoint_path.name}, flush=True)
    metrics = evaluate(model, evaluation_patients, group_name, args, device, cgm_paths, event_paths, average_precision)
    report = {**configuration, "complete": True, "metric_version": METRIC_VERSION, "gpu_count": torch.cuda.device_count(), "gpus": [torch.cuda.get_device_name(index) for index in range(torch.cuda.device_count())], "groups": {group_name: metrics}, "window_verification": {**cgm_metadata["window_verification"], "verification_limit": "cache identity is verified; direct private window-index comparison was not staged to Kaggle"}, "event_cache_version": event_metadata["cache_version"], "availability_policy": "retrospective occurrence-time replay; immediate availability assumed, not measured", "artifacts": str(args.run_directory)}
    atomic_json(args.run_directory / "result.json", report)
    atomic_json(args.run_directory / "run.json", report)
    print(json.dumps(report, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
