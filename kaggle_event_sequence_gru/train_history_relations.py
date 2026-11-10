"""Matched temporal graph pilots and an event-to-time-bin sequence control.

The two variants consume identical CGM histories and individual event tokens.
They use the same three message MLPs and parameter count. The generic model
averages all three transforms for every edge; the typed model routes each edge
to the transform derived from the source event modality. This tests typed
message-passing inductive bias, not extra clinical information: relation IDs
are reconstructed from event modality and timestamp ordering.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np

import train_history_controlled as history

torch, nn = history.torch, history.nn
VARIANTS = ("graph-generic", "graph-typed", "graph-event-disabled",
            "graph-endpoint-shifted", "aligned-nongraph")
HISTORY_STEPS = 24
MAX_EVENTS = 64
EVENT_WIDTH = 17
HIDDEN = 64
EXPERT_WIDTH = 14
EDGE_WIDTH = HIDDEN * 2 + 1 + 3
EXPECTED_PARAMETER_COUNT = 36_883


def select_training_device(preference="auto"):
    """Select an explicitly available research device."""
    if torch is None:
        raise RuntimeError("PyTorch is required")
    if preference not in ("auto", "cuda", "mps", "cpu"):
        raise ValueError(f"unsupported research device: {preference}")
    if preference in ("auto", "cuda") and torch.cuda.is_available():
        return torch.device("cuda:0")
    mps = getattr(torch.backends, "mps", None)
    if preference in ("auto", "mps") and mps is not None and mps.is_available():
        return torch.device("mps")
    if preference == "cpu":
        return torch.device("cpu")
    if preference == "auto":
        raise RuntimeError("no CUDA or Apple MPS accelerator is available; choose --device cpu explicitly")
    raise RuntimeError(f"requested research device is unavailable: {preference}")


class TemporalRelationModel(nn.Module if nn is not None else object):
    """One event-to-observed-CGM edge per retained event and prediction window."""

    def __init__(self, variant: str):
        super().__init__()
        if variant not in VARIANTS:
            raise ValueError(f"unknown relation variant: {variant}")
        self.variant = variant
        # Construct layers shared by graph and aligned-control models first.
        # With the same seed this gives both variants identical initial CGM,
        # event, recurrent-readout, and prediction-head weights.
        self.cgm_encoder = nn.Linear(2, HIDDEN)
        self.event_encoder = nn.Linear(EVENT_WIDTH, HIDDEN)
        self.temporal_readout = nn.GRU(HIDDEN, HIDDEN, batch_first=True)
        self.head = nn.Sequential(nn.Linear(HIDDEN, 32), nn.ReLU(), nn.Linear(32, 1))
        # The parameter bank is identical for graph variants. The aligned
        # non-graph control replaces this 8,466-parameter bank with its own
        # 8,466-parameter time-bin fusion and gating modules.
        if variant != "aligned-nongraph":
            self.edge_experts = nn.ModuleList([
                nn.Sequential(nn.Linear(EDGE_WIDTH, EXPERT_WIDTH), nn.ReLU(),
                              nn.Linear(EXPERT_WIDTH, HIDDEN))
                for _ in range(3)
            ])
        if variant == "aligned-nongraph":
            # The control uses the exact same inputs and causal event-to-slot
            # assignment as the graph, but directly pools event embeddings in
            # each time bin. It has no event-conditioned CGM message function.
            self.aligned_fusion = nn.Linear(HIDDEN * 2 + 1, HIDDEN)
            self.aligned_branch_gates = nn.Linear(HIDDEN, 2)
            self.aligned_event_channel_gates = nn.Parameter(torch.zeros(16))

    def forward(self, history_input, event_input):
        if history_input.ndim != 3 or history_input.shape[1:] != (HISTORY_STEPS, 2):
            raise ValueError("history input must have shape [batch,24,2]")
        if event_input.ndim != 3 or event_input.shape[1:] != (MAX_EVENTS, EVENT_WIDTH):
            raise ValueError("event input must have shape [batch,64,17]")

        history_mask = history_input[:, :, 1]
        cgm_features = torch.stack((history_input[:, :, 0] / 100.0, history_mask), dim=2)
        cgm_nodes = torch.tanh(self.cgm_encoder(cgm_features))

        events = event_input.clone()
        if self.variant == "graph-event-disabled":
            # Keep the exact module/parameter layout while removing every
            # captured-event feature and therefore every event-to-CGM edge.
            events.zero_()
        events[:, :, 15:17] = 0.0  # Exclude export-derived duplicate/provenance fields.
        value_scale = (10.0 * events[:, :, 1] + 25.0 * events[:, :, 2]
                       + 150.0 * events[:, :, 3]).clamp_min(1.0)
        events[:, :, 13] = events[:, :, 13] / value_scale
        active = events[:, :, 0] > 0.5
        modality = events[:, :, 1:4]
        relation_id = modality.argmax(dim=2)
        event_age = events[:, :, 12]
        cgm_age = torch.arange(HISTORY_STEPS - 1, -1, -1,
                               dtype=history_input.dtype,
                               device=history_input.device) / 24.0

        # Select the nearest observed CGM grid point at or after the event.
        # Age decreases toward the prediction time; future edges are forbidden.
        delta = event_age.unsqueeze(2) - cgm_age.view(1, 1, -1)
        eligible = (history_mask.unsqueeze(1) > 0.5) & (delta >= -1e-7)
        distances = torch.where(eligible, delta.clamp_min(0.0),
                                torch.full_like(delta, float("inf")))
        nearest_slot = distances.argmin(dim=2)
        if self.variant == "aligned-nongraph":
            # Pool individual event encodings into the same nearest-later
            # observed CGM bins. This preserves timing and event inputs while
            # removing event-to-CGM edge message passing.
            event_nodes = self.event_encoder(events)
            channel_gain = 1.0 + 0.1 * torch.tanh(self.aligned_event_channel_gates)
            event_nodes = torch.cat((
                event_nodes[:, :, :16] * channel_gain.view(1, 1, 16),
                event_nodes[:, :, 16:]), dim=2)
            event_nodes = event_nodes * active.unsqueeze(2).to(event_nodes.dtype)
            aligned = torch.zeros_like(cgm_nodes)
            aligned.scatter_add_(
                1, nearest_slot.unsqueeze(2).expand(-1, -1, HIDDEN), event_nodes)
            counts = torch.zeros(
                history_input.shape[0], HISTORY_STEPS, 1,
                dtype=history_input.dtype, device=history_input.device)
            counts.scatter_add_(
                1, nearest_slot.unsqueeze(2), active.unsqueeze(2).to(history_input.dtype))
            aligned = aligned / counts.clamp_min(1.0).sqrt()
            # Normalize count so its scale is stable across the event cap.
            count_feature = counts / float(MAX_EVENTS) ** 0.5
            fused = torch.tanh(self.aligned_fusion(
                torch.cat((cgm_nodes, aligned, count_feature), dim=2)))
            gates = torch.sigmoid(self.aligned_branch_gates(fused))
            fused_nodes = torch.tanh(
                gates[:, :, 0:1] * cgm_nodes
                + gates[:, :, 1:2] * aligned + fused)
            _, state = self.temporal_readout(fused_nodes)
            return self.head(state[-1]).squeeze(1)
        if self.variant == "graph-endpoint-shifted":
            # Causal endpoint perturbation: use the second-nearest observed
            # later CGM point when available; fall back to nearest otherwise.
            shifted_distances = distances.scatter(
                2, nearest_slot.unsqueeze(2), float("inf"))
            second_slot = shifted_distances.argmin(dim=2)
            has_second = eligible.sum(dim=2) > 1
            target_slot = torch.where(has_second, second_slot, nearest_slot)
        else:
            target_slot = nearest_slot
        chosen_cgm = cgm_nodes.gather(
            1, target_slot.unsqueeze(2).expand(-1, -1, HIDDEN))
        chosen_age = cgm_age[target_slot]
        elapsed = (event_age - chosen_age).clamp_min(0.0).unsqueeze(2)
        edge_input = torch.cat((self.event_encoder(events), chosen_cgm,
                                elapsed, modality), dim=2)

        # Both models have the same expert bank, input features and edge set.
        all_messages = torch.stack(
            [expert(edge_input) for expert in self.edge_experts], dim=2)
        if self.variant == "graph-typed":
            messages = all_messages.gather(
                2, relation_id[:, :, None, None].expand(-1, -1, 1, HIDDEN)
            ).squeeze(2)
        else:
            # A single generic edge operation is shared across every edge.
            messages = all_messages.mean(dim=2)
        messages = messages * active.unsqueeze(2).to(messages.dtype)

        aggregated = torch.zeros_like(cgm_nodes)
        aggregated.scatter_add_(
            1, target_slot.unsqueeze(2).expand(-1, -1, HIDDEN), messages)
        edge_counts = torch.zeros(
            history_input.shape[0], HISTORY_STEPS, 1,
            dtype=history_input.dtype, device=history_input.device)
        edge_counts.scatter_add_(
            1, target_slot.unsqueeze(2), active.unsqueeze(2).to(history_input.dtype))
        # sqrt normalization retains event multiplicity while controlling scale.
        fused_nodes = torch.tanh(cgm_nodes + aggregated / edge_counts.clamp_min(1).sqrt())
        _, state = self.temporal_readout(fused_nodes)
        return self.head(state[-1]).squeeze(1)


def parameter_count(model) -> int:
    return sum(parameter.numel() for parameter in model.parameters())


def run_configuration(*, args, data, model_params, train_count,
                      train_positives, metric_version, source_hash,
                      environment):
    """Build the immutable run/checkpoint contract from one resolved fit."""
    return {
        "contract_version": "loop-full-history-temporal-relations-v1",
        "model": ("time-aligned-nongraph-event-sequence-control"
                  if args.variant == "aligned-nongraph"
                  else "matched-temporal-event-graph"),
        "mode": "train", "fixture_only": False,
        "variant": args.variant, "fold": args.fold, "seed": args.seed,
        "hidden": HIDDEN, "epochs": args.epochs,
        "batch_size": args.batch_size, "workers": args.workers,
        "history_steps": HISTORY_STEPS, "max_events": MAX_EVENTS,
        "relation_types": (None if args.variant == "aligned-nongraph"
                           else ["prior_basal", "prior_bolus", "prior_food"]),
        "relation_id_source": (
            "event modality features retained; event timestamps map to nearest observed later CGM bins; no relation labels"
            if args.variant == "aligned-nongraph"
            else "event features are zeroed before graph construction"
            if args.variant == "graph-event-disabled"
            else "event modality one-hot; deterministic endpoint-derived label"
        ),
        "event_input_policy": (
            "all event features zeroed before graph construction"
            if args.variant == "graph-event-disabled" else "captured event features retained"
        ),
        "edge_policy": (
            "no graph edges; event tokens pooled into the nearest observed later CGM bin"
            if args.variant == "aligned-nongraph"
            else "disabled; no event-to-CGM edges are constructed"
            if args.variant == "graph-event-disabled"
            else "second-nearest observed later CGM grid point when available; otherwise nearest; no future edges"
            if args.variant == "graph-endpoint-shifted"
            else "each event to nearest observed later CGM grid point; no future edges"
        ),
        "generic_edge_policy": "mean of the shared three-expert bank for every edge",
        "typed_edge_policy": "expert selected by event-derived relation id",
        "model_architecture": (
            "event-only token encoding, nearest-later observed CGM-bin aggregation, gated concatenation, temporal GRU"
            if args.variant == "aligned-nongraph"
            else "event-CGM edge messages, per-slot aggregation, temporal GRU"
        ),
        "trainable_parameters": model_params,
        "parameter_match": ("exactly 36,883 trainable parameters; event-only time-bin pooling control"
                            if args.variant == "aligned-nongraph"
                            else "all graph variants have identical module layout and parameter count"),
        "manifest_sha256": data["manifest_sha256"],
        "window_identity_sha256": data["window_identity_sha256"],
        "input_content_sha256": data["content_sha256"],
        "training_membership_sha256": data["membership_digest"](data["train"]),
        "optimizer": {"name": "AdamW", "learning_rate": 2e-4,
                      "weight_decay": 1e-4, "loss": "BCEWithLogitsLoss"},
        "source_sha256": source_hash,
        "evaluation_scope": "outer-fold validation; development only",
        "locked_holdout_used": False,
        "availability_policy": "retrospective occurrence time; immediate availability assumed, not measured",
        "metric_version": metric_version,
        "train_windows_expected": train_count,
        "train_positive_labels_expected": train_positives,
        "environment": environment,
        "complete": False,
    }


def source_digest(code_directory: Path) -> str:
    root = Path(code_directory).resolve()
    digest = hashlib.sha256(history.source_digest(root).encode())
    digest.update(Path(__file__).read_bytes())
    return digest.hexdigest()


def smoke_test(device="cpu"):
    if torch is None:
        raise RuntimeError("PyTorch is required for the temporal-relation model")
    torch.manual_seed(20261017)
    batch = 3
    x = torch.zeros(batch, HISTORY_STEPS, 2, device=device)
    x[:, :, 0] = 120.0
    x[:, :, 1] = 1.0
    x[1, 5, 1] = 0.0
    e = torch.zeros(batch, MAX_EVENTS, EVENT_WIDTH, device=device)
    e[0, 0, 0] = 1.0
    e[0, 0, 2] = 1.0  # bolus edge
    e[0, 0, 12] = 0.5
    e[0, 1, 0] = 1.0
    e[0, 1, 3] = 1.0  # food edge
    e[0, 1, 12] = 0.0
    e[1, 0, 0] = 1.0
    e[1, 0, 1] = 1.0  # basal edge
    e[1, 0, 12] = 0.99
    counts = {}
    initial_state = None
    shared_state = None
    shared_prefixes = ("cgm_encoder.", "event_encoder.",
                       "temporal_readout.", "head.")
    for variant in VARIANTS:
        torch.manual_seed(20261017)
        model = TemporalRelationModel(variant).to(device)
        state = model.state_dict()
        if initial_state is None:
            initial_state = {name: tensor.detach().clone() for name, tensor in state.items()}
        elif variant == "graph-typed" and any(
                not torch.equal(initial_state[name], tensor)
                for name, tensor in state.items()):
            raise RuntimeError("generic and typed models do not start from identical weights")
        if variant == "graph-generic":
            shared_state = {name: tensor.detach().clone() for name, tensor in state.items()
                            if name.startswith(shared_prefixes)}
        elif variant == "aligned-nongraph":
            aligned_shared = {name: tensor for name, tensor in state.items()
                              if name.startswith(shared_prefixes)}
            if (set(aligned_shared) != set(shared_state)
                    or any(not torch.equal(shared_state[name], aligned_shared[name])
                           for name in shared_state)):
                raise RuntimeError("graph and aligned control shared layers have different initialization")
        scores = model(x, e)
        if scores.shape != (batch,) or not torch.isfinite(scores).all():
            raise RuntimeError(f"{variant} forward smoke test failed")
        loss = nn.BCEWithLogitsLoss()(scores, torch.tensor([1.0, 0.0, 1.0], device=device))
        loss.backward()
        if not all(torch.isfinite(p.grad).all() for p in model.parameters() if p.grad is not None):
            raise RuntimeError(f"{variant} produced nonfinite gradients")
        if str(device).startswith("cuda") and torch.cuda.device_count() > 1:
            parallel = nn.DataParallel(TemporalRelationModel(variant).to(device))
            parallel_output = parallel(x, e)
            if parallel_output.shape != (batch,) or not torch.isfinite(parallel_output).all():
                raise RuntimeError(f"{variant} multi-GPU forward smoke test failed")
            parallel_loss = nn.BCEWithLogitsLoss()(
                parallel_output, torch.tensor([1.0, 0.0, 1.0], device=device))
            parallel_loss.backward()
        counts[variant] = parameter_count(model)
    if len(set(counts.values())) != 1:
        raise RuntimeError(f"graph variant parameter budgets differ: {counts}")
    if counts["graph-typed"] != EXPECTED_PARAMETER_COUNT:
        raise RuntimeError(f"unexpected graph parameter count: {counts}")
    disabled = TemporalRelationModel("graph-event-disabled").to(device)
    with torch.no_grad():
        original_events = torch.rand(batch, MAX_EVENTS, EVENT_WIDTH, device=device)
        zero_events = torch.zeros_like(original_events)
        zeroed_a = disabled(x, original_events)
        zeroed_b = disabled(x, zero_events)
    if not torch.equal(zeroed_a, zeroed_b):
        raise RuntimeError("event-disabled variant depends on event inputs")
    print({"temporal_relation_model_preflight": "passed", "device": str(device),
           "trainable_parameters": counts, "relation_id_source": "event modality",
           "graph_aligned_shared_initialization": "identical",
           "event_disabled_input_invariance": "passed",
           "future_edges": "forbidden"}, flush=True)


def verified_inputs(input_dir: Path, code_dir: Path, fold_id: str,
                    receipt_path: Path | None, receipt_output: Path | None):
    code_dir = Path(code_dir).resolve()
    sys.path.insert(0, str(code_dir / "src"))
    sys.path.insert(0, str(code_dir / "scripts"))
    from t1d_tkg.cache_io import discover_cache_files
    from t1d_tkg.cgm_history_contract import verify_history_cache
    from t1d_tkg.manifest import load_manifest, manifest_checksum
    from t1d_tkg.neural_contract import (checkpoint_contract, membership_digest,
                                          object_digest, verify_inputs)

    input_dir = Path(input_dir).resolve()
    manifest = load_manifest(input_dir / "loop_model_manifest.json")
    manifest_sha = manifest_checksum(manifest)
    contract = json.loads((input_dir / "input_contract.json").read_text())
    if (contract.get("input_contract_version") != "loop-full-history-input-v1"
            or contract.get("manifest_sha256") != manifest_sha
            or contract.get("max_events") != 64
            or contract.get("history_minutes") != 120
            or contract.get("contains_locked_holdout") is not False):
        raise ValueError("input is not the validated development-only full-history contract")
    fold = next((item for item in manifest["folds"] if item["fold_id"] == fold_id), None)
    if fold is None:
        raise ValueError(f"unknown fold {fold_id}")
    train, validation = set(fold["train_patients"]), set(fold["validation_patients"])
    if train & validation:
        raise ValueError("fold has overlapping train and validation participants")
    checksum = manifest_sha
    cgm_meta, event_meta, feature_paths, event_paths = history.legacy.load_staged_metadata(
        input_dir, checksum)
    window_hash = cgm_meta["window_verification"]["window_identity_sha256"]
    if (contract.get("window_identity_sha256") != window_hash
            or event_meta.get("cgm_window_identity_sha256") != window_hash):
        raise ValueError("input caches do not share the frozen window identity")
    history_dir = input_dir / "loop_cgm_history_cache"
    history_paths = discover_cache_files(history_dir, "history-*.tsv*")
    if receipt_path is not None and Path(receipt_path).is_file():
        print({"stage": "verify_preflight_receipt", "path": str(receipt_path)}, flush=True)
        receipt = json.loads(Path(receipt_path).read_text())
        if (receipt.get("receipt_version") != "loop-full-history-preflight-receipt-v1"
                or receipt.get("manifest_sha256") != checksum
                or receipt.get("window_identity_sha256") != window_hash
                or receipt.get("fold") != fold_id
                or receipt.get("input_stat_sha256") != history.input_stat_digest(input_dir)):
            raise ValueError("preflight receipt does not match this exact input and fold")
        expected = receipt.get("expected", {})
        if set(expected) != set(manifest["patients"]):
            raise ValueError("preflight receipt does not cover exactly development participants")
        content_hash = receipt["input_content_sha256"]
        if object_digest({"history": receipt["history_content_sha256"],
                          "prior": receipt["prior_content_sha256"]}) != content_hash:
            raise ValueError("preflight receipt content digest is invalid")
        history_hash = receipt["history_content_sha256"]
        prior_hash = receipt["prior_content_sha256"]
    else:
        print({"stage": "verify_full_history_cache",
               "participants": len(manifest["patients"])}, flush=True)
        history_hash, expected = verify_history_cache(
            history_dir, input_dir / "loop_cgm_feature_cache",
            manifest_sha256=checksum, patients=set(manifest["patients"]),
            window_identity_sha256=window_hash)
        if (contract.get("cgm_history_input_content_sha256") != history_hash
                or len(history_paths) != cgm_meta["partitions"]):
            raise ValueError("history cache differs from its staged input contract")
        print({"stage": "verify_frozen_cgm_and_event_caches"}, flush=True)
        prior_hash, prior_expected = verify_inputs(
            cgm_meta, event_meta, feature_paths, event_paths, set(manifest["patients"]),
            progress=lambda item: print(item, flush=True))
        if prior_expected != expected:
            raise ValueError("history and event/CGM inputs have different window identities")
        content_hash = object_digest({"history": history_hash, "prior": prior_hash})
        if receipt_output is not None:
            receipt_output = Path(receipt_output)
            receipt_output.parent.mkdir(parents=True, exist_ok=True)
            receipt = {
                "receipt_version": "loop-full-history-preflight-receipt-v1",
                "manifest_sha256": checksum,
                "window_identity_sha256": window_hash,
                "fold": fold_id,
                "history_content_sha256": history_hash,
                "prior_content_sha256": prior_hash,
                "input_content_sha256": content_hash,
                "input_stat_sha256": history.input_stat_digest(input_dir),
                "expected": expected,
            }
            history.legacy.atomic_json(receipt_output, receipt)
            print({"stage": "preflight_receipt_written", "path": str(receipt_output),
                   "participants": len(expected)}, flush=True)
    return {
        "manifest": manifest, "manifest_sha256": checksum,
        "window_identity_sha256": window_hash, "input_contract": contract,
        "content_sha256": content_hash, "expected": expected,
        "train": train, "validation": validation,
        "history_paths": history_paths, "feature_paths": feature_paths,
        "event_paths": event_paths, "checkpoint_contract": checkpoint_contract,
        "membership_digest": membership_digest,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--input-directory", type=Path)
    parser.add_argument("--code-directory", type=Path)
    parser.add_argument("--run-directory", type=Path)
    parser.add_argument("--preflight-receipt", type=Path)
    parser.add_argument("--receipt-output", type=Path,
                        help="write a reusable verified-input receipt if a full preflight is needed")
    parser.add_argument("--variant", choices=VARIANTS, default="graph-generic")
    parser.add_argument("--fold", default="outer-0")
    parser.add_argument("--seed", type=int, default=20261003)
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=4096)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--device", choices=("auto", "cuda", "mps", "cpu"), default="auto",
                        help="auto prefers CUDA then Apple MPS")
    args = parser.parse_args()
    if args.self_test:
        smoke_test("cpu")
        return
    if args.input_directory is None or args.code_directory is None or args.run_directory is None:
        raise ValueError("input, code and new run directories are required")
    if min(args.epochs, args.batch_size, args.workers) < 1:
        raise ValueError("epochs, batch-size and workers must be positive")
    run_dir = Path(args.run_directory)
    if run_dir.exists():
        raise FileExistsError(f"Refusing to overwrite completed or partial run: {run_dir}")
    if torch is None:
        raise RuntimeError("PyTorch is required")
    data = verified_inputs(args.input_directory, args.code_directory, args.fold,
                           args.preflight_receipt, args.receipt_output)
    from t1d_tkg.metrics import METRIC_VERSION, average_precision
    smoke_test()
    device = select_training_device(args.device)
    smoke_test(device)

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    if device.type == "cuda":
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    model = TemporalRelationModel(args.variant).to(device)
    model_params = parameter_count(model)
    if model_params != EXPECTED_PARAMETER_COUNT:
        raise RuntimeError(f"model parameter contract changed: {model_params}")
    train_count = sum(data["expected"][patient]["records"] for patient in data["train"])
    train_positives = sum(data["expected"][patient]["positive_labels"] for patient in data["train"])
    run_dir.mkdir(parents=True)
    configuration = run_configuration(
        args=args, data=data, model_params=model_params,
        train_count=train_count, train_positives=train_positives,
        metric_version=METRIC_VERSION,
        source_hash=source_digest(args.code_directory),
        environment={"python": platform.python_version(), "numpy": np.__version__,
                     "torch": str(torch.__version__), "cuda": torch.version.cuda,
                     "device": str(device),
                     "gpus": ([torch.cuda.get_device_name(i)
                               for i in range(torch.cuda.device_count())]
                              if device.type == "cuda" else [])},
    )
    history.legacy.atomic_json(run_dir / "run.json", configuration)
    parallel = nn.DataParallel(model) if device.type == "cuda" and torch.cuda.device_count() > 1 else model
    optimizer = torch.optim.AdamW(parallel.parameters(), lr=2e-4, weight_decay=1e-4)
    loss_fn = nn.BCEWithLogitsLoss()
    train_windows = train_positives_seen = 0
    train_log = []
    for epoch in range(args.epochs):
        parallel.train()
        seen = positives = 0
        weighted_loss = 0.0
        for batch_num, (_, _, x, e, y) in enumerate(history.batches(
            data["train"], args.batch_size, args.workers,
            data["history_paths"], data["feature_paths"], data["event_paths"],
            include_events=True), start=1):
            optimizer.zero_grad(set_to_none=True)
            logits = parallel(torch.as_tensor(x, dtype=torch.float32, device=device),
                              torch.as_tensor(e, dtype=torch.float32, device=device))
            loss = loss_fn(logits, torch.as_tensor(y, dtype=torch.float32, device=device))
            if not torch.isfinite(loss):
                raise RuntimeError("nonfinite training loss")
            loss.backward()
            optimizer.step()
            seen += len(y)
            positives += int(np.asarray(y).sum())
            weighted_loss += float(loss.detach()) * len(y)
            if batch_num == 1 or batch_num % 100 == 0:
                record = {"stage": "train", "variant": args.variant,
                          "fold": args.fold, "seed": args.seed,
                          "epoch": epoch + 1, "batches": batch_num,
                          "windows": seen, "loss": float(loss.detach())}
                print(record, flush=True)
        if seen != train_count or positives != train_positives:
            raise ValueError(f"training count mismatch: {seen}/{train_count} windows, "
                             f"{positives}/{train_positives} positives")
        train_windows += seen
        train_positives_seen += positives
        train_log.append({"epoch": epoch + 1, "windows": seen,
                          "positive_labels": positives,
                          "mean_batch_loss_weighted_by_windows": weighted_loss / seen})
        checkpoint = run_dir / f"checkpoint-epoch-{epoch + 1}.pt"
        temporary = checkpoint.with_suffix(".pt.tmp")
        torch.save({"contract": data["checkpoint_contract"](configuration),
                    "epoch": epoch + 1, "model": model.state_dict(),
                    "optimizer": optimizer.state_dict()}, temporary)
        temporary.replace(checkpoint)
        print({"stage": "checkpoint", "epoch": epoch + 1,
               "path": str(checkpoint)}, flush=True)

    metrics = history.evaluate(parallel, data["validation"],
        argparse.Namespace(run_directory=run_dir, batch_size=args.batch_size,
                           workers=args.workers), device,
        data["history_paths"], data["feature_paths"], data["event_paths"],
        average_precision, include_events=True)
    history.prior.verify_predictions(
        run_dir / "predictions", data["validation"], data["expected"])
    result = {**configuration, "complete": True, "groups": {"validation": metrics},
              "prediction_identity_verified": True,
              "training_windows_total": train_windows,
              "training_positive_labels_total": train_positives_seen,
              "training_log": train_log, "artifacts": str(run_dir)}
    history.legacy.atomic_json(run_dir / "run.json", result)
    history.legacy.atomic_json(run_dir / "result.json", result)
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()

