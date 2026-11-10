#!/usr/bin/env python3
"""Build a shareable, aggregate-only novelty review package."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = Path("docs/novelty_evidence_report_2026_10_31.md")
BASE_FILES = {
    "docs/novelty_evidence_report_2026_10_31.md",
    "docs/primary_source_novelty_check_2026_10_31.md",
    "docs/primary_source_novelty_update_2026_10_31.md",
    "docs/primary_source_check_attention_tft_2026_10_31.md",
    "docs/primary_source_event_context_2026_10_31.md",
    "docs/targeted_prior_art_search_2026_10_31.md",
    "docs/proposal_validation.md",
    "docs/refined_proposal.md",
    "docs/novelty_evidence_audit_correction_2026_10_31.md",
    "docs/literature_search_log.md",
    "docs/literature_matrix.csv",
    "docs/pubmed_search_protocol_2026_10_31.md",
    "docs/novelty_assessment.md",
    "docs/novelty_status_and_paper_direction_2026_10_30.md",
    "docs/decisive_experiments.md",
    "docs/research_plan.md",
    "docs/research_protocol.md",
    "docs/loop_time_aligned_nongraph_control.md",
    "audit/novelty_evidence_bundle_20261031_v10.json",
    "audit/loop_graph_event_ablation_outer0_seed20261031_paired_20261031.json",
    "scripts/audit_novelty_evidence_bundle.py",
    "audit/loop_full_history_event_ablation_outer0_seed20261003_paired_20261031.json",
    "scripts/compare_full_history_event_ablation.py",
    "audit/loop_longer_schedule_outer0_seed20261031_graph_vs_aligned_cpu8.json",
    "audit/dclp_temporal_coverage_20261031.json",
    "audit/dclp_eligible_windows_20261031.json",
    "audit/dclp_insulin_semantics_20261031.json",
    "audit/dclp5_eligible_windows_raw_time_20261031.json",
    "audit/dclp5_eligible_windows_adjusted_time_20261031.json",
    "audit/dclp3_eligible_windows_raw_time_20261031.json",
    "audit/dclp_timestamp_policy_sensitivity_20261031.json",
    "docs/loop_extended_schedule_protocol_2026_10_31.md",
    "docs/dclp_temporal_coverage_audit_2026_10_31.md",
    "scripts/audit_jaeb_eligible_windows.py",
    "scripts/audit_dclp_insulin_semantics.py",
    "scripts/audit_jaeb_timestamp_policy_sensitivity.py",
    "docs/jaeb_candidate_screening.md",
    "docs/frozen_loop_cgm_jaeb_transfer_20261031.md",
    "scripts/evaluate_frozen_loop_cgm_logistic_on_jaeb.py",
    "audit/dclp3_frozen_loop_cgm_logistic_transfer_raw_20261031_v3.json",
    "audit/dclp5_frozen_loop_cgm_logistic_transfer_raw_20261031_v3.json",
    "audit/dclp5_frozen_loop_cgm_logistic_transfer_adjusted_20261031_v3.json",
    "scripts/audit_jaeb_temporal_coverage.py",
    "audit/novelty_recomputation_check_20261031.json",
    "audit/loop_graph_vs_aligned_nongraph_seed20261030_five_fold_summary.json",
    "audit/loop_graph_vs_aligned_nongraph_two_seed_five_fold_participant_summary.json",
    "manuscript/manuscript.md",
    "manuscript/manuscript.docx",
    "manuscript/manuscript.pdf",
    "manuscript/references.bib",
    "manuscript/results_snapshot.csv",
    "manuscript/evidence_map.json",
    "manuscript/verification.json",
    "manuscript/manuscript_template.md",
    "manuscript/build_manuscript.py",
    "scripts/audit_novelty_evidence_bundle.py",
    "scripts/summarize_graph_aligned_nongraph_folds.py",
    "scripts/summarize_two_seed_graph_aligned_control.py",
    "scripts/build_novelty_review_package.py",
}


def reject_private_or_holdout_content(value, path: str) -> None:
    if isinstance(value, dict):
        if value.get("locked_holdout_used") is True:
            raise ValueError(f"refusing to package holdout-derived audit: {path}")
        if value.get("identifiers_emitted") is True:
            raise ValueError(f"refusing to package identifier-emitting audit: {path}")
        for child in value.values():
            reject_private_or_holdout_content(child, path)
    elif isinstance(value, list):
        for child in value:
            reject_private_or_holdout_content(child, path)


def package_readme() -> str:
    return """# Novelty evidence package (31 October 2026)

