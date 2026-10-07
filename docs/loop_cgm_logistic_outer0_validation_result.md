# Matched CGM logistic validation result: outer 0

The two-feature streaming logistic pilot and persistence/slope rule were
evaluated on the same outer-0 validation group: 130 participants, 8,885,621
windows, and 274,044 positive labels. Training used only the 395 outer-0
training participants; neither the internal development-test group nor locked
holdout was evaluated.

| Model | Participant-macro AP | Brier score |
|---|---:|---:|
| Persistence/slope rule | 0.2251 | 0.0565 |
| Current-glucose plus slope logistic | 0.4570 | 0.0230 |

The logistic improvement is +0.2319 macro AP and −0.0336 Brier on this
development validation set. It establishes that a learned mapping of the same
two CGM inputs is materially stronger than the fixed extrapolation rule. This
is not yet a final model claim: configuration stability must be checked within
development, followed by internal-fold and locked-holdout evaluation only
after model choices are frozen.

Source artifact: `audit/loop_cgm_logistic_outer0_matched_validation.json`.
