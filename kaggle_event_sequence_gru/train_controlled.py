"""Controlled development comparisons; no locked holdout or legacy checkpoint loading."""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
import platform
import sys
import tempfile
from pathlib import Path

import numpy as np
import train_gru_recovery as legacy

torch, nn = legacy.torch, legacy.nn


class ControlledModel(nn.Module if nn is not None else object):
    def __init__(self, variant, hidden=64):
        super().__init__()
        self.variant = variant
        if variant == "cgm-mlp":
            # 22,047 trainable parameters versus 22,065 for the hidden=64 GRU.
            self.network = nn.Sequential(nn.Linear(2, 146), nn.ReLU(), nn.Linear(146, 146), nn.ReLU(), nn.Linear(146, 1))
        else:
            self.network = legacy.SequenceGRU(hidden)

    def forward(self, cgm, events):
        if self.variant == "cgm-mlp":
            scaled = torch.stack((cgm[:, 0] / 100.0, cgm[:, 1] / 20.0), dim=1)
            return self.network(scaled).squeeze(1)
        events = events.clone()
        events[:, :, 15:17] = 0  # Full-export provenance is never a new model input.
        if self.variant == "cgm-gru-mask":
            events.zero_()
        elif self.variant == "recording-gru":
            events[:, :, 4:14] = 0  # Keep record, modality and known-value masks.
        elif self.variant == "type-timing-gru":
            events[:, :, 13] = 0  # Keep value-known mask; remove numerical values.
        elif self.variant == "no-age-gru":
            events[:, :, 12] = 0  # Ordinal newest-first order remains observable.
        return self.network(cgm, events)


def smoke_test(device="cpu"):
    """Execute actual CPU forward/backward/reload tests in the torch runtime."""
    if torch is None:
        raise RuntimeError("PyTorch is required for the model preflight")
    from t1d_tkg.neural_contract import VARIANTS
    torch.manual_seed(7)
    cgm = torch.tensor([[110.0, -2.0], [160.0, 1.0]], device=device)
    events = torch.zeros(2, 64, 17, device=device)
    events[0, :2, 0] = 1
    events[0, :2, 2] = 1
    events[0, :2, 13:15] = torch.tensor([2.0, 1.0], device=device)
    counts = {}
    for variant in VARIANTS:
        model = ControlledModel(variant).to(device)
        model.eval()
        before = model(cgm, events)
        assert before.shape == (2,) and torch.isfinite(before).all()
        provenance = events.clone(); provenance[:, :, 15:17] = 500
        torch.testing.assert_close(before, model(cgm, provenance))
        short = model(cgm, events[:, :4])
        torch.testing.assert_close(before, short)  # Padding length invariance.
        empty = torch.zeros_like(events)
        torch.testing.assert_close(model(cgm, empty), model(cgm, empty[:, :1]))
        if variant in ("cgm-mlp", "cgm-gru-mask"):
            torch.testing.assert_close(before, model(cgm, empty))
        if variant in ("recording-gru", "type-timing-gru"):
            values = events.clone(); values[:, :, 13] = 1000
            torch.testing.assert_close(before, model(cgm, values))
        if variant == "no-age-gru":
            ages = events.clone(); ages[:, :, 12] = 0.8
            torch.testing.assert_close(before, model(cgm, ages))
        clone = ControlledModel(variant).to(device); clone.load_state_dict(model.state_dict())
        torch.testing.assert_close(before, clone(cgm, events))
        # cuDNN RNN modules require training mode for their backward pass.
        # Keep the behavioral checks above in eval mode, then switch explicitly
        # for the optimizer smoke test on GPU as well as CPU.
        model.train()
        optimizer = torch.optim.AdamW(model.parameters(), lr=2e-4, weight_decay=1e-4)
        training_logits = model(cgm, events)
        loss = nn.BCEWithLogitsLoss()(training_logits, torch.tensor([1.0, 0.0], device=device))
        loss.backward()
        assert any(parameter.grad is not None and torch.isfinite(parameter.grad).all() for parameter in model.parameters())
        optimizer.step()
        model.eval()
        assert torch.isfinite(model(cgm, events)).all()
        with tempfile.TemporaryDirectory(prefix="loop-model-smoke-") as directory:
            checkpoint = Path(directory) / "checkpoint.pt"
            torch.save({"model": model.state_dict(), "optimizer": optimizer.state_dict()}, checkpoint)
            saved = torch.load(checkpoint, map_location=device, weights_only=True)
            clone.load_state_dict(saved["model"])
            torch.testing.assert_close(model(cgm, events), clone(cgm, events))
            restored_optimizer = torch.optim.AdamW(clone.parameters(), lr=2e-4, weight_decay=1e-4)
            restored_optimizer.load_state_dict(saved["optimizer"])
        if str(device).startswith("cuda") and torch.cuda.device_count() > 1:
            parallel = nn.DataParallel(model)
            torch.testing.assert_close(model(cgm, events), parallel(cgm, events), rtol=1e-4, atol=1e-5)
        counts[variant] = sum(parameter.numel() for parameter in model.parameters())
    print(json.dumps({"model_preflight": "passed", "device": str(device), "parameters": counts}), flush=True)


