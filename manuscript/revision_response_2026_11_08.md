# Internal review response and section-quality ratings

Revision date: 8 November 2026. Empirical cutoff: 31 October 2026. The author requested complete documentation, journal-quality writing, multiple reviewers, ratings and improvement. Three agents independently reviewed reporting standards, methods/statistics and clinical/editorial framing, then reread the revised materials. They worked in a shared AI-assisted workflow; their assessments are not independent human peer review or a guarantee of acceptance.

## 1. Delivered synthesis

The [master research record](../docs/research_master_record_2026_11_08.md) reconstructs each stage from proposal and dataset access through canonicalization, eligibility, metric repair, remote recovery, baseline/event/graph controls, stronger pooling controls, explanation sensitivity, external CGM transfer and the novelty assessment. The [technical supplement](supplementary_methods.md) specifies exact input/model/statistical contracts and a planned-versus-executed ledger. The source inventory indexes the research documents and aggregate audit records; the main manuscript presents the focused argument in a journal-format word budget.

The working format is JAMIA Research and Applications, selected under the user's instruction to exercise judgment. The user supplied Pronab Chandra Roy and Lihui Liu, in that order, with no institutional affiliations. Authorship eligibility, corresponding-author responsibility/email, ethics, funding, interests, contribution roles and patient involvement still require actual author confirmation. The writing does not invent these facts. No model training or reserved-group performance evaluation was undertaken solely to improve the documents.

## 2. Finding-by-finding response

| Finding | Revision made and evidence | Disposition |
|---|---|---|
| The main argument favored the earlier sequence comparison over the stronger control | Rewrote objective, abstract, Results and Discussion around the later pooling comparison; retained sequence result as contextual and explicitly development-informed. | Corrected reporting; prospective specification not claimed. |
| Oversized literature paragraph | Replaced with focused Background/Objective sections; retained full 70-record source review and detailed prior art in the master/supplement. | Corrected readability and traceability. |
| Incorrect feature count | Changed 14 added event features to 14 total features:2 CGM + 12 event-summary variables. Saved audit confirms the actual feature list. | Factual error corrected. |
| Pooling architecture incompletely reported | Added 129→64 fusion,64→2 branch gates,16 channel gains, parameter accounting and no-event behavior. | Architecture documented in main Section 3.4 and Supplement S3. |
| Over-specific message-passing attribution | Explained that pooling changes the CGM-only nonlinear path even without events, and explicit count exposure/fusion differ. | Implementation-level inference retained; factorial mechanism test remains unperformed. |
| Statistical estimand insufficiently explicit | Defined participant-first averaging over two fixed seeds,650 AP / 652 Brier denominators,10,000 resamples and exact bootstrap seeds in S5. | Reporting corrected; fit/selection/seed uncertainty remains excluded. |
| Nested/prespecified interpretation risk | Added protocol/execution register, local-plan versus registration distinction and development-reuse statement. | Accurate exploratory scope. |
| Eight-epoch gap could imply convergence | Stated seed/fold/hardware/source differences; single pair is descriptive schedule follow-up. | No isolated epoch effect, equivalence or convergence claim. |
| Source population versus analytic cohort | Added original Loop context with primary source; retained 919/851/835/652 denominators separately; unavailable analytic demographics/dates marked missing. | Reporting improved; actual characterization remains absent. |
| Missingness/event capture could be overinterpreted | Distinguished record presence, source reporting, zero/mask payloads, unknown values and complete-future selection. | Boundaries retained throughout. |
| AP/Brier could imply warning utility/calibration | Preserved strict sensor target and stated alert/lead-time/calibration requirements separately. | No clinical operating-policy claim. |
| Explanation screen selection reuse | Recorded selection-conditioned deletion/retention evaluation and inadequately matched random controls. | No independent explanation-faithfulness claim. |
| External transfer could imply graph validation | Moved detailed DCLP diagnostics to master/supplement; retained explicit CGM-only, reused-cohort and clock caveats. | No external event/graph claim. |
| Bibliography ordering and unused references | Numeric citations normalized by first mention, missing labels rejected, uncited entries omitted from generated main list; full working bibliography retained. | Machine-verified current references. |
| Stale PDF/README statements | Updated navigation and build instructions; current PDF rebuilt from revised LaTeX and checked separately. | Source/render freshness verified by dossier build. |
| Raw rebuild prerequisites | Documented missing local basal 1/2 tables without restoring/replacing raw data. | Reacquisition prerequisite remains explicit. |
| Incomplete AI disclosure | Added analytical tool assistance in Methods and aligned acknowledgments across local/remote workflows. | Tool-version/date and author verification still require confirmation. |
| Journal formatting | Correct article type, ≤250-word structured abstract, ≤4,000-word main text,3 tables,2 figures,5 keywords, ordered citations, end legends, alt text and double spacing. | Final counts and rendered-file checks recorded in dossier audit. |
| Factual author declarations unavailable | Incorporated supplied names/order/no affiliations; provided a declaration register rather than inferred funding/ethics/interests. | Submission blockers remain author-dependent. |

