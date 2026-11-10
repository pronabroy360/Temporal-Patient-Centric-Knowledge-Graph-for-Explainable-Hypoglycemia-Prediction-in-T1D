"""Development-only, capacity-matched full-CGM-history comparison.

This is a new experiment. It cannot load the earlier two-feature checkpoints.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import multiprocessing as mp
import platform
import sys
from itertools import zip_longest
from pathlib import Path
from queue import Empty

import numpy as np

import train_controlled as prior
import train_gru_recovery as legacy

torch, nn = legacy.torch, legacy.nn
VARIANTS = ("history-only", "history-event", "history-event-zero",
            "history-event-capacity-matched")
EVENT_WIDTH = 17
MAX_EVENTS = 64
CAPACITY_MATCHED_WIDTHS = {"cgm": 66, "event_embedding": 27,
                           "event_gru": 67, "head": 24}
CAPACITY_MATCHED_PARAMETERS = 36_883


def select_training_device(preference="auto"):
    """Select a supported accelerator, preserving explicit user choices."""
    if torch is None:
        raise RuntimeError("PyTorch is required")
    if preference not in ("auto", "cuda", "mps"):
        raise ValueError(f"unsupported research device: {preference}")
    if preference in ("auto", "cuda") and torch.cuda.is_available():
        return torch.device("cuda:0")
    mps = getattr(torch.backends, "mps", None)
    if preference in ("auto", "mps") and mps is not None and mps.is_available():
        return torch.device("mps")
    if preference == "auto":
        raise RuntimeError("research-scale training requires CUDA or Apple MPS")
    raise RuntimeError(f"requested research device is unavailable: {preference}")


def gru_parameter_count(input_width: int, hidden_width: int) -> int:
    """PyTorch's single-layer, unidirectional GRU parameter count with biases."""
    return 3 * input_width * hidden_width + 3 * hidden_width**2 + 6 * hidden_width


def capacity_matched_parameter_count(widths=CAPACITY_MATCHED_WIDTHS) -> int:
    cgm = widths["cgm"]
    event_embedding = widths["event_embedding"]
    event_gru = widths["event_gru"]
    head = widths["head"]
    return (gru_parameter_count(2, cgm) + EVENT_WIDTH * event_embedding
            + event_embedding + gru_parameter_count(event_embedding, event_gru)
            + (cgm + event_gru) * head + head + head + 1)


class HistoryModel(nn.Module if nn is not None else object):
    def __init__(self, variant: str):
        super().__init__()
        if variant not in VARIANTS:
            raise ValueError("unknown full-history variant")
        self.variant = variant
        if variant == "history-only":
            # 36,607 parameters; joint variant has 36,609.
            self.cgm = nn.GRU(2, 100, batch_first=True)
            self.head = nn.Sequential(nn.Linear(100, 53), nn.ReLU(), nn.Linear(53, 1))
        elif variant == "history-event-capacity-matched":
            widths = CAPACITY_MATCHED_WIDTHS
            self.cgm = nn.GRU(2, widths["cgm"], batch_first=True)
            self.event_embed = nn.Sequential(
                nn.Linear(EVENT_WIDTH, widths["event_embedding"]), nn.ReLU())
            self.event_gru = nn.GRU(widths["event_embedding"], widths["event_gru"],
                                    batch_first=True)
            self.head = nn.Sequential(
                nn.Linear(widths["cgm"] + widths["event_gru"], widths["head"]),
                nn.ReLU(), nn.Linear(widths["head"], 1))
        else:
            self.cgm = nn.GRU(2, 64, batch_first=True)
            self.event_embed = nn.Sequential(nn.Linear(EVENT_WIDTH, 32), nn.ReLU())
            self.event_gru = nn.GRU(32, 64, batch_first=True)
            self.head = nn.Sequential(nn.Linear(128, 32), nn.ReLU(), nn.Linear(32, 1))

    def forward(self, history, events):
        # History columns: observed value in mg/dL and observed mask. A zero
        # payload is never treated as a measured glucose value.
        scaled = torch.stack((history[:, :, 0] / 100.0, history[:, :, 1]), dim=2)
        _, state = self.cgm(scaled)
        cgm_state = state[-1]
        if self.variant == "history-only":
            return self.head(cgm_state).squeeze(1)
        if self.variant == "history-event-zero":
            event_state = torch.zeros_like(cgm_state)
        else:
            event_input = events.clone()
            event_input[:, :, 15:17] = 0  # Never use export-derived provenance.
            scale = (10.0 * event_input[:, :, 1] + 25.0 * event_input[:, :, 2]
                     + 150.0 * event_input[:, :, 3]).clamp_min(1.0)
            event_input[:, :, 13] = event_input[:, :, 13] / scale
            lengths = event_input[:, :, 0].sum(dim=1).long()
            output, _ = self.event_gru(self.event_embed(event_input))
            final = output[torch.arange(output.shape[0], device=output.device),
                           (lengths - 1).clamp_min(0)]
            event_state = torch.where((lengths > 0).unsqueeze(1), final,
                                      torch.zeros_like(final))
        return self.head(torch.cat((cgm_state, event_state), dim=1)).squeeze(1)