def source_digest(code_directory):
    files = [*code_directory.joinpath("src").rglob("*.py"), *code_directory.joinpath("scripts").glob("*.py"), Path(__file__), Path(legacy.__file__)]
    digest = hashlib.sha256()
    for path in sorted(files, key=lambda path: str(path)):
        # Logical paths survive mounting the same package under another prefix.
        name = str(path.relative_to(code_directory)) if path.is_relative_to(code_directory) else path.name
        digest.update(name.encode() + b"\0" + path.read_bytes() + b"\0")
    return digest.hexdigest()


def verify_predictions(directory, patients, expected):
    from t1d_tkg.neural_contract import validate_prediction_row
    paths = {legacy.patient_filename("validation", patient): patient for patient in patients}
    if {path.name for path in directory.glob("*.jsonl.gz")} != set(paths):
        raise ValueError("prediction archive does not contain exactly the validation participant set")
    for name, patient in paths.items():
        count = positives = 0
        previous = None
        digest = hashlib.sha256()
        with gzip.open(directory / name, "rt", encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                previous = validate_prediction_row(row, patient, previous)
                digest.update(f"{previous.isoformat()}|{row['label']}\n".encode())
                count += 1; positives += row["label"]
        if {"records": count, "positive_labels": positives, "digest": digest.hexdigest()} != expected[patient]:
            raise ValueError("prediction timestamps/labels do not match the independently verified CGM cache")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--fixture-only", action="store_true", help="CPU integration check for tiny software fixtures only (<=1000 rows, <=30 participants); never a research run")
    parser.add_argument("--mode", choices=("preflight", "train", "evaluate"), default="preflight")
    parser.add_argument("--input-directory", type=Path)
    parser.add_argument("--code-directory", type=Path)
    parser.add_argument("--run-directory", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--variant", default="clean-gru", choices=("cgm-mlp", "cgm-gru-mask", "clean-gru", "recording-gru", "type-timing-gru", "no-age-gru"))
    parser.add_argument("--fold", default="outer-0")
    parser.add_argument("--seed", type=int, default=20261002)
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--hidden", type=int, default=64)
    parser.add_argument("--batch-size", type=int, default=4096)
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()
    if args.self_test:
        smoke_test(); return
    legacy.discover_paths(args)
    from t1d_tkg.manifest import load_manifest, manifest_checksum
    from t1d_tkg.metrics import METRIC_VERSION, average_precision
    from t1d_tkg.neural_contract import CONTRACT_VERSION, verify_inputs, membership_digest, checkpoint_contract, validate_checkpoint
    if args.hidden != 64 or min(args.epochs, args.batch_size, args.workers) < 1:
        raise ValueError("this comparison fixes hidden=64 and requires positive epochs/batch size/workers")
    manifest = load_manifest(args.input_directory / "loop_model_manifest.json")
    checksum = manifest_checksum(manifest)
    contract = json.loads((args.input_directory / "input_contract.json").read_text())
    if contract.get("manifest_sha256") != checksum or contract.get("max_events") != 64 or contract.get("history_minutes") != 120 or contract.get("contains_locked_holdout") is not False:
        raise ValueError("input contract is not the declared 64-event development-only contract")
    fold = next((item for item in manifest["folds"] if item["fold_id"] == args.fold), None)
    if fold is None:
        raise ValueError("unknown model fold")
    train, validation = set(fold["train_patients"]), set(fold["validation_patients"])
    cgm_meta, event_meta, cgm_paths, event_paths = legacy.load_staged_metadata(args.input_directory, checksum)
    window_hash = cgm_meta["window_verification"]["window_identity_sha256"]
    if contract.get("window_identity_sha256") != window_hash or event_meta.get("cgm_window_identity_sha256") != window_hash or contract.get("partitions") != cgm_meta["partitions"]:
        raise ValueError("cache identities or partition contract differ")
    print({"stage": "verify_input", "note": "streaming full content checks before GPU allocation"}, flush=True)
    content_hash, expected = verify_inputs(cgm_meta, event_meta, cgm_paths, event_paths, set(manifest["patients"]), progress=lambda item: print(item, flush=True))
    if sum(item["records"] for item in expected.values()) != cgm_meta["records"] or sum(item["positive_labels"] for item in expected.values()) != cgm_meta["positive_labels"]:
        raise ValueError("CGM aggregate metadata differs from verified content")
    if args.mode == "preflight":
        smoke_test()
        print({"input_preflight": "passed", "input_content_sha256": content_hash, "participants": len(expected)}, flush=True)
        return
    if args.run_directory is None or args.run_directory.exists():
        raise ValueError("choose a new --run-directory; completed outputs are never overwritten")
    if args.mode == "evaluate" and args.checkpoint is None:
        raise ValueError("evaluate requires a controlled-v1 checkpoint")
    if torch is None:
        raise RuntimeError("training/evaluation requires PyTorch")
    if args.fixture_only:
        if len(expected) > 30 or sum(item["records"] for item in expected.values()) > 1000:
            raise ValueError("CPU fixture mode refuses research-scale data")
    elif not torch.cuda.is_available():
        raise RuntimeError("training/evaluation requires the Kaggle CUDA runtime")
    smoke_test()
    if not args.fixture_only:
        smoke_test("cuda:0")
    optimizer_config = {"name": "AdamW", "learning_rate": 2e-4, "weight_decay": 1e-4, "loss": "BCEWithLogitsLoss", "positive_weight": 1.0}
    configuration = {"contract_version": CONTRACT_VERSION, "model": "controlled-neural", "fixture_only": args.fixture_only, "variant": args.variant, "fold": args.fold, "seed": args.seed, "hidden": args.hidden, "epochs": args.epochs, "batch_size": args.batch_size, "workers": args.workers, "max_events": 64, "manifest_sha256": checksum, "window_identity_sha256": window_hash, "input_content_sha256": content_hash, "training_membership_sha256": membership_digest(train), "optimizer": optimizer_config, "source_sha256": source_digest(args.code_directory), "event_input_policy": "occurrence-replay-no-export-provenance-v1", "evaluation_scope": "validation", "complete": False, "environment": {"python": platform.python_version(), "numpy": np.__version__, "torch": str(torch.__version__), "cuda": torch.version.cuda, "gpus": [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]}}
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    torch.backends.cudnn.deterministic = True; torch.backends.cudnn.benchmark = False
    device = torch.device("cpu" if args.fixture_only else "cuda:0")
    base = ControlledModel(args.variant, args.hidden).to(device)
    configuration["trainable_parameters"] = sum(parameter.numel() for parameter in base.parameters())
    configuration["mode"] = args.mode
    completed_epochs = args.epochs
    if args.mode == "evaluate":
        checkpoint = torch.load(args.checkpoint, map_location=device, weights_only=True)
        validate_checkpoint(checkpoint, configuration)
        base.load_state_dict(checkpoint["model"])
        completed_epochs = checkpoint["epoch"]
    args.run_directory.mkdir(parents=True)
    legacy.atomic_json(args.run_directory / "run.json", configuration)
    model = nn.DataParallel(base) if not args.fixture_only and torch.cuda.device_count() > 1 else base
    print({"stage": "ready", "variant": args.variant, "gpu_count": torch.cuda.device_count(), "parameters": configuration["trainable_parameters"]}, flush=True)
    cgm_only = args.variant in ("cgm-mlp", "cgm-gru-mask")
    if args.mode == "train":
        optimizer = torch.optim.AdamW(model.parameters(), lr=2e-4, weight_decay=1e-4)
        loss_fn = nn.BCEWithLogitsLoss()
        for epoch in range(args.epochs):
            model.train(); count = positive = 0
            for batch_number, (_, _, cgm, events, labels) in enumerate(legacy.batches(train, args.batch_size, args.workers, cgm_paths, event_paths, cgm_only=cgm_only), 1):
                optimizer.zero_grad(set_to_none=True)
                loss = loss_fn(model(torch.as_tensor(cgm, device=device), torch.as_tensor(events, device=device)), torch.as_tensor(labels, device=device))
                if not torch.isfinite(loss):
                    raise RuntimeError("nonfinite training loss")
                loss.backward(); optimizer.step(); count += len(labels); positive += int(labels.sum())
                if batch_number == 1 or batch_number % 100 == 0:
                    print({"stage": "train", "epoch": epoch + 1, "batches": batch_number, "windows": count, "loss": float(loss.detach())}, flush=True)
            if count != sum(expected[p]["records"] for p in train) or positive != sum(expected[p]["positive_labels"] for p in train):
                raise ValueError("training producer count differs from independently verified cache")
            path = args.run_directory / f"checkpoint-epoch-{epoch+1}.pt"
            temporary = path.with_suffix(".pt.tmp")
            torch.save({"contract": checkpoint_contract(configuration), "epoch": epoch+1, "model": base.state_dict(), "optimizer": optimizer.state_dict()}, temporary)
            temporary.replace(path)
            print({"stage": "checkpoint", "epoch": epoch+1, "windows": count}, flush=True)
    metrics = legacy.evaluate(model, validation, "validation", args, device, cgm_paths, event_paths, average_precision, cgm_only=cgm_only)
    verify_predictions(args.run_directory / "predictions", validation, expected)
    report = {**configuration, "complete": True, "epochs": completed_epochs, "metric_version": METRIC_VERSION, "groups": {"validation": metrics}, "prediction_identity_verified": True, "availability_policy": "retrospective occurrence-time replay; immediate availability assumed, not measured", "artifacts": str(args.run_directory)}
    legacy.atomic_json(args.run_directory / "result.json", report)
    legacy.atomic_json(args.run_directory / "run.json", report)
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
