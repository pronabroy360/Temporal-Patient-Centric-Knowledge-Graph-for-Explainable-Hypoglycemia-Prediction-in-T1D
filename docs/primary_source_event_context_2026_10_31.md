# Primary-source check: event-context hypoglycemia prediction

**Checked:** 31 October 2026  
**Purpose:** Bound what three prior T1D studies establish about meal/insulin context and hypoglycemia prediction. This note supports the project's novelty review; it is not a systematic review.

## Dave et al. (2021): short-horizon event prediction with IOB/COB

Dave et al., “Feature-Based Machine Learning Model for Real-Time Hypoglycemia Prediction,” *Journal of Diabetes Science and Technology* 15(4), 842–855, DOI [10.1177/1932296820922622](https://doi.org/10.1177/1932296820922622), used CGM records from 112 youths with T1D and evaluated <70 mg/dL prediction at 30- and 60-minute horizons. For a subset of 19 participants, it added insulin-on-board (IOB) and carbohydrate-on-board (COB) features to a CGM-feature random-forest model. The paper says the insulin data represented food boluses, omitted basal insulin, and used estimated carbohydrate intake. It therefore establishes prior use of insulin/carbohydrate context in short-horizon T1D hypoglycemia prediction, but not a graph, transaction-level relational representation, or a patient-disjoint evaluation. The accessible methods do not establish that its comparison was matched to our model's information timing or capacity.

**Effect-size caution:** The PubMed abstract says insulin/carbohydrate data improved 60-minute but not 30-minute predictions. The article's results table reports higher sensitivity/specificity for IOB/COB variants across its “within” intervals, and the discussion describes incremental improvement especially at 30–60 minutes; the conclusion specifically summarizes a four-percentage-point improvement at 60 minutes. These statements are not fully aligned. We should cite this paper as evidence that the event-context question has precedent, but should not make a definitive claim that IOB/COB did or did not improve the 30-minute result without reconciling its table, analysis subset, and published corrections.

Primary sources: [publisher full text](https://journals.sagepub.com/doi/10.1177/1932296820922622); [PubMed record and abstract](https://pubmed.ncbi.nlm.nih.gov/32476492/); [2021 erratum](https://doi.org/10.1177/19322968211027985); [corrigendum](https://doi.org/10.1177/19322968211059154).

## Jensen et al. (2020): nocturnal prediction with CGM, meal, and insulin candidate features

Jensen et al., “Prediction of Nocturnal Hypoglycemia From Continuous Glucose Monitoring Data in People With Type 1 Diabetes: A Proof-of-Concept Study,” *Journal of Diabetes Science and Technology* 14(2), 250–256, DOI [10.1177/1932296819868727](https://doi.org/10.1177/1932296819868727), analyzed 4,721 night profiles from 463 people with T1D; 429 profiles had an episode. A profile consisted of a night and three preceding days. The target was at least three consecutive CGM measurements (at least 15 minutes) at or below 54 mg/dL between 00:01 and 05:59. The candidate feature set used CGM, meal, bolus-insulin, and demographic data; 20% of participants were held out for evaluation and 80% used for feature selection/training. A four-feature subset yielded ROC-AUC 0.79, with an example sensitivity/specificity operating point of 75%/70%.

This is prior evidence for participant-level nocturnal hypoglycemia prediction using a dataset with meal/insulin context among candidate inputs. The endpoint is a nighttime severe-low rule, not rolling 30-minute any-low prediction. It is not an event-graph or matched representation study. The full-text discussion explicitly says no meal or bolus feature remained in the final selected subset. The study therefore does not establish an incremental meal/bolus feature effect, despite considering those records during feature construction. The article's conclusion notes basal rates and physical activity as possible additions, which also cautions against treating the study as a comprehensive event model.

Primary sources: [publisher article](https://journals.sagepub.com/doi/10.1177/1932296819868727); [PubMed record](https://pubmed.ncbi.nlm.nih.gov/31390891/); [PMC full-text record](https://pmc.ncbi.nlm.nih.gov/articles/PMC7196854/).

## Vu et al. (2020): large-scale CGM-only nocturnal prediction

Vu et al., “Predicting Nocturnal Hypoglycemia from Continuous Glucose Monitoring Data with Extended Prediction Horizon,” *AMIA Annual Symposium Proceedings* 2019, 874–882 (published in the 2020 collection), PMID [32308884](https://pubmed.ncbi.nlm.nih.gov/32308884/), analyzed more than one million nights from 9,800 people with T1D using MiniMed 530G. At midnight, a random forest predicted nocturnal glucose below 70 mg/dL for at least 15 minutes across a six-hour overnight horizon; the reported overall AUC was 0.84. Features comprised prior sensor-glucose statistics, prior-low event counts, and temporal-location features. Although users could upload carbohydrate logs and insulin boluses, the paper explicitly says those auxiliary data were inconsistent and its modeling objective was prediction solely from CGM. The explored ~1,000-user dataset was sorted by stream time, with the earliest 80% used for training/cross-validation and latest 20% as holdout; participant disjointness is not established by that split description.

This study is a large CGM-only nocturnal comparator, not evidence for meal/insulin event features, a rolling short horizon, or graph relations. It reinforces why a CGM-only baseline is necessary and why its split should not be described as patient-disjoint.

Primary sources: [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC7153099/); [PubMed abstract](https://pubmed.ncbi.nlm.nih.gov/32308884/).

## Implication for this project

The novelty claim must not be that meal or insulin information has never been used for T1D hypoglycemia prediction. Dave directly tested derived IOB/COB context in short-horizon prediction; Jensen used meal and insulin records among candidate features for nocturnal prediction. The narrower, still provisional question is whether **timestamped event instances and explicit event-to-window relations** add value over controls with the same event content, availability time, and model capacity, for this project's rolling incident-low endpoint. Neither of these studies, as inspected, reports that matched relational-representation comparison. Current negative Loop results remain evidence against claiming a graph benefit unless further controlled experiments and replication show otherwise.

