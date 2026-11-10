# Primary-source check: attention-augmented TFT hypoglycemia abstract

**Checked:** 31 October 2026  
**Purpose:** Verify a suspected recent title and assess its relevance to the project’s narrow event-relation comparison question.

## Record verification

The title **“Attention-Augmented Temporal Fusion Transformer for Short-Horizon Hypoglycemia Prediction in Type 1 Diabetes”** is a real 2026 record, not merely a generated index entry. Crossref’s Crossmark record identifies the title, *Endocrine Practice*, and DOI [10.1016/j.eprac.2026.03.018](https://doi.org/10.1016/j.eprac.2026.03.018). OpenAlex’s record identifies it as a 2026 article in volume 32, issue 4, supplement, page S336. The DOI resolves to Elsevier’s publisher record, although ScienceDirect returned HTTP 403 during this check.

This appears to be a **one-page conference-supplement abstract**, rather than a full-length journal methods paper. That distinction matters: the record confirms the work exists, but the publisher full text/methods were not accessible for independent verification.

## What can and cannot be established

An abstract transcription hosted on ResearchGate reports use of the T1DiabetesGranada cohort, a 30-minute hypoglycemia forecast, a Temporal Fusion Transformer, and comparisons with glucose-only neural models. It describes cross-signal interactions and reports an AUC advantage over glucose-only methods. The author-linked GitHub repository likewise names T1DiabetesGranada as its dataset and links to the same DOI. These are useful discovery/context sources, **not substitutes for the inaccessible publisher abstract or full paper**; details such as exact inputs, endpoint, partitioning, calibration, and statistical testing remain unverified here.

The verified title and available description make this a close precedent for **short-horizon T1D hypoglycemia forecasting with a multimodal attention model**. It therefore further rules out any broad novelty claim based on combining glucose with other signals, using attention/TFT, or targeting short-horizon hypoglycemia.

The available record does **not** establish a comparison of timestamped event-instance relations against a non-graph model given the same events, information cutoff, temporal alignment, windows, and comparable model capacity. Nor does it establish a temporal knowledge-graph representation. Because the full methods were unavailable, this is an unresolved limitation of the comparison, not evidence that no such design was used.

## Relevance to our claim

The project’s candidate claim should remain narrowly empirical: test whether explicit clinical-event relations improve prediction over strong non-graph controls under matched information, timing, windows, splits, and capacity. This TFT abstract is a necessary comparator in the literature matrix and introduction, but the accessible evidence does not presently collapse that specific comparison gap.

**Recommendation:** add a matrix entry with the publisher DOI and mark method-level screening incomplete pending the full abstract/full text. Do not cite the ResearchGate metrics as verified publisher results unless they are checked against the official supplement.

## Sources

- [Crossref Crossmark record](https://crossmark.crossref.org/dialog?cm_version=v2.0&doi=10.1016%2Fj.eprac.2026.03.018&domain=www.endocrinepractice.org&uri_scheme=https%3A) — DOI/title/journal verification.
- [Publisher DOI record](https://doi.org/10.1016/j.eprac.2026.03.018) — canonical record; page inaccessible to this check (403).
- [OpenAlex bibliographic record](https://openalex.org/W7154979851) — supplement issue/page metadata; secondary index.
- [Author-linked GitHub repository](https://github.com/andrewma91/Attention-Augmented-TFT-for-Hypoglycemia-Prediction-in-Type-1-Diabetes) — code/data description and DOI citation; author attribution could not be independently established from the accessible publisher record.
- [ResearchGate abstract transcription](https://www.researchgate.net/publication/405480656_Attention-Augmented_Temporal_Fusion_Transformer_for_Short-Horizon_Hypoglycemia_Prediction_in_Type_1_Diabetes) — discovery aid only, not treated as primary evidence for reported outcomes.