def source_digest(code_directory: Path) -> str:
    code_directory = Path(code_directory).resolve()
    digest = hashlib.sha256()
    files = [*Path(code_directory).joinpath("src").rglob("*.py"),
             *Path(code_directory).joinpath("scripts").glob("*.py"),
             Path(__file__).resolve(), Path(prior.__file__).resolve(),
             Path(legacy.__file__).resolve()]
    for path in sorted(files, key=lambda p: str(p.relative_to(code_directory))):
        logical = path.relative_to(code_directory)
        digest.update(str(logical).encode() + b"\0" + path.read_bytes() + b"\0")
    return digest.hexdigest()


def input_stat_digest(input_directory: Path) -> str:
    """Fingerprint staged files quickly after a full preflight has passed.

    This lets the two matched fits reuse one expensive content verification,
    while refusing to train if any staged input file changes afterwards.
    """
    root = Path(input_directory).resolve()
    entries = []
    for path in sorted((item for item in root.rglob("*") if item.is_file()),
                       key=lambda item: str(item.relative_to(root))):
        stat = path.stat()
        entries.append((str(path.relative_to(root)), stat.st_size, stat.st_mtime_ns))
    # Keep this helper independent of `object_digest`, which is imported inside
    # main() for the CLI. Calling that local import here caused preflight to
    # finish its expensive verification and then fail while writing the receipt.
    payload = json.dumps(entries, sort_keys=True, separators=(",", ":"),
                         allow_nan=False).encode()
    return hashlib.sha256(payload).hexdigest()


def history_event_rows(history_path, feature_path, event_paths, *, include_events,
                       eligible_patients=None):
    from t1d_tkg.cgm_history_cache import iter_partition as iter_history
    from run_loop_event_sequence_linear_pilot import sequence_partition

    histories = iter_history(history_path)
    if eligible_patients is not None:
        histories = (row for row in histories if row[0] in eligible_patients)
    source = ((history, None) for history in histories)
    if include_events:
        source = zip_longest(
            histories,
            sequence_partition(feature_path, event_paths, MAX_EVENTS,
                               eligible_patients=eligible_patients),
        )
    for history, event in source:
        if history is None or (include_events and event is None):
            raise ValueError("event and history caches contain different window counts")
        patient, time, label, values, mask = history
        sequence = ()
        if event is not None:
            if (patient, time, label) != (event[0], event[1], event[4]):
                raise ValueError("event and CGM history windows are misaligned")
            sequence = event[3]
        yield patient, time, label, values, mask, sequence


def producer(worker, workers, patients, batch_size, history_paths, feature_paths,
             event_paths, output, include_events):
    try:
        for partition in range(worker, len(history_paths), workers):
            rows = []
            current = None
            emitted = 0

            def flush(patient, chunk):
                nonlocal emitted
                if not chunk:
                    return
                history = np.asarray([
                    list(zip(row[3], row[4], strict=True)) for row in chunk
                ], dtype=np.float32)
                if include_events:
                    events = np.asarray([row[5] for row in chunk], dtype=np.float32).reshape(-1, MAX_EVENTS, EVENT_WIDTH)
                else:
                    events = np.zeros((len(chunk), 1, EVENT_WIDTH), dtype=np.float32)
                labels = np.asarray([row[2] for row in chunk], dtype=np.float32)
                output.put(("batch", patient, [row[1] for row in chunk], history, events, labels))
                emitted += len(chunk)

            modality_paths = [event_paths[name][partition] for name in legacy.MODALITIES]
            for row in history_event_rows(history_paths[partition], feature_paths[partition],
                                          modality_paths, include_events=include_events,
                                          eligible_patients=patients):
                patient = row[0]
                if patient not in patients:
                    continue
                if current is not None and patient != current:
                    flush(current, rows)
                    rows = []
                current = patient
                rows.append(row)
                if len(rows) == batch_size:
                    flush(current, rows)
                    rows = []
            if current is not None:
                flush(current, rows)
            output.put(("partition", partition + 1, emitted))
        output.put(("done", worker))
    except BaseException as error:
        output.put(("error", worker, repr(error)))


