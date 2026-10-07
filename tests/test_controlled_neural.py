import gzip
import importlib.util
import json
import sys
import os
import subprocess
import ast
import base64
import hashlib
import io
import zipfile
from pathlib import Path

import pytest

from t1d_tkg.event_cache import EVENT_CACHE_VERSION, write_partition as write_events
from t1d_tkg.feature_cache import CACHE_VERSION, FEATURE_NAMES, write_partition as write_cgm
from t1d_tkg.neural_contract import checkpoint_contract, validate_checkpoint, verify_inputs, validate_prediction_row
from t1d_tkg.source_inventory import require_source_inventory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "kaggle_event_sequence_gru"))
import train_gru_recovery as recovery


def staged(tmp_path, expanded=False):
    cgm = tmp_path / "loop_cgm_feature_cache"; cgm.mkdir()
    event = tmp_path / "loop_event_instance_cache"; event.mkdir()
    row = ("p", "2026-01-01T12:00:00+00:00", 1, 90, -2)
    cgm_summary = write_cgm(cgm / "features-00.tsv.gz", [row])
    event_summaries = [write_events(event / f"events-{modality}-00.jsonl.gz", modality, []) for modality in recovery.MODALITIES]
    cgm_meta = {"cache_version": CACHE_VERSION, "manifest_sha256": "m", "partitions": 1, "partition_summaries": [cgm_summary]}
    event_meta = {"cache_version": EVENT_CACHE_VERSION, "manifest_sha256": "m", "files": [item["file"] for item in event_summaries], "summaries": event_summaries}
    (cgm / "metadata.json").write_text(json.dumps(cgm_meta))
    (event / "metadata.json").write_text(json.dumps(event_meta))
    if expanded:
        for directory in (cgm, event):
            for path in directory.glob("*.gz"):
                path.with_suffix("").write_bytes(gzip.decompress(path.read_bytes())); path.unlink()
    return recovery.load_staged_metadata(tmp_path, "m")


@pytest.mark.parametrize("expanded", [False, True])
def test_staging_names_and_full_content_check(tmp_path, expanded):
    cgm, event, cgm_paths, event_paths = staged(tmp_path, expanded)
    digest, identities = verify_inputs(cgm, event, cgm_paths, event_paths, {"p"})
    assert len(digest) == 64 and identities["p"]["records"] == 1
    assert identities["p"]["positive_labels"] == 1


def test_expansion_preserves_verified_input_identity(tmp_path):
    compressed = tmp_path / "compressed"; compressed.mkdir()
    plain = tmp_path / "plain"; plain.mkdir()
    def digest(path, expanded):
        return verify_inputs(*staged(path, expanded), {"p"})
    assert digest(compressed, False) == digest(plain, True)


def test_duplicate_compressed_and_expanded_partition_is_rejected(tmp_path):
    staged(tmp_path)
    path = tmp_path / "loop_cgm_feature_cache/features-00.tsv.gz"
    path.with_suffix("").write_bytes(gzip.decompress(path.read_bytes()))
    with pytest.raises(ValueError, match="duplicate logical"):
        recovery.load_staged_metadata(tmp_path, "m")


def test_missing_and_misaligned_partition_rejected(tmp_path):
    staged(tmp_path)
    path = tmp_path / "loop_event_instance_cache/events-food-00.jsonl.gz"
    path.rename(path.with_name("events-food-01.jsonl.gz"))
    with pytest.raises(ValueError, match="metadata"):
        recovery.load_staged_metadata(tmp_path, "m")
    path.with_name("events-food-01.jsonl.gz").unlink()
    with pytest.raises(RuntimeError, match="partition"):
        recovery.load_staged_metadata(tmp_path, "m")


def test_corrupt_records_and_header_rejected(tmp_path):
    cgm, event, paths, events = staged(tmp_path, True)
    original = paths[0].read_text()
    paths[0].write_text(original.replace("90.0", "91.0"))
    with pytest.raises(ValueError, match="digest mismatch"):
        verify_inputs(cgm, event, paths, events, {"p"})
    paths[0].write_text(original.replace(CACHE_VERSION, "wrong-version"))
    with pytest.raises(ValueError, match="header mismatch"):
        verify_inputs(cgm, event, paths, events, {"p"})