This archive contains the current novelty report, focused primary-source
review, audit-correction note, query-documented literature search and matrix,
experiment protocol, linked aggregate audits, independent recomputation
receipt, current manuscript draft in Markdown/DOCX/PDF formats, and scripts used to audit or regenerate
the key summaries and manuscript.

## Main conclusion

Broad novelty for a patient-centric/temporal knowledge graph, graph
hypoglycemia prediction, T1D graph-versus-sequence modeling, or insulin/meal
event context is not supported. In the completed two-seed, five-fold,
two-epoch Loop development comparison, same-input, same-timing, exactly
parameter-matched time-bin pooling outperformed the tested graph
message-passing model on participant-macro AP in all ten fits. The
participant-level paired summary averages each person's difference over the
two fixed seeds. Its intervals condition on saved predictions and do not
quantify refit, seed, or cohort uncertainty.

A separate predeclared eight-epoch CPU pair on outer-0 at one additional seed
also slightly favored aligned pooling. The gap was much smaller than in the
two-epoch multi-fold aggregate. This one-fold schedule-sensitivity result
does not establish convergence or training-seed stability; its protocol and
paired audit are included.

The local DCLP3 and DCLP5 releases pass a strict window-eligibility screen:
7,930,123 post-randomization DCLP3 windows (168 participants; 3.05% positive)
and 5,113,177 numeric-only DCLP5 windows (100 participants; 3.29% positive)
have 120 minutes of continuous CGM history and a fully observed 30-minute
future. Many windows contain both basal and bolus records in their prior
120-minute occurrence-time lookback. DCLP5 low-sentinel handling is separately
reported. These are feasibility counts, not model results or external
validation. The follow-up source-field screen found nonnegative numeric basal
and bolus values; local Jaeb documentation describes basal rows as new-rate
changes and DCLP5 boluses as amounts actually delivered. The DCLP5 glossary
field name differs from its released bolus column. Raw-to-adjusted timestamp
string deltas are often many hours, and a small number exceed 24 hours
substantially; the current strict-window and overlap counts are conditional on
the selected adjusted-time policy and must be recomputed after clock review.
Units, zero-rate meaning, cross-release clock equivalence, extended-bolus
mapping, event availability, and transfer parity remain unresolved; neither
screened release has nonempty carbohydrate values in the selected tables. In
DCLP5, preferring adjusted CGM times adds 9,981 eligible windows and 286
positive labels relative to raw CGM times; the earlier screen mixed raw CGM
and adjusted-preferred pump-event times. The audit package includes raw/raw,
mixed-policy, and adjusted/adjusted aggregate results for DCLP5 plus a DCLP3
raw/raw versus raw/adjusted comparison. These are sensitivity analyses; they
do not adjudicate the correct source clock.

Five frozen two-epoch Loop CGM logistic models were also replayed without
refitting on DCLP3 and DCLP5 CGM-only targets. Each model had higher
participant-macro AP and lower Brier than persistence in DCLP3 raw and DCLP5
raw/adjusted-preferred runs. This is external CGM transfer context only, not
external event-graph validation; folds reuse the same participants and are
not independent replications. Timestamp semantics remain unresolved, and
the target is a release-local future-CGM threshold rather than an adjudicated
clinical episode. See the transfer report and its five-fold aggregate files.