def batches(patients, batch_size, workers, history_paths, feature_paths,
            event_paths, *, include_events):
    context = mp.get_context("spawn")
    queues = [context.Queue(maxsize=2) for _ in range(workers)]
    processes = [context.Process(target=producer,
                 args=(worker, workers, patients, batch_size, history_paths,
                       feature_paths, event_paths, queues[worker], include_events), daemon=True)
                 for worker in range(workers)]
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
                            raise RuntimeError(f"history producer {worker} exited without completion")
                        print({"stage": "waiting_for_history_producer", "worker": worker}, flush=True)
                if item[0] == "batch":
                    yield item[1:]
                elif item[0] == "partition":
                    print({"partition": item[1], "windows_emitted": item[2]}, flush=True)
                elif item[0] == "done":
                    active[worker] = False
                else:
                    raise RuntimeError(f"history producer {item[1]} failed: {item[2]}")
    finally:
        for process in processes:
            process.join(timeout=5)
            if process.is_alive():
                process.terminate()
        for output in queues:
            output.close()


def evaluate(model, patients, args, device, history_paths, feature_paths,
             event_paths, average_precision, *, include_events):
    prediction_dir = args.run_directory / "predictions"
    prediction_dir.mkdir(exist_ok=True)
    model.eval()
    with torch.no_grad():
        for patient, times, history, events, labels in batches(
            patients, args.batch_size, args.workers, history_paths, feature_paths,
            event_paths, include_events=include_events
        ):
            scores = torch.sigmoid(model(torch.as_tensor(history, device=device),
                                         torch.as_tensor(events, device=device))).cpu().numpy()
            legacy.append_predictions(prediction_dir, "validation", patient, times, labels, scores)

    participants = windows = positives = ap_count = 0
    ap_sum = squared_sum = macro_brier_sum = 0.0
    identities = []
    for path in sorted(prediction_dir.glob("validation-*.jsonl.gz")):
        labels = []
        scores = []
        digest = hashlib.sha256()
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                labels.append(int(row["label"]))
                scores.append(float(row["score"]))
                digest.update(f"{row['index_time']}|{row['label']}\n".encode())
        if not labels:
            raise ValueError("empty participant prediction archive")
        participants += 1
        windows += len(labels)
        positives += sum(labels)
        squared = sum((label - score) ** 2 for label, score in zip(labels, scores, strict=True))
        squared_sum += squared
        macro_brier_sum += squared / len(labels)
        ap = average_precision(labels, scores)
        if ap is not None:
            ap_count += 1
            ap_sum += ap
        identities.append((path.name, len(labels), digest.hexdigest()))
    if participants != len(patients) or not ap_count:
        raise ValueError("prediction archives do not cover the selected participants")
    return {"participants": participants, "windows": windows, "positive_labels": positives,
            "ap_defined_participants": ap_count, "participant_macro_ap": ap_sum / ap_count,
            "participant_macro_brier": macro_brier_sum / participants,
            "pooled_brier": squared_sum / windows,
            "prediction_window_identity_sha256": hashlib.sha256(
                json.dumps(identities, separators=(",", ":")).encode()).hexdigest()}


