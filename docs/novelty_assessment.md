# Novelty assessment and prior-work comparison

Date: 10 September 2026. Decision: proceed with a focused comparative research contribution; do not claim a new algorithm or the first semantic T1D graph. This extends the initial [proposal validation](proposal_validation.md). Search scope and access limits are recorded in the [search log](literature_search_log.md).

## What the additional investigation changed

The original comparison between time-point graphs and semantic patient graphs is too narrow. Relevant work includes patient KGs, patient-similarity graphs, visibility graphs, fixed physiology graphs, continuous-time models and graph explanation diagnostics. The remaining opportunity is a controlled investigation of event-level relations under a clearly defined advance-warning task. The proposed study must explain which aspect produces any gain: more information, individual-event resolution, timing, relational structure, parameter count, or recording assumptions.

This is an inference from the reviewed sources, not evidence that no equivalent study exists. An unreported feature in an abstract is **unknown**, not absent. Published scores below are deliberately not compared across incompatible experiments.

## Closest work

| Study / evidence inspected | Representation and established overlap | Task / evidence limitations | Consequence for our proposal |
|---|---|---|---|
| Daniel Onwuchekwa, Weber & Maleshkova; ESWC 2024 conference PDF, formal chapter online 28 January 2025 | Proposes patient-context KGs, ontology integration, embeddings and temporal semantics. | Conference PDF contains an early research plan and preliminary MIMIC-III example; it does not establish the proposed matched outpatient benchmark. Final chapter full text was not obtained. | Semantic patient-specific hypoglycemia prediction is prior work. Cite the proceedings DOI and distinguish versions. [Conference text](https://2024.eswc-conferences.org/wp-content/uploads/2024/05/77770363.pdf), [publisher record](https://link.springer.com/chapter/10.1007/978-3-031-78955-7_4). |
| Rad et al., 2024; publisher methods/application sections | Patient-centric PHKG, FHIR alignment and diabetes applications. | Prediction application does not establish a matched test of our event-relation contribution. | Patient-centricity, semantic integration and interoperability are not standalone novelty. [Paper](https://www.mdpi.com/2075-4426/14/4/359). |
| HETER, 2023; publisher methods/results | CGM subsequences connected using similarity, graph convolution, attention and recurrent temporal learning. | Mixed T1D/T2D cohort; glucose forecasting. “Heterogeneous” here concerns different CGM series, not necessarily typed clinical event nodes. | Distinguish patient/subsequence similarity from within-person event relations. Graph-plus-GRU and temporal heterogeneity already exist. [Paper, section 2.3](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2023.1225638/full). |
| Hüni, Garcia-Tirado & Riesen; S+SSPR 2024, chapter online 31 January 2025; abstract and author repository | Visibility-graph CGM representation and LSTM/GAT comparison on 37 people with T1D. Repository defines any-low-within-horizon labels. | Full final chapter and implementation-level split audit remain outstanding; repository is not a reproduced result. | Add visibility graphs to the relevant baseline families; the any-low target is established. [Chapter](https://link.springer.com/chapter/10.1007/978-3-031-80507-3_6), [author repository](https://github.com/fabianHueni/cgm-visibility-graph-dataset). |
| Sarwar et al., SysCon 2026; author-uploaded manuscript methods/diagnostics | Fixed modality nodes with physiology-inspired edges, GATv2, node ablation, edge deletion/reinsertion and random controls. | Describes future-step classification from shifted glucose; do not assume equivalence to incident any-low-within-H labels. No reproduction. | A physiology graph and edge-faithfulness analysis are prior work. Compare fixed modality summaries against individual event instances. [Author-uploaded manuscript](https://www.researchgate.net/publication/404642556_Explainable_Multitask_Graph_Network_for_Blood_Glucose_Forecasting_and_Hypoglycemia_Risk_Classification), DOI 10.1109/SysCon66367.2026.11503533. |
| Sarwar et al., JAMIA 2026; PubMed/publisher abstract | Temporal neighborhood graph, GAT-BiGRU, multimodal 30/60-minute prediction and GNNExplainer. | Publisher full-text URL redirects to abstract; full splits, labels, supplements and code remain unverified. | Include temporal-neighborhood comparator; do not infer methodological deficiencies from inaccessible details. [PubMed](https://pubmed.ncbi.nlm.nih.gov/42314749/). |
| Maqsood et al., IEEE Access 2026; institution-hosted accepted manuscript, methods and robustness sections | Neural CDE, event channels, missingness handling, physiology constraints, calibration/risk analysis and attribution. | Reports patient-wise evaluation and missingness/shift experiments; exact comparability requires reproduction. DOI in acceptance footer is 10.1109/ACCESS.2026.3672553; ignore template DOI at top. | Irregular inputs, calibration, missingness robustness and lead-time analysis cannot independently establish novelty. Add a serious irregular-input non-graph comparator. [Accepted manuscript](https://epubl.ktu.edu/object/elaba%3A279147543/279147543.pdf). |

The SysCon manuscript is primary author content hosted on ResearchGate. Its authorship/upload notice and manuscript text were visible; the IEEE DOI resolver failed in this session. This is a disclosed access route, not an independent replication or a claim that every version is identical.

## Adjacent methods that constrain claims

| Existing idea | Evidence | Implication |
|---|---|---|
| Time-aware graph aggregation and dynamic-event learning | [TGAT](https://arxiv.org/abs/2002.07962), [TGN](https://arxiv.org/abs/2006.10637) | Timestamps, inductive inference and temporal attention are established ingredients. |
| Continuous-time heterogeneous graph learning | [CTRL](https://arxiv.org/abs/2405.08013) | Adding heterogeneity to temporal learning is not automatically a new architecture. |
| Event time versus database knowledge time | [Bitemporal property graphs](https://arxiv.org/abs/2111.13499) | The two-time representation is established database methodology. Prediction availability is also not necessarily identical to ingestion time. |
| Missingness masks and time since observations | [GRU-D](https://arxiv.org/abs/1606.01865) | A baseline must receive these signals; their inclusion is not evidence for KG value. |
| Glucose motifs and graph-based relations | [MotifDisco](https://arxiv.org/abs/2409.15219) | A motif-based pivot would require its own comparison; do not simply rename events as motifs and claim novelty. Preprint abstract inspected. |

## Claims we can and cannot make

| Candidate claim | Current judgment |
|---|---|
| First patient-centric semantic KG for T1D hypoglycemia | Reject. |
| First temporal or heterogeneous GNN for glucose prediction | Reject. |
| First physiology-based graph or graph perturbation explanation | Reject. |
| First use of two timestamps, missingness masks or clinical standards | Reject. |
| A controlled study of event-instance resolution, relation typing and information availability for incident hypoglycemia | Defensible research objective. Whether it is a distinct completed contribution depends on methods comparison and empirical results. |
| Relations add predictive information beyond identical raw inputs | Incorrect when relations are deterministic functions of those inputs. Test inductive bias, sample efficiency or robustness instead. |
| Reported paths faithfully explain a prediction | Requires measured fidelity and provenance integrity; cannot be inferred from a diagram. |
| Clinically useful / deployment-ready | Not established by this retrospective project. |

## Recommended direction and alternatives

**Primary direction:** event-instance versus modality-summary representations, tested on identical information and held-out people. Make representation resolution, relation parameterization, timing and model capacity separate experimental factors. The deliverable is a reproducible scientific answer to when the graph helps, with auditable event explanations. Use a modest existing relation-aware encoder initially.

**Conditional extension:** quantify how delayed recording changes the incremental value of event relations and the validity of explanation evidence. Distinguish measured delays from imposed scenarios. This is an extension of the scientific question, not a claim to have invented bitemporal graphs.

**Deferred direction:** physiologically constrained or motif-bottleneck architecture. The reviewed literature makes a superficial architecture combination weak; adding it now would enlarge the proposal without demonstrated need. Revisit only after the baseline study identifies a specific failure and a testable mechanism.

The [refined proposal](refined_proposal.md) and [decisive experiments](decisive_experiments.md) make the recommended direction concrete. No architecture was selected based on test results, and no paper outcome has been assumed.

## Remaining uncertainty

The accessible evidence supports rejecting the original broad novelty claim and specifying a narrower study. It does not certify novelty. Final GAT-BiGRU methods/supplements and final versions of the two Springer chapters remain access-dependent; the semantic dissertation and follow-up literature need deeper screening before manuscript submission. Search did not establish a later completed equivalent study, but incomplete retrieval cannot establish absence. If a directly equivalent benchmark appears, update the question toward reproduction, new data, or a demonstrated limitation rather than defending the original wording.