The remaining candidate contribution is a narrowly scoped empirical
comparison for this Loop release, endpoint, and implementation, focused on
raw timestamped insulin/meal transaction alignment to CGM windows. Event-instance
relations themselves are not new: Acharya and Lee (2014) describe temporal
causal relations over diabetic event streams including insulin, glucose and
hypoglycemic symptoms; Li et al. (2020) build event-order KGs and analyze
diabetes logs; Postiglione et al. (2024) use temporal patient KGs for future
disorder prediction. The remaining question is the controlled predictive
comparison, not graph construction. Generic
temporal event graphs with time-indexed visits, medication nodes, and graph
explanations already appear in IJCAI's TRANS work. In addition, a 26 October
arXiv preprint evaluates the same broad any-future-glucose-below-70 endpoint
at 30 minutes with patient-disjoint outer folds, multimodal-versus-sequence
comparisons, and explanation perturbation checks. It does not describe raw
insulin/meal transaction instances or graph relations; it is a preprint with
incomplete implementation detail. A separate 2026 Endocrine Practice TFT
supplement is bibliographically verified but its publisher methods were
inaccessible. The literature matrix contains 70 unique records. Novelty remains provisional. The linked search protocol records query syntax and the important limitation that this was not a native database export or completed PRISMA review.
Dave et al. also compared short-horizon models with and without IOB/COB
context; meal-anchored forecasting and aggregate carbohydrate-on-board
nocturnal models are prior art. None inspected compares the same event
instances under matched graph and non-graph representations. The Dave
abstract/body discrepancy on its 30-minute effect remains unresolved.
MT-HypoNet already reports Loop-based inter-patient
five-fold hypoglycemia forewarning using two-hour histories, with a different
sustained-event definition; do not claim the first Loop forewarning model or
first patient-disjoint Loop evaluation. Tziavaras et al. also report an
interpretable, physiology-informed attention-LSTM using 24-hour CGM, meal,
and insulin histories for nocturnal hypoglycemia risk, with an external
SMARTDIAB evaluation. BG-BERT establishes multimodal forecast-derived
low-glucose evaluation, Sun et al. study future-disturbance-aware sequence
distillation, and PhyNet tests physiological/counterfactual faithfulness.
Oviedo et al. previously studied patient-specific meal/bolus-triggered
postprandial hypoglycemia prediction, and IDMVis established temporal event
sequence visualization for T1D clinical decision support.
Thus event-aware temporal inputs, availability-aware modeling,
physiology-informed prediction, interpretation, and external validation are
prior work. The
focused search is not systematic. Hüni's University of Bern thesis provides
full methods for a related CGM-only LSTM-versus-visibility-GNN predecessor,
including the same 120-minute history, 30-minute any-low horizon family; its
chronological split is within-person, and the graph nodes are CGM readings,
not treatment/meal events. The final Springer chapter is unavailable and
must not be assumed identical to the thesis. Convergence/optimization,
replicated event-disabled controls, measured event availability and
independent explanation evaluation remain open. The DCLP
window screen is feasibility evidence; the separate CGM-only frozen-model
transfer does not resolve event mapping or graph generalization.
The manuscript verification checks 21 paired comparisons, including the
separate eight-epoch outer-0 schedule check.

No locked-holdout model predictions or participant identifiers are included.
The manuscript is a research draft, not a clinically validated model or a
field-wide first claim. The evidence map includes independently regenerated,
byte-matched summaries and hashes of the novelty source documents.
"""


def build(output: Path) -> dict:
    report_path = ROOT / REPORT
    content = report_path.read_text(encoding="utf-8")
    files = set(BASE_FILES)
    for target in re.findall(r"\]\(([^)]+\.json)\)", content):
        if target.startswith("../audit/"):
            path = (report_path.parent / target).resolve()
            if path.is_file():
                files.add(path.relative_to(ROOT).as_posix())
    missing = [name for name in sorted(files) if not (ROOT / name).is_file()]
    if missing:
        raise FileNotFoundError(missing)

    for name in files:
        path = ROOT / name
        if path.suffix == ".json":
            reject_private_or_holdout_content(json.loads(path.read_text()), name)
    readme = package_readme()
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED,
                         compresslevel=6) as archive:
        archive.writestr("README.md", readme)
        manifest = []
        for name in sorted(files):
            payload = (ROOT / name).read_bytes()
            archive.writestr(name, payload)
            manifest.append({"path": name, "bytes": len(payload),
                             "sha256": hashlib.sha256(payload).hexdigest()})
        manifest.insert(0, {
            "path": "README.md", "bytes": len(readme.encode()),
            "sha256": hashlib.sha256(readme.encode()).hexdigest(),
        })
        archive.writestr("MANIFEST.json", json.dumps(
            {"package": "novelty_review_20261031", "files": manifest},
            indent=2, sort_keys=True) + "\n")
    with zipfile.ZipFile(output) as archive:
        corrupt = archive.testzip()
        if corrupt is not None:
            raise zipfile.BadZipFile(f"corrupt package member: {corrupt}")
        names = archive.namelist()
    return {"output": str(output), "bytes": output.stat().st_size,
            "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
            "members": len(names), "integrity": "passed"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(
        "research_outputs/novelty_review_20261031.zip"))
    args = parser.parse_args()
    print(json.dumps(build(args.output), indent=2))


if __name__ == "__main__":
    main()