## 3. Reviewer ratings and meaning

Each reviewer used an anchored 1–5 rubric:1 absent/misleading;2 substantial gaps;3 working draft;4 strong reporting with bounded gaps;5 polished and fully evidenced within the stated scope. Decimal values are intermediate judgments. Scores measure the stated dimension, not acceptance probability. No overall mean is calculated across heterogeneous writing and empirical-evidence scores.

The clinical/editorial review gives these final main-section scores, relative to the original draft:

| Section | Before /5 | Revised /5 |
|---|---:|---:|
| Title | 4.0 | 4.5 |
| Abstract | 3.0 | 4.5 |
| Background/objective | 2.0 | 4.5 |
| Methods/clinical framing | 4.0 | 4.5 |
| Results | 3.5 | 4.5 |
| Discussion | 4.0 | 4.5 |
| Conclusion | 3.5 | 4.5 |
| Clinical terminology | 4.5 | 4.5 |
| Novelty positioning | 3.5 | 4.5 |
| Declarations/author facts | 2.0 | 3.0 |
| Presentation/citations | 3.0 | 4.5 |

The statistical review rated architecture reporting and statistical estimand reporting 4.5/5 after revision, compared with 3.0 and 3.5 before. It independently compared all 21 snapshot rows with their actual paired-audit point estimates, differences and interval endpoints, finding no discrepancy to tolerance 1e−12. It deliberately retained training/optimization 2.5, event/relation robustness 2.5, explanation evidence 2.0 and external validity 2.0, because writing did not add new experiments. It rated the master record, supplementary methods and readiness transparency 4.5 for documentation within the exploratory scope.

The reporting reviewer found main-section reporting generally 4.4–4.7 after revision, while cohort characterization and declarations remained constrained. Each complete rating table and its limitations is available in the original review file. Earlier pass counts/wording are historical snapshots; the dossier audit gives the final packaged counts.

Sources: [clinical/editorial review](reviews/clinical_editor_review_2026_11_08.md), [methods/statistics review](reviews/methods_statistics_review_2026_11_08.md), [reporting-standard review](reviews/reporting_standards_review_2026_11_08.md).

## 4. What remains genuinely incomplete

Internal reviewers accepted the documents as a transparent exploratory research account. They did not approve a clinical model or certify journal submission readiness. Missing author/ethics/data-use facts, actual analytic population characterization, strong optimization/CGM-only controls, independent explanation testing, alert/calibration evaluation and claim-appropriate confirmation remain in the [readiness register](submission_readiness_2026_11_08.md). The target journal may also require editorial resolution of thesis/preprint citation treatment. Relevant prior art must not be suppressed or relabeled to resolve that policy question.

Final delivery checks cover source links, coverage inventory, numeric consistency, bibliography, figure/table presence, DOCX structure, PDF text/render freshness, and the package manifest. Such checks establish documentary integrity; they do not remove selection bias or make unperformed work complete.
