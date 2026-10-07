# Corrected five-fold CGM development result

The frozen two-epoch CGM logistic model was evaluated once on each
patient-disjoint development-test fold using corrected threshold-grouped AP.
All runs used the protected verified feature cache and the same model-manifest
checksum.

| Model | AP-defined participants | Participant-macro AP | Pooled Brier |
|---|---:|---:|---:|
| Persistence/slope rule | 650 | 0.209095 | 0.055132 |
| Two-feature CGM logistic | 650 | 0.446938 | 0.021590 |

The evaluation covers all 652 development participants, 44,028,064 windows,
and 1,296,297 positive labels. Two participants had no positive labels, so AP
is undefined for them and the documented AP denominator is 650. They remain
included in Brier and coverage calculations.

CGM logistic AP ranges from 0.430838 to 0.457896 across folds. It exceeds the
rule AP in every fold and has lower Brier in every fold. This establishes the
corrected development CGM reference for matched event and graph comparisons.
It is an exploratory development estimate because shared choices were made on
the development population. It does not authorize evaluation of the locked
holdout.

Source: `audit/loop_cgm_logistic_development_summary_v2.json`. Each fold also
has a protected complete model and participant-prediction archive under
`private/pilot_runs/`.