def smoke_test(device="cpu"):
    if torch is None:
        raise RuntimeError("PyTorch is required for full-history model preflight")
    torch.manual_seed(7)
    history = torch.zeros(2, 24, 2, device=device)
    history[:, :, 0] = 110
    history[:, :, 1] = 1
    events = torch.zeros(2, 64, EVENT_WIDTH, device=device)
    events[0, :2, 0] = 1
    counts = {}
    for variant in VARIANTS:
        model = HistoryModel(variant).to(device)
        logits = model(history, events)
        if logits.shape != (2,) or not torch.isfinite(logits).all():
            raise RuntimeError("history model forward pass failed")
        if variant not in ("history-event", "history-event-capacity-matched"):
            torch.testing.assert_close(logits, model(history, torch.ones_like(events)))
        changed = history.clone()
        changed[0, :, 1] = 0
        changed_logits = model(changed, events)
        sensitivity = (logits - changed_logits).abs().max()
        if float(sensitivity) <= 1e-7:
            raise RuntimeError(
                f"{variant} does not respond to a full-sequence missingness change "
                f"on {device} (max logit delta={float(sensitivity):.3g})"
            )
        if str(device).startswith("cuda") and torch.cuda.device_count() > 1:
            torch.testing.assert_close(logits, nn.DataParallel(model)(history, events),
                                       rtol=1e-4, atol=1e-5)
        loss = nn.BCEWithLogitsLoss()(logits, torch.tensor([1.0, 0.0], device=device))
        loss.backward()
        if not all(torch.isfinite(parameter.grad).all() for parameter in model.parameters() if parameter.grad is not None):
            raise RuntimeError("nonfinite history model gradients")
        counts[variant] = sum(parameter.numel() for parameter in model.parameters())
    expected_counts = {"history-only": 36607, "history-event": 36609,
                       "history-event-zero": 36609,
                       "history-event-capacity-matched": CAPACITY_MATCHED_PARAMETERS}
    if counts != expected_counts:
        raise RuntimeError(f"unexpected model parameter budget: {counts}")
    print({"history_model_preflight": "passed", "device": str(device),
           "parameters": counts}, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--fixture-only", action="store_true")
    parser.add_argument("--mode", choices=("preflight", "train"), default="preflight")
    parser.add_argument("--input-directory", type=Path)
    parser.add_argument("--code-directory", type=Path)
    parser.add_argument("--run-directory", type=Path)
    parser.add_argument("--preflight-receipt", type=Path,
                        help="reuse a matching receipt written by a completed full preflight")
    parser.add_argument("--variant", choices=VARIANTS, default="history-only")
    parser.add_argument("--fold", default="outer-0")
    parser.add_argument("--seed", type=int, default=20261003)
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=4096)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--device", choices=("auto", "cuda", "mps"), default="auto",
                        help="auto prefers CUDA then Apple MPS; CPU is reserved for fixtures")
    args = parser.parse_args()
    if args.self_test:
        smoke_test()
        return
    if min(args.epochs, args.batch_size, args.workers) < 1:
        raise ValueError("epochs, batch size and workers must be positive")
    if args.input_directory is None or args.code_directory is None:
        raise ValueError("input and code directories are required")
    args.code_directory = args.code_directory.resolve()
    sys.path.insert(0, str(args.code_directory / "src"))
    sys.path.insert(0, str(args.code_directory / "scripts"))
    from t1d_tkg.cache_io import discover_cache_files
    from t1d_tkg.cgm_history_contract import verify_history_cache
    from t1d_tkg.manifest import load_manifest, manifest_checksum
    from t1d_tkg.metrics import METRIC_VERSION, average_precision
    from t1d_tkg.neural_contract import (checkpoint_contract, membership_digest,
                                         object_digest, verify_inputs)

    manifest = load_manifest(args.input_directory / "loop_model_manifest.json")
    checksum = manifest_checksum(manifest)
    input_contract = json.loads((args.input_directory / "input_contract.json").read_text())
    if (input_contract.get("manifest_sha256") != checksum
            or input_contract.get("max_events") != 64
            or input_contract.get("history_minutes") != 120
            or input_contract.get("contains_locked_holdout") is not False
            or input_contract.get("cgm_history_cache_version") != "loop-cgm-history-cache-v1"):
        raise ValueError("input is not the new development-only full-history contract")
    fold = next((item for item in manifest["folds"] if item["fold_id"] == args.fold), None)
    if fold is None:
        raise ValueError("unknown model fold")
    train = set(fold["train_patients"])
    validation = set(fold["validation_patients"])
    history_dir = args.input_directory / "loop_cgm_history_cache"
    feature_dir = args.input_directory / "loop_cgm_feature_cache"
    event_dir = args.input_directory / "loop_event_instance_cache"
    cgm_meta, event_meta, feature_paths, event_paths = legacy.load_staged_metadata(args.input_directory, checksum)
    window_hash = cgm_meta["window_verification"]["window_identity_sha256"]
    if (input_contract.get("window_identity_sha256") != window_hash
            or event_meta.get("cgm_window_identity_sha256") != window_hash
            or event_meta.get("development_participants") != len(manifest["patients"])):
        raise ValueError("frozen window identity differs across inputs")
    history_paths = discover_cache_files(history_dir, "history-*.tsv*")
    if args.mode == "train" and args.preflight_receipt is not None:
        receipt = json.loads(args.preflight_receipt.read_text())
        if (receipt.get("receipt_version") != "loop-full-history-preflight-receipt-v1"
                or receipt.get("manifest_sha256") != checksum
                or receipt.get("window_identity_sha256") != window_hash
                or receipt.get("fold") != args.fold
                or receipt.get("input_stat_sha256") != input_stat_digest(args.input_directory)):
            raise ValueError("preflight receipt does not match this staged input, fold, or manifest")
        expected = receipt.get("expected", {})
        if set(expected) != set(manifest["patients"]):
            raise ValueError("preflight receipt does not cover exactly the development cohort")
        history_hash = receipt["history_content_sha256"]
        prior_hash = receipt["prior_content_sha256"]
        content_hash = object_digest({"history": history_hash, "prior": prior_hash})
        if content_hash != receipt.get("input_content_sha256"):
            raise ValueError("preflight receipt content fingerprint is invalid")
        print({"stage": "reuse_verified_preflight", "receipt": str(args.preflight_receipt)}, flush=True)
    else:
        print({"stage": "verify_full_history_input"}, flush=True)
        history_hash, expected = verify_history_cache(history_dir, feature_dir,
            manifest_sha256=checksum, patients=set(manifest["patients"]),
            window_identity_sha256=window_hash)
        if (input_contract.get("cgm_history_input_content_sha256") != history_hash
                or input_contract.get("partitions") != cgm_meta["partitions"]):
            raise ValueError("full-history input contract differs from staged cache content")
        prior_hash, prior_expected = verify_inputs(cgm_meta, event_meta, feature_paths,
            event_paths, set(manifest["patients"]),
            progress=lambda item: print(item, flush=True))
        if expected != prior_expected or len(history_paths) != int(cgm_meta["partitions"]):
            raise ValueError("history and prior model inputs have different windows")
        content_hash = object_digest({"history": history_hash, "prior": prior_hash})
    if args.mode == "preflight":
        smoke_test()
        if args.preflight_receipt is not None:
            receipt = {
                "receipt_version": "loop-full-history-preflight-receipt-v1",
                "manifest_sha256": checksum,
                "window_identity_sha256": window_hash,
                "fold": args.fold,
                "history_content_sha256": history_hash,
                "prior_content_sha256": prior_hash,
                "input_content_sha256": content_hash,
                "input_stat_sha256": input_stat_digest(args.input_directory),
                "expected": expected,
            }
            legacy.atomic_json(args.preflight_receipt, receipt)
            print({"preflight_receipt": str(args.preflight_receipt),
                   "receipt_participants": len(expected)}, flush=True)
        print({"input_preflight": "passed", "input_content_sha256": content_hash,
               "participants": len(expected)}, flush=True)
        return
    if args.run_directory is None or args.run_directory.exists():
        raise ValueError("choose a new run directory")
    if torch is None:
        raise RuntimeError("PyTorch is required")
    if args.fixture_only:
        if len(expected) > 30 or sum(item["records"] for item in expected.values()) > 1000:
            raise ValueError("fixture mode refuses research-scale input")
    elif args.device == "auto":
        device = select_training_device("auto")
    else:
        device = select_training_device(args.device)
    smoke_test()
    if args.fixture_only:
        device = torch.device("cpu")
    if not args.fixture_only:
        smoke_test(device)
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    base = HistoryModel(args.variant).to(device)
    optimizer_spec = {"name": "AdamW", "learning_rate": 2e-4, "weight_decay": 1e-4,
                      "loss": "BCEWithLogitsLoss", "positive_weight": 1.0}
    configuration = {"contract_version": "loop-full-history-neural-v1",
        "model": "full-cgm-history-controlled", "fixture_only": args.fixture_only,
        "mode": "train",
        "variant": args.variant, "fold": args.fold, "seed": args.seed,
        "hidden": 64, "epochs": args.epochs, "batch_size": args.batch_size,
        "workers": args.workers, "max_events": MAX_EVENTS,
        "manifest_sha256": checksum, "window_identity_sha256": window_hash,
        "input_content_sha256": content_hash,
        "training_membership_sha256": membership_digest(train),
        "optimizer": optimizer_spec, "source_sha256": source_digest(args.code_directory),
        "event_input_policy": "occurrence-replay-no-export-provenance-v1",
        # The fold's train_patients are drawn only from the development
        # population; the locked holdout is never read by this trainer.
        "locked_holdout_used": False,
        "evaluation_scope": "validation", "trainable_parameters": sum(p.numel() for p in base.parameters()),
        "history_steps": 24, "metric_version": METRIC_VERSION, "complete": False,
        "train_windows_expected": sum(expected[patient]["records"] for patient in train),
        "train_positive_labels_expected": sum(
            expected[patient]["positive_labels"] for patient in train),
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "torch": str(torch.__version__), "cuda": torch.version.cuda,
                        "device": str(device),
                        "gpus": ([torch.cuda.get_device_name(i)
                                  for i in range(torch.cuda.device_count())]
                                 if device.type == "cuda" else [])}}
    if args.variant == "history-event-capacity-matched":
        configuration["evaluation_scope"] = "outer-fold validation; development only"
        configuration["architecture"] = {
            "family": "independent-cgm-gru-and-event-gru-late-fusion",
            "graph_message_passing": False,
            "widths": CAPACITY_MATCHED_WIDTHS,
            "parameter_match_target": CAPACITY_MATCHED_PARAMETERS,
        }
    args.run_directory.mkdir(parents=True)
    legacy.atomic_json(args.run_directory / "run.json", configuration)
    model = nn.DataParallel(base) if not args.fixture_only and torch.cuda.device_count() > 1 else base
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-4, weight_decay=1e-4)
    loss_fn = nn.BCEWithLogitsLoss()
    include_events = args.variant in ("history-event", "history-event-capacity-matched")
    for epoch in range(args.epochs):
        model.train()
        count = positive = 0
        for batch_number, (_, _, history, events, labels) in enumerate(batches(
            train, args.batch_size, args.workers, history_paths, feature_paths,
            event_paths, include_events=include_events
        ), 1):
            optimizer.zero_grad(set_to_none=True)
            loss = loss_fn(model(torch.as_tensor(history, device=device),
                                 torch.as_tensor(events, device=device)),
                           torch.as_tensor(labels, device=device))
            if not torch.isfinite(loss):
                raise RuntimeError("nonfinite history training loss")
            loss.backward()
            optimizer.step()
            count += len(labels)
            positive += int(labels.sum())
            if batch_number == 1 or batch_number % 100 == 0:
                print({"stage": "train", "epoch": epoch + 1, "batches": batch_number,
                       "windows": count, "loss": float(loss.detach())}, flush=True)
        if count != sum(expected[p]["records"] for p in train) or positive != sum(
            expected[p]["positive_labels"] for p in train
        ):
            raise ValueError("training count differs from frozen windows")
        checkpoint = args.run_directory / f"checkpoint-epoch-{epoch + 1}.pt"
        temporary = checkpoint.with_suffix(".pt.tmp")
        torch.save({"contract": checkpoint_contract(configuration), "epoch": epoch + 1,
                    "model": base.state_dict(), "optimizer": optimizer.state_dict()}, temporary)
        temporary.replace(checkpoint)
        print({"stage": "checkpoint", "epoch": epoch + 1, "windows": count}, flush=True)
    metrics = evaluate(model, validation, args, device, history_paths, feature_paths,
                       event_paths, average_precision, include_events=include_events)
    prior.verify_predictions(args.run_directory / "predictions", validation, expected)
    report = {**configuration, "complete": True, "groups": {"validation": metrics},
              "prediction_identity_verified": True,
              "availability_policy": "retrospective occurrence-time replay; immediate availability assumed, not measured",
              "artifacts": str(args.run_directory)}
    legacy.atomic_json(args.run_directory / "result.json", report)
    legacy.atomic_json(args.run_directory / "run.json", report)
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
