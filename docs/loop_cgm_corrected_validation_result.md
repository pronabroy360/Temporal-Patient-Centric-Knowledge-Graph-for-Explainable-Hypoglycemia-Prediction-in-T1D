# Corrected CGM validation and configuration selection

The corrected tied-score AP implementation (`threshold-grouped-ap-v2`) was
used on outer-0 validation. Both candidates passed exact reconciliation with
the frozen window index: 652 development participants, 44,028,064 windows,
and identity hash
`26036d7d3d27c21a4407d15aacd916b98ba598dfded5da319288a74b54a592aa`.

| Candidate | Epochs | Participant-macro AP | Brier score |
|---|---:|---:|---:|
| CGM logistic A | 1 | 0.456594 | 0.022965 |
| CGM logistic B | 2 | 0.457055 | 0.022880 |
| Persistence/slope rule | — | 0.210490 | 0.056535 |
| Training-prevalence probability | — | — | 0.029896 |

AP is defined for all 130 validation participants. Candidate B remains the
selected configuration under the prespecified higher-AP rule. The corrected
logistic AP values are about 0.00043–0.00044 lower than the historical values;
the binary rule AP is about 0.01463 lower. Brier scores are unchanged because
the defect affected AP ranking at tied scores only.

The protected archives contain 130 participant prediction files and 8,885,621
rows for each candidate, plus the fitted model state and run metadata. Archive
coverage matches the public reports. These results validate the corrected
development selection; they are not a final performance estimate.

Sources: `audit/loop_cgm_corrected_epochs1_validation.json`,
`audit/loop_cgm_corrected_epochs2_validation.json`, and
`audit/loop_cgm_corrected_selection.json`.
