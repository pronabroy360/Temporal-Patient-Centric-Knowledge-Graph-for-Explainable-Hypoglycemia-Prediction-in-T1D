# Loop model split coverage

The protected split audit assigned every frozen eligible/known window to one
development outer-test fold or the locked holdout. No participant fell outside
the split.

| Group | Participants | Windows | Positive prevalence |
|---|---:|---:|---:|
| Outer 0 | 127 | 8,193,251 | 3.141% |
| Outer 1 | 130 | 8,885,621 | 3.084% |
| Outer 2 | 141 | 9,386,356 | 2.882% |
| Outer 3 | 124 | 8,395,597 | 2.737% |
| Outer 4 | 130 | 9,167,239 | 2.886% |
| Locked holdout | 183 | 12,347,786 | 3.041% |

Overall prevalence is 2.965% (1,671,803 positives among 56,375,850 windows).
The modest fold variation is expected from patient-level splitting and does not
indicate a class-collapse problem. Model fitting and threshold selection must
remain entirely within the 652 development participants; the 183-person
holdout remains locked until the pipeline is frozen.

Manifest checksum:
`69b41e4acfae7d2afc990c8cd15d8fc3f969784d4e5f6534a9263033d341ad52`.
