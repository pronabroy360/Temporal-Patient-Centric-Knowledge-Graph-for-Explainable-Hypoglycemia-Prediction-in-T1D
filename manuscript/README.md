# Working manuscript

Evidence snapshot: 20 October 2026. This is a full research-paper draft based on completed project work, with author-dependent declarations left explicit. It is not a submission-ready claim of clinical validation.

Read `manuscript.pdf` or edit `manuscript.docx`. `manuscript.md` is the generated plain-text version; edit `manuscript_template.md` and rebuild to preserve generated results. `manuscript.tex` is an editable LaTeX export. Figures are supplied as PNG, PDF, and SVG. `references.bib` contains the bibliography.

The main results use five MPS folds at seed 20261003 and four completed folds at seed 20261004. The older CUDA pair, typed-routing pilot, and historical event diagnostics are identified separately. The script takes this fixed snapshot; newer audit files are not silently added. It reads aggregate metrics and completed run metadata, not participant predictions or identifiers, and does not train a model or evaluate the reserved final-performance group.

Rebuild from the repository root:

```bash
MPLCONFIGDIR=/private/tmp/t1d-manuscript-matplotlib python3 manuscript/build_manuscript.py
tectonic --only-cached --keep-logs manuscript/manuscript.tex
```

Python's standard library is sufficient for the editable documents and evidence checks; figures additionally use the already available Matplotlib and NumPy packages. PDF compilation requires Tectonic and its cached TeX bundle, plus Times New Roman (available on the current Mac); substitute an installed font in the generated LaTeX on other systems. The Word document is generated directly as Office Open XML and does not require Microsoft Word or python-docx.

Before submission, complete these author decisions and facts:

- Confirm authors, affiliations, corresponding author, contribution roles, funding, interests, and patient/public involvement.
- Supply the local ethics or exemption determination and verify data-use and redistribution terms. Original-study approval is not approval of this secondary analysis.
- Choose a journal and adjust its formatting, word limit, and required reporting checklist. Approve the AI-assistance disclosure under its policy.
- Confirm the exact release citation and an appropriate code archive, environment specification, and license.
- Decide whether to submit this bounded development study or complete a stronger validation package first. Pending work includes second-seed fold 4, more seeds, convergence and stronger baseline comparisons, event/alignment/relation controls, availability/range sensitivities, alert and calibration analyses, explanation fidelity, reserved final-performance evaluation, external validation, and demographic/subgroup characterization.

`evidence_map.json` records file hashes and the validation performed while building the draft. `results_snapshot.csv` retains full-precision numerical results. `verification.json` states the checks and their limits. The manuscript build does not independently recompute the existing bootstrap intervals from raw prediction shards; those are taken from the previously paired audits, checked against local completed-run point estimates. Typed-pilot raw predictions were not confirmed locally. No project training files or existing research results were modified to prepare this package.
