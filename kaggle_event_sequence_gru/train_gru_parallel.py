"""Parallel Kaggle trainer for the frozen 64-event Loop GRU comparator.

The Kaggle upload expands gzip inputs and strips their final suffix. Three
deterministic producer processes construct sequence batches concurrently; the
consumer trains in a fixed round-robin producer order and uses both T4 GPUs.
"""
from __future__ import annotations

import argparse
import gzip
import json
import multiprocessing as mp
import queue
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import average_precision_score, brier_score_loss
from torch import nn


ROOT = Path("/kaggle/input/datasets/roypro360")
INPUT = ROOT / "kaggle-loop-sequence-input" / "kaggle_loop_sequence_input"
CODE = ROOT / "t1d-tkg-code"
sys.path.insert(0, str(CODE / "scripts"))
sys.path.insert(0, str(CODE / "src"))

# Kaggle expands the uploaded gzip streams but the project readers use
# gzip.open. Builtin open accepts the same text-read arguments used here.
gzip.open = open

from run_loop_event_sequence_linear_pilot import sequence_partition
from t1d_tkg.manifest import load_manifest, manifest_checksum


MAX_EVENTS = 64
EVENT_WIDTH = 17
MODALITIES = ("basal", "bolus", "food")


class SequenceGRU(nn.Module):
    def __init__(self, hidden: int = 64):
        super().__init__()
        self.event = nn.Sequential(nn.Linear(EVENT_WIDTH, 32), nn.ReLU())
        self.gru = nn.GRU(32, hidden, batch_first=True)
        self.cgm = nn.Sequential(nn.Linear(2, 16), nn.ReLU())
        self.head = nn.Sequential(
            nn.Linear(hidden + 16, 32), nn.ReLU(), nn.Linear(32, 1)
        )

    def forward(self, cgm, events):
        cgm = torch.stack((cgm[:, 0] / 100.0, cgm[:, 1] / 20.0), dim=1)
        events = events.clone()
        value_scale = (
            10.0 * events[:, :, 1]
            + 25.0 * events[:, :, 2]
            + 150.0 * events[:, :, 3]
        ).clamp_min(1.0)
        events[:, :, 13] = events[:, :, 13] / value_scale
        lengths = events[:, :, 0].sum(dim=1).long()
        encoded = self.event(events)
        outputs, _ = self.gru(encoded)
        final_index = (lengths - 1).clamp_min(0)
        hidden = outputs[torch.arange(outputs.shape[0], device=outputs.device), final_index]
        hidden = torch.where((lengths > 0).unsqueeze(1), hidden, torch.zeros_like(hidden))
        return self.head(torch.cat((hidden, self.cgm(cgm)), dim=1)).squeeze(1)


def cache_paths():
    cgm_dir = INPUT / "loop_cgm_feature_cache"
    event_dir = INPUT / "loop_event_instance_cache"
    cgms = sorted(cgm_dir.glob("features-*.tsv"))
    events = {
        modality: sorted(event_dir.glob(f"events-{modality}-*.jsonl"))
        for modality in MODALITIES
    }
    if len(cgms) != 64 or any(len(paths) != 64 for paths in events.values()):
        raise RuntimeError(
            f"cache mismatch: cgm={len(cgms)}, events="
            f"{ {name: len(paths) for name, paths in events.items()} }"
        )
    return cgms, events


def producer(worker_id, workers, patients, batch_size, output):
    try:
        cgms, events = cache_paths()
        for partition in range(worker_id, len(cgms), workers):
            paths = [events[modality][partition] for modality in MODALITIES]
            current = None
            rows = []
            emitted = 0

            def flush(patient, values):
                nonlocal emitted
                for start in range(0, len(values), batch_size):
                    part = values[start : start + batch_size]
                    emitted += len(part)
                    output.put(
                        (
                            "batch",
                            patient,
                            np.asarray([row[0] for row in part], dtype=np.float32),
                            np.asarray([row[1] for row in part], dtype=np.float32).reshape(
                                -1, MAX_EVENTS, EVENT_WIDTH
                            ),
                            np.asarray([row[2] for row in part], dtype=np.float32),
                        )
                    )

            for patient, _, cgm, sequence, label, _, _ in sequence_partition(
                cgms[partition], paths, MAX_EVENTS
            ):
                if patient not in patients:
                    continue
                if current is None:
                    current = patient
                if patient != current:
                    flush(current, rows)
                    current, rows = patient, []
                rows.append((cgm, sequence, label))
                # Emit full batches as soon as they are constructed. Holding a
                # participant's entire history can retain hundreds of thousands
                # of 64x17 Python tuples and starve the GPUs for minutes.
                if len(rows) >= batch_size:
                    flush(current, rows)
                    rows = []
            if current is not None:
                flush(current, rows)
            output.put(("partition", partition + 1, emitted))
        output.put(("done", worker_id))
    except BaseException as error:
        output.put(("error", worker_id, repr(error)))


