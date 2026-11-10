#!/usr/bin/env python3
"""Integrity-check the aggregate artifacts cited by the novelty status report.

Reads run metadata and aggregate JSON only. It never reads prediction shards,
raw patient records, or emits participant identifiers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SHA256 = "69b41e4acfae7d2afc990c8cd15d8fc3f969784d4e5f6534a9263033d341ad52"
WINDOW_SHA256 = "26036d7d3d27c21a4407d15aacd916b98ba598dfded5da319288a74b54a592aa"
INPUT_SHA256 = "3c142f9e6fbeeac7afbb30bb745f67593fad1282c0463dd9a8a5b15314af4c28"


def load_json(relative: str):
    path = ROOT / relative
    payload = path.read_bytes()
    return json.loads(payload), {
        "path": relative,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
    }


def close(a, b):
    return math.isclose(float(a), float(b), rel_tol=0.0, abs_tol=1e-12)


def run_metadata(run_path: Path, *, fold: str, seed: int, participants: int,
                 windows: int, prediction_identity: str | None = None):
    # Archive paths in paired audit JSON are repository-relative. Resolve them
    # consistently so the checker works from any current working directory.
    if not run_path.is_absolute():
        run_path = ROOT / run_path
    relative = str(run_path.relative_to(ROOT))
    run, fingerprint = load_json(relative)
    assert run.get("complete") is True, f"incomplete run: {relative}"
    assert run.get("locked_holdout_used") is False, f"holdout used: {relative}"
    assert run.get("fold") == fold and run.get("seed") == seed, relative
    group = run["groups"]["validation"]
    assert group["participants"] == participants, relative
    assert group["windows"] == windows, relative
    assert run.get("manifest_sha256") == MANIFEST_SHA256, relative
    assert run.get("window_identity_sha256") == WINDOW_SHA256, relative
    if prediction_identity is not None:
        assert group.get("prediction_window_identity_sha256") == prediction_identity, relative
    return run, fingerprint


def audit_graph_sequence(file_checks):
    path = "audit/loop_mps_graph_sequence_two_seed_five_fold_summary_20261020.json"
    summary, fingerprint = load_json(path)
    file_checks.append(fingerprint)
    assert summary["locked_holdout_used"] is False
    assert len(summary["per_fold_seed"]) == 10
    assert summary["contract"]["epochs"] == 1
    assert summary["contract"]["parameters_per_model"] == 36883
    results = []
    for row in summary["per_fold_seed"]:
        paired, paired_fingerprint = load_json(row["audit_file"])
        file_checks.append(paired_fingerprint)
        assert paired_fingerprint["sha256"] == row["audit_sha256"]
        contract = paired["training_contract"]
        assert paired["draws"] == 10000
        assert paired["manifest_sha256"] == MANIFEST_SHA256
        assert paired["window_identity_sha256"] == WINDOW_SHA256
        assert contract["input_content_sha256"] == INPUT_SHA256
        assert paired["parameter_counts"] == {
            "graph_generic": 36883, "non_graph_sequence": 36883
        }, row["audit_file"]
        assert contract["epochs"] == 1 and contract["seed"] == row["seed"]
        assert contract["fold"] == row["fold"]
        assert paired["windows"] == row["windows"]
        assert paired["participants"] == row["participants"]
        assert close(paired["participant_macro_ap"]["difference_first_minus_second"],
                     row["ap_difference"])
        assert close(paired["participant_macro_brier"]["difference_first_minus_second"],
                     row["macro_brier_difference"])
        for side in ("first", "second"):
            archive = Path(paired[f"{side}_archive"])
            run, run_fingerprint = run_metadata(
                archive / "run.json", fold=row["fold"], seed=row["seed"],
                participants=row["participants"], windows=row["windows"],
                prediction_identity=row["prediction_identity_sha256"],
            )
            file_checks.append(run_fingerprint)
            assert run.get("input_content_sha256") == INPUT_SHA256
            assert run.get("trainable_parameters") == 36883
            assert run["groups"]["validation"]["positive_labels"] == paired["positive_labels"]
        results.append({"seed": row["seed"], "fold": row["fold"],
                        "participants": row["participants"], "windows": row["windows"],
                        "ap_difference_graph_minus_sequence": row["ap_difference"],
                        "macro_brier_difference_graph_minus_sequence": row["macro_brier_difference"]})
    assert summary["seed_fold_descriptives"][0]["folds_completed_n"] == 5
    assert summary["seed_fold_descriptives"][1]["folds_completed_n"] == 5
    return {
        "status": "verified",
        "fits": 10,
        "epochs_per_fit": 1,
        "parameters_per_model": 36883,
        "locked_holdout_used": False,
        "paired_results": results,
        "scope_limit": summary["note"],
    }


def audit_typed(file_checks):
    path = "audit/loop_relation_typed_vs_generic_seed20261004_five_fold_summary_20261020.json"
    summary, fingerprint = load_json(path)
    file_checks.append(fingerprint)
    assert len(summary["folds"]) == 5
    ap_differences = []
    for row in summary["folds"]:
        assert row["locked_holdout_used"] is False
        audit, fp = load_json(row["paired_audit"])
        file_checks.append(fp)
        assert audit["identifiers_emitted"] is False
        assert audit["manifest_sha256"] == MANIFEST_SHA256
        assert audit["window_identity_sha256"] == WINDOW_SHA256
        assert audit["parameter_counts"] == {"graph_generic": 36883, "graph_typed": 36883}
        assert audit["participants"] == row["participants"]
        assert audit["windows"] == row["windows"]
        assert close(audit["participant_macro_ap"]["difference_first_minus_second"],
                     row["typed_minus_generic_ap"])
        assert close(audit["participant_macro_brier"]["difference_first_minus_second"],
                     row["typed_minus_generic_macro_brier"])
        ap_differences.append(row["typed_minus_generic_ap"])
    assert close(sum(ap_differences) / len(ap_differences),
                 summary["descriptive_across_fold_summary"]["typed_minus_generic_participant_macro_ap_mean_unweighted_over_folds"])
    return {
        "status": "verified",
        "folds": 5,
        "seed": summary["seed"],
        "typed_ap_higher_folds": sum(r["typed_minus_generic_ap"] > 0 for r in summary["folds"]),
        "mean_fold_typed_minus_generic_ap": summary["descriptive_across_fold_summary"]["typed_minus_generic_participant_macro_ap_mean_unweighted_over_folds"],
        "locked_holdout_used": False,
    }


def audit_endpoint(file_checks):
    path = "audit/loop_relation_endpoint_perturbation_two_seed_five_fold_summary_20261028.json"
    summary, fingerprint = load_json(path)
    file_checks.append(fingerprint)
    assert summary["paired_evaluations"] == 10
    assert summary["training_seeds"] == [20261004, 20261005]
    assert summary["matched_model_parameters"] == 36883
    assert summary["manifest_sha256"] == MANIFEST_SHA256
    assert summary["window_identity_sha256"] == WINDOW_SHA256
    results = []
    for row in summary["per_seed_fold_results"]:
        audit_path = str(Path("audit") / row["paired_audit"])
        paired, fp = load_json(audit_path)
        file_checks.append(fp)
        assert paired["identifiers_emitted"] is False
        assert paired["manifest_sha256"] == MANIFEST_SHA256
        assert paired["window_identity_sha256"] == WINDOW_SHA256
        assert paired["participants"] == row["participants"]
        assert paired["windows"] == row["windows"]
        assert close(paired["participant_macro_ap"]["difference_first_minus_second"],
                     row["nearest_minus_second_nearest_ap"])
        assert close(paired["participant_macro_brier"]["difference_first_minus_second"],
                     row["nearest_minus_second_nearest_macro_brier"])
        for side in ("first", "second"):
            archive = Path(paired[f"{side}_archive"])
            run, run_fp = run_metadata(
                archive / "run.json", fold=row["fold"], seed=row["seed"],
                participants=row["participants"], windows=row["windows"],
            )
            file_checks.append(run_fp)
            assert run["locked_holdout_used"] is False
        results.append({"seed": row["seed"], "fold": row["fold"],
                        "nearest_minus_second_nearest_ap": row["nearest_minus_second_nearest_ap"],
                        "nearest_minus_second_nearest_macro_brier": row["nearest_minus_second_nearest_macro_brier"]})
    return {
        "status": "verified",
        "fits": 10,
        "nearest_higher_ap_fits": summary["descriptive_direction_counts_across_10_seed_fold_pairs"]["nearest_ap_higher"],
        "nearest_lower_brier_fits": summary["descriptive_direction_counts_across_10_seed_fold_pairs"]["nearest_macro_brier_lower"],
        "participant_cluster_bootstrap": summary["participant_cluster_bootstrap"],
        "locked_holdout_used": False,
        "scope_limit": summary["inference_limit"],
        "paired_results": results,
    }


def audit_event_age(file_checks):
    path = "audit/loop_event_age_reassignment_two_seed_five_fold_summary_20261029.json"
    summary, fingerprint = load_json(path)
    file_checks.append(fingerprint)
    assert len(summary["fold_seed_results"]) == 10
    assert summary["all_clean_replays_reproduced_saved_metrics_and_identity"] is True
    assert summary["locked_holdout_used"] is False
    rows = []
    for row in summary["fold_seed_results"]:
        fold_file = row["fold"].replace("-", "")
        name = f"audit/loop_event_age_reassignment_{fold_file}_seed{row['seed']}_20261028.json"
        audit, fp = load_json(name)
        file_checks.append(fp)
        assert audit["identifiers_emitted"] is False
        assert audit["locked_holdout_used"] is False
        assert audit["window_identity_sha256"] == WINDOW_SHA256
        assert audit["participants"] == row["participants"]
        assert audit["windows"] == row["windows"]
        assert audit["seed"] == row["seed"]
        assert audit["fold"] == row["fold"]
        assert close(audit["metrics"]["participant_macro_ap"]["original_minus_reassigned"],
                     row["ap_original_minus_reassigned"])
        assert close(audit["metrics"]["participant_macro_brier"]["original_minus_reassigned"],
                     row["brier_original_minus_reassigned"])
        rows.append({"seed": row["seed"], "fold": row["fold"],
                     "original_minus_reassigned_ap": row["ap_original_minus_reassigned"],
                     "original_minus_reassigned_macro_brier": row["brier_original_minus_reassigned"]})
    return {"status": "verified", "fits": 10,
            "descriptive_fixed_fit_summary": summary["descriptive_fixed_fit_summary"],
            "locked_holdout_used": False, "paired_results": rows,
            "scope_limit": summary["interpretation"]}


def audit_explanations(file_checks):
    path = "audit/loop_graph_event_explanation_faithfulness_outer0_seed20261005_20261029_v2.json"
    report, fingerprint = load_json(path)
    file_checks.append(fingerprint)
    assert report["identifiers_emitted"] is False
    assert report["locked_holdout_used"] is False
    assert report["sampling"]["validation_windows_scanned"] == 8885621
    assert report["sampling"]["validation_positive_labels"] == 274044
    assert report["sampling"]["sampled_windows"] == 518
    assert report["sampling"]["participants_sampled"] == 130
    return {"status": "verified", "sampled_windows": 518, "participants": 130,
            "locked_holdout_used": False,
            "participant_average_top_minus_random_joint_deletion": report["results"]["top_minus_random_deletion_abs_probability_change"]["mean_across_sampled_participants"],
            "participant_average_random_minus_top_retention": report["results"]["random_minus_top_retention_abs_probability_difference"]["mean_across_sampled_participants"],
            "selection_conditioned": True,
            "scope_limit": report["limitations"]}


def audit_aligned_control(file_checks):
    """Verify the matched time-aligned graph/non-graph development pilot."""
    path = "audit/loop_graph_vs_aligned_nongraph_outer0_seed20261029.json"
    paired, fingerprint = load_json(path)
    file_checks.append(fingerprint)
    assert paired["identifiers_emitted"] is False
    assert paired["comparison_contract"] == "loop-graph-vs-time-aligned-nongraph-v1"
    assert paired["manifest_sha256"] == MANIFEST_SHA256
    assert paired["window_identity_sha256"] == WINDOW_SHA256
    assert paired["seed"] == 20261029 and paired["group"] == "validation"
    assert paired["draws"] == 10000
    assert paired["participants"] == 130 and paired["windows"] == 8885621
    assert paired["positive_labels"] == 274044
    assert paired["parameter_counts"] == {
        "aligned_nongraph": 36883, "graph_generic": 36883
    }
    runs = {}
    for side, variant in (("first", "graph-generic"),
                          ("second", "aligned-nongraph")):
        archive = Path(paired[f"{side}_archive"])
        run, run_fingerprint = run_metadata(
            archive / "run.json", fold="outer-0", seed=20261029,
            participants=130, windows=8885621,
        )
        file_checks.append(run_fingerprint)
        assert run.get("variant") == variant
        assert run.get("input_content_sha256") == INPUT_SHA256
        assert run.get("trainable_parameters") == 36883
        assert run.get("epochs") == 2 and run.get("batch_size") == 4096
        runs[variant] = run
    graph_run = runs["graph-generic"]
    control_run = runs["aligned-nongraph"]
    assert graph_run.get("source_sha256") == control_run.get("source_sha256")
    assert graph_run.get("training_membership_sha256") == control_run.get("training_membership_sha256")
    graph_group = graph_run["groups"]["validation"]
    control_group = control_run["groups"]["validation"]
    assert graph_group.get("prediction_window_identity_sha256")
    assert graph_group["prediction_window_identity_sha256"] == control_group.get(
        "prediction_window_identity_sha256")
    ap = paired["participant_macro_ap"]
    brier = paired["participant_macro_brier"]
    assert close(ap["first"], graph_group["participant_macro_ap"])
    assert close(ap["second"], control_group["participant_macro_ap"])
    assert close(brier["first"], graph_group["participant_macro_brier"])
    assert close(brier["second"], control_group["participant_macro_brier"])
    return {
        "status": "verified",
        "fold": "outer-0",
        "seed": 20261029,
        "epochs": 2,
        "participants": paired["participants"],
        "windows": paired["windows"],
        "positive_labels": paired["positive_labels"],
        "parameters_per_arm": 36883,
        "prediction_window_identity_sha256": graph_group[
            "prediction_window_identity_sha256"],
        "graph_minus_control_ap": ap["difference_first_minus_second"],
        "graph_minus_control_ap_ci95": ap["difference_ci95"],
        "graph_minus_control_macro_brier": brier["difference_first_minus_second"],
        "graph_minus_control_macro_brier_ci95": brier["difference_ci95"],
        "locked_holdout_used": False,
        "scope_limit": paired["interpretation"],
    }


def audit_aligned_control_replication(file_checks):
    """Verify every second-seed fold against its strict pair and run metadata."""
    summary_path = "audit/loop_graph_vs_aligned_nongraph_seed20261030_five_fold_summary.json"
    summary, summary_fp = load_json(summary_path)
    file_checks.append(summary_fp)
    assert summary["seed"] == 20261030
    assert summary["locked_holdout_used"] is False
    assert summary["manifest_sha256"] == MANIFEST_SHA256
    assert summary["input_content_sha256"] == INPUT_SHA256
    assert summary["participants"] == 652
    assert summary["windows"] == 44028064
    assert summary["positive_labels"] == 1296297
    assert summary["parameters_per_arm"] == 36883
    assert summary["epochs"] == 2
    assert len(summary["fold_results"]) == 5

    expected_source = "a4d1a91916a675024110e1c30d54546c3aa0d51724480dfdbcdbb141dea71648"
    rows = []
    folds = []
    for number in range(5):
        fold = f"outer-{number}"
        pair_path = f"audit/loop_graph_vs_aligned_nongraph_outer{number}_seed20261030_source_a4d.json"
        paired, pair_fp = load_json(pair_path)
        file_checks.append(pair_fp)
        assert paired["identifiers_emitted"] is False
        assert paired.get("locked_holdout_used") is not True
        assert paired["comparison_contract"] == "loop-graph-vs-time-aligned-nongraph-v1"
        assert paired["seed"] == 20261030 and paired["group"] == "validation"
        assert paired["draws"] == 10000
        assert paired["manifest_sha256"] == MANIFEST_SHA256
        assert paired["window_identity_sha256"] == WINDOW_SHA256
        assert paired["parameter_counts"] == {
            "aligned_nongraph": 36883, "graph_generic": 36883
        }
        assert paired["shared_timing_contract"] == (
            "same event tokens assigned to nearest observed later CGM time bin; future bins forbidden"
        )
        assert paired["participants"] == summary["fold_results"][fold]["participants"]
        assert paired["windows"] > 0
        assert paired["first_variant"] == "graph-generic"
        assert paired["second_variant"] == "aligned-nongraph"

        runs = {}
        for side, variant in (("first", "graph-generic"), ("second", "aligned-nongraph")):
            archive = Path(paired[f"{side}_archive"])
            run, run_fp = run_metadata(
                archive / "run.json", fold=fold, seed=20261030,
                participants=paired["participants"], windows=paired["windows"],
            )
            file_checks.append(run_fp)
            assert run["variant"] == variant
            assert run["source_sha256"] == expected_source
            assert run["input_content_sha256"] == INPUT_SHA256
            assert run["trainable_parameters"] == 36883
            assert run["epochs"] == 2 and run["batch_size"] == 4096
            assert run["workers"] == 3
            assert run["groups"]["validation"]["positive_labels"] == paired["positive_labels"]
            runs[variant] = run

        graph_group = runs["graph-generic"]["groups"]["validation"]
        control_group = runs["aligned-nongraph"]["groups"]["validation"]
        assert graph_group["prediction_window_identity_sha256"] == control_group["prediction_window_identity_sha256"]
        assert graph_group["prediction_window_identity_sha256"]
        assert close(paired["participant_macro_ap"]["first"], graph_group["participant_macro_ap"])
        assert close(paired["participant_macro_ap"]["second"], control_group["participant_macro_ap"])
        assert close(paired["participant_macro_brier"]["first"], graph_group["participant_macro_brier"])
        assert close(paired["participant_macro_brier"]["second"], control_group["participant_macro_brier"])
        row = summary["fold_results"][fold]
        assert close(paired["participant_macro_ap"]["difference_first_minus_second"], row["ap_graph_minus_control"])
        assert close(paired["participant_macro_brier"]["difference_first_minus_second"], row["macro_brier_graph_minus_control"])
        rows.append({
            "fold": fold,
            "participants": paired["participants"],
            "windows": paired["windows"],
            "positive_labels": paired["positive_labels"],
            "graph_minus_control_ap": paired["participant_macro_ap"]["difference_first_minus_second"],
            "graph_minus_control_ap_ci95": paired["participant_macro_ap"]["difference_ci95"],
            "graph_minus_control_macro_brier": paired["participant_macro_brier"]["difference_first_minus_second"],
            "graph_minus_control_macro_brier_ci95": paired["participant_macro_brier"]["difference_ci95"],
            "source_sha256": expected_source,
            "prediction_identity_sha256": graph_group["prediction_window_identity_sha256"],
        })
        folds.append(fold)

    assert sum(row["participants"] for row in rows) == 652
    assert sum(row["windows"] for row in rows) == 44028064
    assert sum(row["positive_labels"] for row in rows) == 1296297
    ap = summary["participant_macro_ap_difference"]
    brier = summary["participant_macro_brier_difference"]
    assert close(ap["graph_minus_control"], -0.01219261726763336)
    assert close(brier["graph_minus_control"], 0.00017278452889733263)
    return {
        "status": "verified",
        "seed": 20261030,
        "epochs": 2,
        "folds": 5,
        "parameters_per_arm": 36883,
        "participants": 652,
        "windows": 44028064,
        "positive_labels": 1296297,
        "source_sha256": expected_source,
        "fold_results": rows,
        "aggregate_ap_graph_minus_control": ap,
        "aggregate_macro_brier_graph_minus_control": brier,
        "locked_holdout_used": False,
        "scope_limit": summary["interpretation"],
    }


def audit_two_seed_participant_summary(file_checks):
    path = "audit/loop_graph_vs_aligned_nongraph_two_seed_five_fold_participant_summary.json"
    summary, fingerprint = load_json(path)
    file_checks.append(fingerprint)
    assert summary["audit_type"] == "two-seed participant-level paired graph vs aligned-pooling summary"
    assert summary["seeds"] == [20261029, 20261030]
    assert summary["folds"] == [f"outer-{i}" for i in range(5)]
    assert summary["locked_holdout_used"] is False
    assert summary["manifest_sha256"] == MANIFEST_SHA256
    assert summary["input_content_sha256"] == INPUT_SHA256
    assert summary["participants"] == 652
    assert summary["ap_defined_participants"] == 650
    assert summary["windows"] == 44028064
    assert summary["positive_labels"] == 1296297
    assert set(summary["fold_results"]) == set(summary["folds"])

    first_seed_audits = {
        0: "loop_graph_vs_aligned_nongraph_outer0_seed20261029.json",
        1: "loop_graph_vs_aligned_nongraph_outer1_seed20261029.json",
        2: "loop_graph_vs_aligned_nongraph_outer2_seed20261029_current_source_rerun.json",
        3: "loop_graph_vs_aligned_nongraph_outer3_seed20261029_current_source.json",
        4: "loop_graph_vs_aligned_nongraph_outer4_seed20261029_source_a4d.json",
    }
    identity_checks = []
    for number, fold in enumerate(summary["folds"]):
        audit_paths = [
            f"audit/{first_seed_audits[number]}",
            f"audit/loop_graph_vs_aligned_nongraph_outer{number}_seed20261030_source_a4d.json",
        ]
        identities_by_seed = []
        for seed, audit_path in zip(summary["seeds"], audit_paths):
            paired, pair_fp = load_json(audit_path)
            file_checks.append(pair_fp)
            assert paired["comparison_contract"] == "loop-graph-vs-time-aligned-nongraph-v1"
            assert paired["seed"] == seed
            assert paired["identifiers_emitted"] is False
            assert paired["parameter_counts"] == {"aligned_nongraph": 36883, "graph_generic": 36883}
            assert paired["participants"] == summary["fold_results"][fold]["participants"]
            assert paired["windows"] > 0
            assert paired["manifest_sha256"] == MANIFEST_SHA256
            assert paired["window_identity_sha256"] == WINDOW_SHA256
            side_identities = {}
            side_sources = {}
            for side, variant in (("first", "graph-generic"), ("second", "aligned-nongraph")):
                archive = Path(paired[f"{side}_archive"])
                run, run_fp = run_metadata(
                    archive / "run.json", fold=fold, seed=seed,
                    participants=paired["participants"], windows=paired["windows"],
                )
                file_checks.append(run_fp)
                assert run["variant"] == variant
                assert run["trainable_parameters"] == 36883 and run["epochs"] == 2
                assert run["groups"]["validation"]["positive_labels"] == paired["positive_labels"]
                side_identities[variant] = run["groups"]["validation"]["prediction_window_identity_sha256"]
                side_sources[variant] = run["source_sha256"]
            assert side_identities["graph-generic"] == side_identities["aligned-nongraph"]
            assert side_identities["graph-generic"]
            expected_sources = summary["fold_results"][fold]["source_sha256"]
            assert side_sources["graph-generic"] == expected_sources[str(seed)]
            assert side_sources["aligned-nongraph"] == expected_sources[str(seed)]
            identities_by_seed.append(side_identities["graph-generic"])
        assert identities_by_seed[0] == identities_by_seed[1], f"cross-seed prediction window identity differs: {fold}"
        identity_checks.append({"fold": fold, "shared_seed_prediction_identity_sha256": identities_by_seed[0]})

    ap = summary["participant_macro_ap_difference"]
    brier = summary["participant_macro_brier_difference"]
    assert close(ap["graph_minus_control_after_within_participant_seed_average"], -0.009899666243301021)
    assert close(brier["graph_minus_control_after_within_participant_seed_average"], 0.00012643217625050957)
    for fold in summary["folds"]:
        row = summary["fold_results"][fold]
        assert set(row["source_sha256"]) == {"20261029", "20261030"}
        assert row["participants"] > 0
    return {
        "status": "verified_summary_contract",
        "seeds": summary["seeds"],
        "folds": summary["folds"],
        "participants": summary["participants"],
        "windows": summary["windows"],
        "positive_labels": summary["positive_labels"],
        "participant_macro_ap_difference": ap,
        "participant_macro_brier_difference": brier,
        "cross_seed_prediction_identity_checks": identity_checks,
        "scope_limit": summary["interpretation"],
        "note": "Summary contract and reported constants checked here; saved-prediction recomputation is performed by summarize_two_seed_graph_aligned_control.py.",
    }


def audit_extended_schedule(file_checks):
    """Verify the single-fold, eight-epoch CPU schedule-sensitivity pair."""
    paired_path = "audit/loop_longer_schedule_outer0_seed20261031_graph_vs_aligned_cpu8.json"
    paired, paired_fp = load_json(paired_path)
    file_checks.append(paired_fp)
    assert paired.get("identifiers_emitted") is False
    assert paired.get("comparison_contract") == "loop-graph-vs-time-aligned-nongraph-v1"
    assert paired.get("seed") == 20261031 and paired.get("group") == "validation"
    assert paired.get("draws") == 10000 and paired.get("participants") == 130
    assert paired.get("windows") == 8885621 and paired.get("positive_labels") == 274044
    assert paired.get("manifest_sha256") == MANIFEST_SHA256
    assert paired.get("window_identity_sha256") == WINDOW_SHA256
    assert paired.get("parameter_counts") == {"graph_generic": 36883, "aligned_nongraph": 36883}
    ap = paired["participant_macro_ap"]
    brier = paired["participant_macro_brier"]
    assert close(ap["difference_first_minus_second"], -0.0007158781777918263)
    assert close(brier["difference_first_minus_second"], 0.000014150974249584901)

    runs = {}
    for side, variant in (("first", "graph-generic"), ("second", "aligned-nongraph")):
        archive = Path(paired[f"{side}_archive"])
        run, run_fp = run_metadata(
            archive / "run.json", fold="outer-0", seed=20261031,
            participants=130, windows=8885621,
            prediction_identity="a68ad87255e8b8944b269a6995489640ee6b37576799e917d548a0d161700224",
        )
        file_checks.append(run_fp)
        assert run.get("complete") is True and run.get("prediction_identity_verified") is True
        assert run.get("variant") == variant and run.get("epochs") == 8
        assert run.get("batch_size") == 4096 and run.get("workers") == 3
        assert run.get("trainable_parameters") == 36883
        assert run.get("input_content_sha256") == INPUT_SHA256
        assert run.get("training_membership_sha256") == "ff0e90e1508ecb24a55733797fc067373b9c89c4ef02d8449226f8e651e32fb3"
        assert run.get("environment", {}).get("device") == "cpu"
        assert run.get("locked_holdout_used") is False
        assert len(run.get("training_log", [])) == 8
        runs[variant] = run

    graph, control = runs["graph-generic"], runs["aligned-nongraph"]
    for key in ("source_sha256", "training_membership_sha256", "input_content_sha256",
                "window_identity_sha256", "manifest_sha256", "fold", "seed", "epochs",
                "batch_size", "workers", "optimizer"):
        assert graph.get(key) == control.get(key), f"extended schedule pair differs: {key}"
    gg, cg = graph["groups"]["validation"], control["groups"]["validation"]
    assert gg["prediction_window_identity_sha256"] == cg["prediction_window_identity_sha256"]
    assert gg["prediction_window_identity_sha256"] == (
        "a68ad87255e8b8944b269a6995489640ee6b37576799e917d548a0d161700224")
    assert close(gg["participant_macro_ap"], ap["first"])
    assert close(cg["participant_macro_ap"], ap["second"])
    assert close(gg["participant_macro_brier"], brier["first"])
    assert close(cg["participant_macro_brier"], brier["second"])
    return {
        "status": "verified",
        "fold": "outer-0",
        "seed": 20261031,
        "epochs": 8,
        "parameters_per_arm": 36883,
        "device": "cpu",
        "participants": 130,
        "windows": 8885621,
        "graph_minus_aligned_ap": ap,
        "graph_minus_aligned_macro_brier": brier,
        "source_sha256": graph["source_sha256"],
        "locked_holdout_used": False,
        "scope_limit": "One development fold and one seed; fixed-prediction intervals do not estimate model-fit, seed, or cohort uncertainty.",
    }
    assert paired["shared_timing_contract"] == (
        "same event tokens assigned to nearest observed later CGM time bin; future bins forbidden"
    )
    runs = {}
    for side, variant in (("first", "graph-generic"), ("second", "aligned-nongraph")):
        archive = Path(paired[f"{side}_archive"])
        run, run_fingerprint = run_metadata(
            archive / "run.json", fold="outer-0", seed=20261029,
            participants=130, windows=8885621,
            prediction_identity="a68ad87255e8b8944b269a6995489640ee6b37576799e917d548a0d161700224",
        )
        file_checks.append(run_fingerprint)
        assert run["input_content_sha256"] == INPUT_SHA256
        assert run["trainable_parameters"] == 36883
        assert run["epochs"] == 2 and run["batch_size"] == 4096
        assert run["workers"] == 3 and run["locked_holdout_used"] is False
        assert run["variant"] == variant
        assert run["groups"]["validation"]["positive_labels"] == 274044
        runs[variant] = run

    ap = paired["participant_macro_ap"]
    brier = paired["participant_macro_brier"]
    assert close(ap["first"], runs["graph-generic"]["groups"]["validation"]["participant_macro_ap"])
    assert close(ap["second"], runs["aligned-nongraph"]["groups"]["validation"]["participant_macro_ap"])
    assert close(brier["first"], runs["graph-generic"]["groups"]["validation"]["participant_macro_brier"])
    assert close(brier["second"], runs["aligned-nongraph"]["groups"]["validation"]["participant_macro_brier"])
    return {
        "status": "verified",
        "fold": "outer-0",
        "seed": 20261029,
        "epochs": 2,
        "participants": 130,
        "windows": 8885621,
        "parameters_per_model": 36883,
        "graph_minus_aligned_nongraph_ap": ap["difference_first_minus_second"],
        "graph_minus_aligned_nongraph_ap_ci95": ap["difference_ci95"],
        "participants_graph_ap_higher": ap["positive_difference_participants"],
        "participants_graph_ap_lower": ap["negative_difference_participants"],
        "graph_minus_aligned_nongraph_macro_brier": brier["difference_first_minus_second"],
        "graph_minus_aligned_nongraph_macro_brier_ci95": brier["difference_ci95"],
        "participants_graph_brier_lower": brier["negative_difference_participants"],
        "pooled_brier": paired["pooled_brier"],
        "locked_holdout_used": False,
        "scope_limit": paired["interpretation"],
    }


def audit_recovered_sequence_event_ablation(file_checks):
    """Check the recovered two-epoch full-history sequence event ablation."""
    path = "audit/loop_full_history_event_ablation_outer0_seed20261003_paired_20261031.json"
    paired, fingerprint = load_json(path)
    file_checks.append(fingerprint)
    assert paired["identifiers_emitted"] is False
    assert paired["manifest_sha256"] == MANIFEST_SHA256
    assert paired["window_identity_sha256"] == WINDOW_SHA256
    assert paired["contract_version"] == "loop-full-history-neural-v1"
    assert paired["first_variant"] == "history-event"
    assert paired["second_variant"] == "history-event-zero"
    assert paired["draws"] == 10_000
    assert paired["participants"] == 130 and paired["windows"] == 8_885_621
    assert paired["positive_labels"] == 274_044
    assert paired["declared_parameter_count_each"] == 36_609

    runs = {}
    for side, variant in (("first", "history-event"),
                          ("second", "history-event-zero")):
        archive = Path(paired[f"{side}_archive"])
        if not archive.is_absolute():
            archive = ROOT / archive
        relative = str((archive / "run.json").relative_to(ROOT))
        run, run_fingerprint = load_json(relative)
        file_checks.append(run_fingerprint)
        assert run["complete"] is True
        assert run["prediction_identity_verified"] is True
        if "locked_holdout_used" in run:
            assert run["locked_holdout_used"] is False
        assert run["evaluation_scope"] == "validation"
        assert run["variant"] == variant
        assert run["fold"] == "outer-0" and run["seed"] == 20261003
        assert run["epochs"] == 2 and run["batch_size"] == 4096
        assert run["trainable_parameters"] == 36_609
        assert run["manifest_sha256"] == MANIFEST_SHA256
        assert run["window_identity_sha256"] == WINDOW_SHA256
        assert run["training_membership_sha256"] == (
            "ff0e90e1508ecb24a55733797fc067373b9c89c4ef02d8449226f8e651e32fb3")
        assert run["groups"]["validation"]["prediction_window_identity_sha256"] == (
            "a68ad87255e8b8944b269a6995489640ee6b37576799e917d548a0d161700224")
        runs[variant] = run

    event, zero = runs["history-event"], runs["history-event-zero"]
    assert event["source_sha256"] == zero["source_sha256"]
    assert event["input_content_sha256"] == zero["input_content_sha256"] == INPUT_SHA256
    assert event["groups"]["validation"]["participants"] == zero["groups"]["validation"]["participants"] == 130
    assert event["groups"]["validation"]["windows"] == zero["groups"]["validation"]["windows"] == 8_885_621
    ap = paired["participant_macro_ap"]
    brier = paired["participant_macro_brier"]
    assert close(ap["first"], event["groups"]["validation"]["participant_macro_ap"])
    assert close(ap["second"], zero["groups"]["validation"]["participant_macro_ap"])
    assert close(brier["first"], event["groups"]["validation"]["participant_macro_brier"])
    assert close(brier["second"], zero["groups"]["validation"]["participant_macro_brier"])
    return {
        "status": "verified",
        "architecture": "full-history sequence event branch; not a graph model",
        "fold": "outer-0", "seed": 20261003, "epochs": 2,
        "participants": 130, "windows": 8_885_621,
        "holdout_scope_note": "recovered archive marks validation scope but has no explicit locked_holdout_used field",
        "event_minus_zero_ap": ap["difference_first_minus_second"],
        "event_minus_zero_ap_ci95": ap["difference_ci95"],
        "event_minus_zero_macro_brier": brier["difference_first_minus_second"],
        "scope_limit": paired["interpretation"],
    }


def audit_graph_event_disabled(file_checks):
    """Check the matched two-epoch outer-0 graph event-input ablation."""
    path = "audit/loop_graph_event_ablation_outer0_seed20261031_paired_20261031.json"
    paired, fingerprint = load_json(path)
    file_checks.append(fingerprint)
    assert paired["identifiers_emitted"] is False
    assert paired["contract_version"] == "loop-full-history-temporal-relations-v1"
    assert paired["first_variant"] == "graph-generic"
    assert paired["second_variant"] == "graph-event-disabled"
    assert paired["draws"] == 10_000
    assert paired["manifest_sha256"] == MANIFEST_SHA256
    assert paired["window_identity_sha256"] == WINDOW_SHA256
    assert paired["declared_parameter_count_each"] == 36_883
    assert paired["participants"] == 130 and paired["windows"] == 8_885_621
    assert paired["positive_labels"] == 274_044
    assert paired["seed"] == 20261031 and paired["group"] == "validation"
    for side, variant in (("first", "graph-generic"),
                          ("second", "graph-event-disabled")):
        archive = Path(paired[f"{side}_archive"])
        run, run_fingerprint = run_metadata(
            archive / "run.json", fold="outer-0", seed=20261031,
            participants=130, windows=8_885_621,
            prediction_identity="a68ad87255e8b8944b269a6995489640ee6b37576799e917d548a0d161700224",
        )
        file_checks.append(run_fingerprint)
        assert run["variant"] == variant
        assert run["trainable_parameters"] == 36_883
        assert run["input_content_sha256"] == INPUT_SHA256
        assert run["training_membership_sha256"] == (
            "ff0e90e1508ecb24a55733797fc067373b9c89c4ef02d8449226f8e651e32fb3")
        assert run["source_sha256"] == "d536c331439e3d34b6c52a909b16d46e470892f0223a3fffa673cdc4d8ca3048"
        assert run["epochs"] == 2 and run["locked_holdout_used"] is False
    ap, brier = paired["participant_macro_ap"], paired["participant_macro_brier"]
    assert close(ap["difference_first_minus_second"],
                 paired["participant_macro_ap"]["first"] - paired["participant_macro_ap"]["second"])
    return {
        "status": "verified",
        "fold": "outer-0", "seed": 20261031, "epochs": 2,
        "participants": 130, "windows": 8_885_621,
        "parameters_per_model": 36_883,
        "graph_minus_event_disabled_ap": ap["difference_first_minus_second"],
        "graph_minus_event_disabled_ap_ci95": ap["difference_ci95"],
        "participants_graph_ap_higher": ap["positive_difference_participants"],
        "graph_minus_event_disabled_macro_brier": brier["difference_first_minus_second"],
        "graph_minus_event_disabled_macro_brier_ci95": brier["difference_ci95"],
        "locked_holdout_used": False,
        "scope_limit": paired["interpretation"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=Path("audit/novelty_evidence_bundle_20261031_v10.json"))
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite {args.output}; choose a new path")
    checks = []
    result = {
        "audit_type": "aggregate novelty evidence integrity audit",
        "audit_date": "2026-10-31",
        "manifest_sha256": MANIFEST_SHA256,
        "window_identity_sha256": WINDOW_SHA256,
        "input_content_sha256": INPUT_SHA256,
        "locked_holdout_used": False,
        "identifiers_emitted": False,
        "scope": "Loop development evidence only; no model fitting or participant-level prediction data read",
        "experiments": {
            "graph_vs_sequence": audit_graph_sequence(checks),
            "typed_vs_generic": audit_typed(checks),
            "endpoint_perturbation": audit_endpoint(checks),
            "event_age_reassignment": audit_event_age(checks),
            "explanation_sensitivity": audit_explanations(checks),
            "time_aligned_nongraph_control": audit_aligned_control(checks),
            "time_aligned_nongraph_second_seed": audit_aligned_control_replication(checks),
            "time_aligned_nongraph_two_seed_participant_summary": audit_two_seed_participant_summary(checks),
            "longer_schedule_outer0": audit_extended_schedule(checks),
            "recovered_sequence_event_ablation": audit_recovered_sequence_event_ablation(checks),
            "graph_event_disabled_ablation": audit_graph_event_disabled(checks),
        },
        "source_files_checked": checks,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "source_files_checked"},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
