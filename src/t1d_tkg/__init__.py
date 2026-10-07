"""Leakage-aware primitives for the T1D-TKG research benchmark."""

from .events import Event
from .windows import WindowSample, build_prediction_windows
from .graph import AsOfGraph, build_asof_graph
from .ohio import OhioParseResult, load_ohio_directory, parse_ohio_xml
from .baselines import persistence_slope_score, persistence_slope_score_from_current_and_slope, persistence_slope_score_from_values
from .episodes import confirmed_episode_onsets, match_alerts_to_episodes, select_alert_threshold, simulate_alerts, suppress_alerts
from .metrics import average_precision, brier_score, participant_macro_ap
from .evaluation import evaluate_loso_cgm
from .features import cgm_recent_features, cgm_summary
from .logistic import LogisticModel, fit_logistic, fit_streaming_logistic
from .multimodal import multimodal_summary
from .evaluation import evaluate_loso_multimodal, evaluate_loso_event_sequence
from .event_sequence import event_sequence_summary
from .uncertainty import paired_cluster_bootstrap
from .calibration import PlattScaler, expected_calibration_error, fit_platt_scaler, reliability_bins
from .graph_features import graph_summary, graph_summary_for_sample
from .evaluation import evaluate_loso_graph
from .manifest import build_hashed_kfold_manifest, build_loso_manifest, fold_by_patient, load_manifest, manifest_checksum, save_manifest, validate_manifest
from .explanations import evidence_record, remove_evidence_nodes
from .validation import validate_event_collection
from .archive import validate_prediction_archive
from .config import BenchmarkConfig, DEFAULT_CONFIG
from .window_index import iter_window_index, validate_window_index, validate_window_index_directory, window_index_record, write_window_index
from .range_policy import CgmRangePolicy, filter_cgm_events, get_range_policy
from .event_alignment import aligned_event_counts
from .captured_events import captured_event_features, iter_captured_event_features

__all__ = [
    "AsOfGraph",
    "Event",
    "OhioParseResult",
    "WindowSample",
    "build_asof_graph",
    "build_prediction_windows",
    "load_ohio_directory",
    "parse_ohio_xml",
    "persistence_slope_score",
    "persistence_slope_score_from_values",
    "persistence_slope_score_from_current_and_slope",
    "confirmed_episode_onsets",
    "match_alerts_to_episodes",
    "suppress_alerts",
    "simulate_alerts",
    "select_alert_threshold",
    "average_precision",
    "brier_score",
    "participant_macro_ap",
    "evaluate_loso_cgm",
    "cgm_summary",
    "cgm_recent_features",
    "LogisticModel",
    "fit_logistic",
    "fit_streaming_logistic",
    "multimodal_summary",
    "evaluate_loso_multimodal",
    "event_sequence_summary",
    "evaluate_loso_event_sequence",
    "paired_cluster_bootstrap",
    "PlattScaler",
    "fit_platt_scaler",
    "reliability_bins",
    "expected_calibration_error",
    "graph_summary",
    "graph_summary_for_sample",
    "evaluate_loso_graph",
    "build_loso_manifest",
    "build_hashed_kfold_manifest",
    "validate_manifest",
    "manifest_checksum",
    "save_manifest",
    "load_manifest",
    "fold_by_patient",
    "evidence_record",
    "remove_evidence_nodes",
    "validate_event_collection",
    "validate_prediction_archive",
    "BenchmarkConfig",
    "DEFAULT_CONFIG",
    "CgmRangePolicy",
    "filter_cgm_events",
    "get_range_policy",
    "window_index_record",
    "write_window_index",
    "iter_window_index",
    "validate_window_index",
    "validate_window_index_directory",
    "aligned_event_counts",
    "captured_event_features",
    "iter_captured_event_features",
]