def parallel_batches(patients, batch_size, workers):
    # Spawn avoids inheriting the already-created CUDA context into CPU-only
    # producers. Forking after CUDA initialization can hang on Kaggle/Linux.
    context = mp.get_context("spawn")
    outputs = [context.Queue(maxsize=2) for _ in range(workers)]
    processes = [
        context.Process(
            target=producer,
            args=(worker, workers, patients, batch_size, outputs[worker]),
            daemon=True,
        )
        for worker in range(workers)
    ]
    for process in processes:
        process.start()
    active = [True] * workers
    try:
        while any(active):
            for worker, output in enumerate(outputs):
                if not active[worker]:
                    continue
                item = output.get()
                kind = item[0]
                if kind == "batch":
                    yield item[1:]
                elif kind == "partition":
                    print(
                        {"partition": item[1], "windows_emitted": item[2]}, flush=True
                    )
                elif kind == "done":
                    active[worker] = False
                elif kind == "error":
                    raise RuntimeError(f"producer {item[1]} failed: {item[2]}")
    finally:
        for process in processes:
            process.join(timeout=2)
            if process.is_alive():
                process.terminate()
        for output in outputs:
            output.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=4096)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--hidden", type=int, default=64)
    parser.add_argument("--seed", type=int, default=20260920)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("/kaggle/working/loop_sequence_gru_result.json"),
    )
    args = parser.parse_args()
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    if not torch.cuda.is_available() or torch.cuda.device_count() < 2:
        raise RuntimeError("this run requires the configured two-T4 Kaggle accelerator")

    manifest = load_manifest(INPUT / "loop_model_manifest.json")
    fold = next(item for item in manifest["folds"] if item["fold_id"] == "outer-0")
    train = set(fold["train_patients"])
    valid = set(fold["validation_patients"])
    device = torch.device("cuda:0")
    base_model = SequenceGRU(hidden=args.hidden).to(device)
    model = nn.DataParallel(base_model, device_ids=[0, 1])
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-4, weight_decay=1e-4)
    loss_fn = nn.BCEWithLogitsLoss()

    for epoch in range(args.epochs):
        model.train()
        total = batches = 0
        for _, cgm, events, labels in parallel_batches(
            train, args.batch_size, args.workers
        ):
            optimizer.zero_grad(set_to_none=True)
            prediction = model(
                torch.as_tensor(cgm, device=device),
                torch.as_tensor(events, device=device),
            )
            loss = loss_fn(prediction, torch.as_tensor(labels, device=device))
            loss.backward()
            optimizer.step()
            total += len(labels)
            batches += 1
            if batches % 100 == 0:
                print(
                    {
                        "epoch": epoch + 1,
                        "batches": batches,
                        "training_windows": total,
                        "loss": float(loss.detach()),
                    },
                    flush=True,
                )
        torch.save(
            {
                "epoch": epoch + 1,
                "model": base_model.state_dict(),
                "optimizer": optimizer.state_dict(),
                "seed": args.seed,
            },
            f"/kaggle/working/loop_sequence_gru_epoch{epoch + 1}.pt",
        )
        print({"epoch_complete": epoch + 1, "training_windows": total}, flush=True)

    model.eval()
    by_patient = defaultdict(lambda: [[], []])
    with torch.no_grad():
        for patient, cgm, events, labels in parallel_batches(
            valid, args.batch_size, args.workers
        ):
            scores = torch.sigmoid(
                model(
                    torch.as_tensor(cgm, device=device),
                    torch.as_tensor(events, device=device),
                )
            ).cpu().numpy()
            by_patient[patient][0].extend(labels.tolist())
            by_patient[patient][1].extend(scores.tolist())

    aps, briers = [], []
    windows = positives = 0
    for labels, scores in by_patient.values():
        windows += len(labels)
        positives += sum(labels)
        briers.append(brier_score_loss(labels, scores))
        if len(set(labels)) > 1:
            aps.append(average_precision_score(labels, scores))
    cgm_metadata = json.loads(
        (INPUT / "loop_cgm_feature_cache" / "metadata.json").read_text()
    )
    result = {
        "model": "64-event-sequence-gru-parallel-v2",
        "seed": args.seed,
        "epochs": args.epochs,
        "hidden": args.hidden,
        "batch_size": args.batch_size,
        "producer_workers": args.workers,
        "gpu_count": torch.cuda.device_count(),
        "gpus": [torch.cuda.get_device_name(index) for index in range(2)],
        "fold": "outer-0",
        "participants": len(by_patient),
        "windows": windows,
        "positive_labels": positives,
        "participant_macro_ap": float(np.mean(aps)),
        "participant_macro_brier": float(np.mean(briers)),
        "manifest_sha256": manifest_checksum(manifest),
        "window_identity_sha256": cgm_metadata["window_verification"][
            "window_identity_sha256"
        ],
        "max_events": MAX_EVENTS,
        "availability_policy": (
            "retrospective occurrence-time replay; immediate availability assumed, "
            "not measured"
        ),
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
