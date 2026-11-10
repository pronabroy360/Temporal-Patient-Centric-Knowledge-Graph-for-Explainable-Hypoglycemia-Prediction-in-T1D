# Research manuscript and complete documentation

Documentation revision: 8 November 2026. Empirical/literature cutoff: 31 October 2026. The paper reports exploratory retrospective development comparisons, with the stricter time-aligned pooling comparison presented first. The working journal format is JAMIA Research and Applications. Required author declarations and material research gaps remain explicit; no journal acceptance or submission readiness is certified.

## Start here

- [Main manuscript](manuscript.md), [Word document](manuscript.docx), and [compiled PDF](manuscript.pdf).
- [Complete step-by-step research record](../docs/research_master_record_2026_11_08.md): dataset selection, processing, experiments, corrections, archive recovery, results, novelty and unresolved work.
- [Supplementary methods](supplementary_methods.md): complete architecture, input/label contracts, estimands, development deviations, and external-transfer limits.
- [Submission readiness and author declarations](submission_readiness_2026_11_08.md): evidence-based requirements and missing facts.
- [Independent internal reviews](reviews/): reporting standards, methods/statistics, and clinical/editorial reviews with baseline and revised ratings.
- [Revision response](revision_response_2026_11_08.md): how each material review finding was resolved or why it remains open.
- [Research-document inventory](research_document_inventory.csv): source documents and top-level aggregate audit records, roles, sizes and hashes. Historical documents retain their original dated status.

The reviews were conducted by AI agents sharing a workspace. They are internal review assistance, not independent human peer review, medical assessment, ethics approval or a validated quality score. Section scores must be interpreted alongside unresolved author and empirical requirements.

## Rebuild and evidence scope

Edit manuscript_template.md; build_manuscript.py replaces result placeholders, normalizes numeric citations by first use, creates figures, and writes Markdown/DOCX/LaTeX from aggregate evidence. The full working bibliography remains in references.bib; generated main references include only works cited in the paper. The full 70-record targeted literature matrix and access limitations are in docs/.

From the repository root:

```bash
MPLCONFIGDIR=/private/tmp/t1d-manuscript-matplotlib python3 manuscript/build_manuscript.py
cd manuscript
tectonic --only-cached --keep-logs manuscript.tex
```

The current PDF must be rebuilt after every manuscript change; the dossier builder performs that compilation before packaging. Cached Tectonic, Times New Roman, Matplotlib and NumPy are available in this environment. Other environments must supply equivalent TeX/font dependencies. DOCX generation uses Office Open XML directly. The generic documentation exporter uses the same renderer for the master record and supplement.

The numerical build verifies 21 central paired comparisons and 42 completed-run summaries, and reconciles the two-seed participant summary against independent saved-prediction recomputation receipts. It does not refit all models or independently rerun every historical bootstrap. verification.json records that scope; evidence_map.json fingerprints sources, and results_snapshot.csv preserves full precision. Twenty-one is a count of the central comparison rows, not every historical project fit. The complete study history is in the master record.

The strongest completed comparison is graph versus time-aligned pooling at two epochs across five folds/two seeds, with an additional single-fold eight-epoch CPU pair. Pooling has higher AP in all ten two-epoch fits. The control also changes CGM-only fusion, so this is an implementation comparison, not isolated causal evidence about message passing. The early one-epoch graph-versus-sequence advantage is retained as comparator-dependent evidence.

## Data and artifact boundaries

The 183-person reserved group was excluded from reported model fitting/scoring, but aggregate eligibility and outcome-coverage audits included it. Do not describe all its information as unseen. No clinical utility, first-in-field novelty, independent explanation faithfulness, or external graph validation is established.

Local raw basal files LOOPDeviceBasal1.txt and LOOPDeviceBasal2.txt are currently missing. Reacquiring those source files is required for a complete fresh raw-to-cache reconstruction; cached-input and saved-prediction verification are separate capabilities. Private caches/predictions/checkpoints and temporary event partitions are excluded from the document bundle. Confirm author ethics/data-use declarations and a code license/archive before public release.

The pre-revision manuscript source and rendered artifacts are preserved under archive/2026_10_31/. They are superseded for reading, retained for provenance, and excluded from the current shareable dossier unless explicitly requested.
