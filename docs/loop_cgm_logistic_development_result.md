# Five-fold development CGM logistic result

**Correction notice (15 September 2026):** the shared AP implementation
handled tied scores incorrectly. The AP values below are historical and need
recomputation; Brier scores are not affected by that defect. See the
[correctness review](research_correctness_review.md) before interpreting or
extending these comparisons.

The frozen current-glucose-plus-recent-slope logistic configuration was
evaluated once on each patient-disjoint development-test fold. Aggregation
uses participant weighting for participant-macro AP and window weighting for
the pooled Brier score.

| Model | Participant-macro AP | Pooled Brier |
|---|---:|---:|
| Persistence/slope rule | 0.2251 | 0.0551 |
| Two-feature CGM logistic | 0.4474 | 0.0216 |

The out-of-fold evaluation covers 652 participants, 44,028,064 windows, and
1,296,297 positive labels. Logistic AP by fold ranges from 0.4311 to 0.4584,
which indicates patient-level heterogeneity but a consistent improvement over
the fixed rule in every fold.

This is a development-only benchmark. The 183-person locked holdout is still
unseen. It must remain untouched while the event-aware and graph comparator
specifications are implemented and selected.

Source artifact: `audit/loop_cgm_logistic_development_summary.json`.
