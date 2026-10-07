"""Reproduce a declared sample of recovered predictions on CPU, without fitting."""
from __future__ import annotations
import argparse
import gzip
import hashlib
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "kaggle_event_sequence_gru"))
import train_gru_recovery as recovery
from run_loop_event_sequence_linear_pilot import sequence_partition
from t1d_tkg.manifest import load_manifest, manifest_checksum
from t1d_tkg.neural_contract import verify_content
from t1d_tkg.cache_io import logical_name
from t1d_tkg.feature_cache import CACHE_VERSION, FEATURE_NAMES
from t1d_tkg.event_cache import EVENT_CACHE_VERSION


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-directory", type=Path, required=True)
    parser.add_argument("--input-directory", type=Path, default=Path("private/kaggle_loop_sequence_input"))
    parser.add_argument("--participants", type=int, default=3)
    parser.add_argument("--windows-per-participant", type=int, default=64)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if min(args.participants, args.windows_per_participant) < 1 or args.output.exists():
        raise ValueError("choose positive sample sizes and a new output path")
    torch = recovery.torch
    if torch is None:
        raise RuntimeError("run with the isolated PyTorch interpreter")
    torch.set_num_threads(2)
    run = json.loads((args.run_directory / "run.json").read_text())
    manifest = load_manifest(args.input_directory / "loop_model_manifest.json")
    checksum = manifest_checksum(manifest)
    if not run.get("complete") or run.get("manifest_sha256") != checksum or run.get("fold") != "outer-0":
        raise ValueError("expected the completed matching outer-0 historical run")
    fold = next(item for item in manifest["folds"] if item["fold_id"] == run["fold"])
    validation = set(fold["validation_patients"])
    cgm_meta, event_meta, cgm_paths, event_paths = recovery.load_staged_metadata(args.input_directory, checksum)
    if run["window_identity_sha256"] != event_meta["cgm_window_identity_sha256"] or run["window_identity_sha256"] != cgm_meta["window_verification"]["window_identity_sha256"]:
        raise ValueError("historical run and cache identities differ")
    checkpoint_path = args.run_directory / f"checkpoint-epoch-{run['epochs']}.pt"
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    for key in ("seed", "hidden", "max_events", "manifest_sha256"):
        if checkpoint[key] != run[key]:
            raise ValueError("historical checkpoint and colocated run record differ")
    if checkpoint["epoch"] != run["epochs"]:
        raise ValueError("checkpoint is not the final completed epoch")
    model = recovery.SequenceGRU(run["hidden"])
    model.load_state_dict(checkpoint["model"], strict=True); model.eval()
    verified_files = set()
    events_by_name = {logical_name(item["file"]): item for item in event_meta["summaries"]}
    sample_count = 0; maximum_error = 0.0
    prediction_paths = sorted((args.run_directory / "predictions").glob("validation-*.jsonl.gz"))
    if len(prediction_paths) < args.participants:
        raise ValueError("not enough recovered prediction participants")
    for prediction_path in prediction_paths[:args.participants]:
        with gzip.open(prediction_path, "rt") as handle:
            rows = [json.loads(line) for line in itertools.islice(handle, args.windows_per_participant)]
        patient = rows[0]["patient_id"]
        if patient not in validation or any(row["patient_id"] != patient for row in rows):
            raise ValueError("sample participant is not in the historical validation group")
        partition = int.from_bytes(hashlib.blake2b(patient.encode(), digest_size=8).digest(), "big") % len(cgm_paths)
        cgm_path = cgm_paths[partition]
        events = [event_paths[modality][partition] for modality in recovery.MODALITIES]
        if cgm_path not in verified_files:
            verify_content(cgm_path, cgm_meta["partition_summaries"][partition], {"cache_version": CACHE_VERSION, "features": list(FEATURE_NAMES)})
            verified_files.add(cgm_path)
        for path, modality in zip(events, recovery.MODALITIES, strict=True):
            if path not in verified_files:
                verify_content(path, events_by_name[logical_name(path.name)], {"cache_version": EVENT_CACHE_VERSION, "modality": modality})
                verified_files.add(path)
        samples = list(itertools.islice(sequence_partition(cgm_path, events, 64, eligible_patients={patient}), len(rows)))
        if len(samples) != len(rows):
            raise ValueError("recovered prediction sample is not fully covered by the cache")
        for row, sample in zip(rows, samples, strict=True):
            if (sample[0], sample[1], sample[4]) != (patient, row["index_time"], row["label"]):
                raise ValueError("checkpoint replay does not match recovered window identities")
        with torch.no_grad():
            cgm = torch.tensor([sample[2] for sample in samples], dtype=torch.float32)
            events_tensor = torch.tensor([sample[3] for sample in samples], dtype=torch.float32).reshape(-1, 64, 17)
            scores = torch.sigmoid(model(cgm, events_tensor))
        recorded = torch.tensor([row["score"] for row in rows], dtype=torch.float32)
        torch.testing.assert_close(scores, recorded, rtol=1e-5, atol=1e-5)
        maximum_error = max(maximum_error, float((scores - recorded).abs().max()))
        sample_count += len(rows)
        print({"checkpoint_replay": "sample_passed", "participants_checked": sample_count // args.windows_per_participant, "windows_checked": sample_count}, flush=True)
    report = {"check": "historical-checkpoint-cpu-replay", "complete": True, "torch": str(torch.__version__), "participants_sampled": args.participants, "windows_sampled": sample_count, "sampling_policy": "first hashed prediction filenames; earliest windows in each", "absolute_tolerance": 1e-5, "relative_tolerance": 1e-5, "maximum_absolute_probability_error": maximum_error, "checkpoint_sha256": hashlib.sha256(checkpoint_path.read_bytes()).hexdigest(), "manifest_sha256": checksum, "window_identity_sha256": run["window_identity_sha256"], "input_partitions_content_verified": len(verified_files), "limitation": "sampled CPU replay, not full prediction replay or CUDA/multi-GPU validation", "identifiers_emitted": False}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