def test_non_development_participant_rejected(tmp_path):
    with pytest.raises(ValueError, match="outside development"):
        verify_inputs(*staged(tmp_path), {"different-person"})


def configuration():
    return dict(contract_version="v1", fixture_only=False, variant="clean-gru", fold="outer-0", seed=1, hidden=64, epochs=2, batch_size=4096, workers=3, max_events=64, manifest_sha256="m", window_identity_sha256="w", input_content_sha256="c", training_membership_sha256="t", optimizer={"name": "AdamW"}, source_sha256="s")


@pytest.mark.parametrize("field", ["fold", "training_membership_sha256", "window_identity_sha256", "input_content_sha256", "variant", "source_sha256", "seed", "batch_size", "workers"])
def test_checkpoint_rejects_mismatched_training_contract(field):
    config = configuration()
    checkpoint = {"contract": checkpoint_contract(config), "epoch": 2}
    validate_checkpoint(checkpoint, config)
    config[field] = "different"
    with pytest.raises(ValueError, match="checkpoint contract mismatch"):
        validate_checkpoint(checkpoint, config)


def test_legacy_checkpoint_is_not_a_controlled_checkpoint():
    with pytest.raises(ValueError, match="checkpoint contract mismatch"):
        validate_checkpoint({"manifest_sha256": "m", "hidden": 64, "epoch": 2}, configuration())


@pytest.mark.parametrize("score", [float("nan"), float("inf"), -0.1, 1.1])
def test_invalid_prediction_scores_rejected(score):
    with pytest.raises(ValueError, match="score"):
        validate_prediction_row({"patient_id": "p", "label": 1, "score": score, "index_time": "2026-01-01T12:00:00+00:00"}, "p", None)


def test_incomplete_loop_source_inventory_rejected_before_build(tmp_path):
    paths = {"basal": [tmp_path / "LOOPDeviceBasal3.txt"], "bolus": [tmp_path / "LOOPDeviceBolus.txt"], "food": [tmp_path / "LOOPDeviceFood.txt"]}
    with pytest.raises(ValueError, match="basal source inventory"):
        require_source_inventory(tmp_path, paths)


@pytest.mark.skipif(importlib.util.find_spec("torch") is None, reason="PyTorch is not installed in the default local interpreter; mandatory Kaggle CPU preflight executes this")
def test_actual_torch_models_forward_backward_padding_and_reload():
    from train_controlled import smoke_test
    smoke_test()


@pytest.mark.skipif(importlib.util.find_spec("torch") is None, reason="requires the isolated PyTorch environment")
@pytest.mark.parametrize("variant,expanded", [("cgm-mlp", False), ("clean-gru", True)])
def test_fixture_training_prediction_verification_and_checkpoint_recovery(tmp_path, variant, expanded):
    from t1d_tkg.manifest import build_hashed_kfold_manifest, save_manifest, manifest_checksum
    patients = [f"p{index:02d}" for index in range(30)]
    manifest = build_hashed_kfold_manifest(patients, folds=3)
    checksum = manifest_checksum(manifest)
    inputs = tmp_path / "input"; inputs.mkdir()
    save_manifest(inputs / "loop_model_manifest.json", manifest)
    cgm_dir = inputs / "loop_cgm_feature_cache"; cgm_dir.mkdir()
    event_dir = inputs / "loop_event_instance_cache"; event_dir.mkdir()
    summary = write_cgm(cgm_dir / "features-00.tsv.gz", [(p, "2026-01-01T12:00:00+00:00", 1, 95, -1) for p in patients])
    cgm_meta = {"cache_version": CACHE_VERSION, "manifest_sha256": checksum, "partitions": 1, "partition_summaries": [summary], "records": 30, "positive_labels": 30, "window_verification": {"window_identity_sha256": "fixture"}}
    event_summaries = []
    for modality in recovery.MODALITIES:
        records = [{"patient_id": p, "occurrence_time": "2026-01-01T11:30:00+00:00", "modality": modality, "subtype": "fixture", "model_value": 1.0, "model_value_known": True, "exact_duplicate_count": 2, "same_time_variant_count": 3} for p in patients]
        event_summaries.append(write_events(event_dir / f"events-{modality}-00.jsonl.gz", modality, records))
    event_meta = {"cache_version": EVENT_CACHE_VERSION, "manifest_sha256": checksum, "partitions": 1, "files": [item["file"] for item in event_summaries], "summaries": event_summaries, "cgm_window_identity_sha256": "fixture"}
    (cgm_dir / "metadata.json").write_text(json.dumps(cgm_meta))
    (event_dir / "metadata.json").write_text(json.dumps(event_meta))
    (inputs / "input_contract.json").write_text(json.dumps(dict(manifest_sha256=checksum, max_events=64, history_minutes=120, contains_locked_holdout=False, window_identity_sha256="fixture", partitions=1)))
    if expanded:
        for directory in (cgm_dir, event_dir):
            for path in directory.glob("*.gz"):
                path.with_suffix("").write_bytes(gzip.decompress(path.read_bytes())); path.unlink()
    common = [sys.executable, str(ROOT / "kaggle_event_sequence_gru/train_controlled.py"), "--fixture-only", "--input-directory", str(inputs), "--code-directory", str(ROOT), "--variant", variant, "--workers", "2", "--batch-size", "8"]
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src") + os.pathsep + str(ROOT / "scripts")}
    run = tmp_path / "run"
    trained = subprocess.run([*common, "--mode", "train", "--run-directory", str(run)], env=env, capture_output=True, text=True, timeout=90)
    assert trained.returncode == 0, trained.stdout + trained.stderr
    result = json.loads((run / "result.json").read_text())
    assert result["complete"] and result["prediction_identity_verified"] and result["fixture_only"]
    checkpoint = run / "checkpoint-epoch-2.pt"
    assert checkpoint.exists()
    recovered = tmp_path / "recovered"
    evaluated = subprocess.run([*common, "--mode", "evaluate", "--run-directory", str(recovered), "--checkpoint", str(checkpoint)], env=env, capture_output=True, text=True, timeout=90)
    assert evaluated.returncode == 0, evaluated.stdout + evaluated.stderr
    assert json.loads((recovered / "result.json").read_text())["groups"] == result["groups"]
    wrong_fold = subprocess.run([*common, "--mode", "evaluate", "--fold", "outer-1", "--run-directory", str(tmp_path / "wrong-fold"), "--checkpoint", str(checkpoint)], env=env, capture_output=True, text=True, timeout=90)
    assert wrong_fold.returncode != 0 and "checkpoint contract mismatch" in wrong_fold.stderr
    assert not (tmp_path / "wrong-fold").exists()


def test_complete_kaggle_cell_contains_current_dependencies_and_matches_notebook(tmp_path):
    package = ROOT / "kaggle_event_sequence_gru"
    source = (package / "ONE_CELL_CONTROLLED_COMPARISON.py").read_text()
    constants = {}
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in {"PAYLOAD", "EXPECTED_SHA256"}:
            constants[node.targets[0].id] = ast.literal_eval(node.value)
    payload = base64.b64decode(constants["PAYLOAD"])
    assert hashlib.sha256(payload).hexdigest() == constants["EXPECTED_SHA256"]
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        for name in archive.namelist():
            assert name.startswith(("src/", "scripts/", "kaggle_event_sequence_gru/"))
            assert name.endswith(".py") and ".." not in Path(name).parts
            assert archive.read(name) == (ROOT / name).read_bytes(), f"stale embedded source: {name}"
            compile(archive.read(name), name, "exec")
        archive.extractall(tmp_path)
    notebook = json.loads((package / "loop_controlled_comparison.ipynb").read_text())
    code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    assert len(code_cells) == 1 and "".join(code_cells[0]["source"]) == source
    assert not code_cells[0]["outputs"] and code_cells[0]["execution_count"] is None
    if importlib.util.find_spec("torch") is not None:
        # Run from the extracted package with no local project imports. This
        # verifies that the one-cell handoff needs no late code-dataset update.
        env = {**os.environ, "PYTHONPATH": str(tmp_path / "src") + os.pathsep + str(tmp_path / "scripts")}
        result = subprocess.run([sys.executable, str(tmp_path / "kaggle_event_sequence_gru/train_controlled.py"), "--self-test"], cwd=tmp_path, env=env, capture_output=True, text=True, timeout=60)
        assert result.returncode == 0, result.stdout + result.stderr
