# Temporal Patient-Centric Knowledge Graph for Explainable Hypoglycemia Prediction in Type 1 Diabetes

**Research startup handbook**  
**Prepared:** September 2026  
**Scope:** Only the topic *Temporal Patient-Centric Knowledge Graph for Explainable Hypoglycemia Prediction in Type 1 Diabetes (T1D)*

> **Expanded novelty review — 10 September 2026:** The active proposal is [When Do Temporal Patient Knowledge Graphs Help Hypoglycemia Prediction?](docs/refined_proposal.md). Read the [closest-work comparison](docs/novelty_assessment.md) and [decisive experiments](docs/decisive_experiments.md). The literature matrix contains 21 records. Temporal models, semantic patient KGs, physiology graphs and edge-faithfulness analysis have prior work; the contribution is a controlled test of individual events, relations and information availability. Neither novelty nor predictive benefit has been experimentally established.
>
> **Review update — 10 September 2026:** Start with the [critical validation](docs/proposal_validation.md), [revised protocol](docs/research_protocol.md), and [milestone plan](docs/research_plan.md). These supersede conflicting recommendations below. The researcher has no fixed deadline and prioritizes quality. This handbook remains an idea collection; no dataset audit or modeling results have been completed.
>
> **Key corrections:** Semantic patient-specific hypoglycemia KGs have prior work beyond the 2026 temporal graph paper. The `<70 mg/dL` endpoint includes Level 2 values. The primary advance-warning task excludes currently low/recently unrecovered indices, and incomplete future coverage produces an unknown label. Outcome nodes and future-derived fields must be excluded from input graphs. See the revised protocol for exact rules.

> **Implementation update — 10 September 2026:** A dependency-free synthetic prototype now provides leakage-aware windows, an OhioT1DM-style XML adapter, as-of graph construction, CGM/event/graph smoke comparators, calibration and alert evaluation, participant-cluster bootstrap uncertainty, fold manifests, collection validation, and explanation provenance masks. No patient files have been accessed and no scientific performance result exists. Use the [implementation status](docs/implementation_status.md) and [data-access checklist](docs/data_access_checklist.md) as the active execution record.

---

## 1. Executive summary

### Proposed working title

**T1D-TKG: A Temporal Patient-Centric Knowledge Graph for Explainable Hypoglycemia Prediction in Type 1 Diabetes**

### One-sentence idea

Build a **semantic, patient-specific temporal knowledge graph** from continuous glucose monitoring (CGM), insulin, meals, exercise, physiological signals, and contextual events, then use temporal graph learning to predict **hypoglycemia 30 and 60 minutes ahead** while producing clinically interpretable explanation paths.

### Core research question

> **Does representing a person's multimodal T1D history as a semantic temporal knowledge graph improve hypoglycemia prediction, generalization, and explanation compared with conventional time-series and non-semantic graph models?**

### Why this is worth studying

Hypoglycemia in T1D is not driven by glucose alone. Risk depends on the interaction of:

- recent CGM level and rate of change;
- basal and bolus insulin;
- insulin-on-board;
- meal/carbohydrate intake;
- exercise type/intensity and recency;
- sleep, stress, illness, and time of day;
- individual insulin sensitivity and treatment pattern.

Most predictive pipelines flatten these into a feature vector or time series. A knowledge graph can represent **events, entities, clinical concepts, provenance, and relationships explicitly**, while a temporal model can capture *when* those relationships matter.

The intended contribution is therefore **not merely to turn time points into graph nodes**. It is to build a **patient-centric semantic event graph** with typed clinical relations such as:

```text
Patient --hasReading--> CGMReading
InsulinBolus --administeredTo--> Patient
Meal --consumedBy--> Patient
ExerciseSession --performedBy--> Patient

InsulinBolus --before--> CGMReading
Meal --before--> CGMReading
ExerciseSession --before--> CGMReading

InsulinBolus --contributesTo--> InsulinOnBoard
Meal --contributesTo--> CarbohydrateOnBoard
ExerciseSession --modulates--> GlycemicState

CGMReading --partOfTrajectory--> GlycemicWindow
GlycemicWindow --precedes--> HypoglycemicEvent
```

---

# 2. Critical novelty warning: earlier semantic and temporal graph work overlaps

**Review addition:** [Daniel Onwuchekwa et al., ESWC 2024 PhD Symposium](https://2024.eswc-conferences.org/wp-content/uploads/2024/05/77770363.pdf) also proposes semantic patient-specific KGs for hypoglycemia. Consequently, the semantic/non-semantic distinction below is useful for comparing model families but does not by itself establish novelty. See the [validation review](docs/proposal_validation.md).

Before beginning, you should read:

**Sarwar et al. (2026), “GAT-BiGRU: explainable multi-task temporal graph learning for glucose forecasting, hypoglycemia risk, and counterfactual insulin adjustment,” Journal of the American Medical Informatics Association (JAMIA).**

The accessible abstract reports a temporal GAT-BiGRU model that:

- converts multimodal CGM time series into a **temporal k-neighborhood graph**;
- represents each time point as a feature-enriched node;
- uses graph attention plus a BiGRU;
- predicts glucose trajectories and hypoglycemia risk at **30- and 60-minute horizons**;
- evaluates on **OhioT1DM and BrisT1D**;
- uses **GNNExplainer** for interpretability.

Paper:
https://academic.oup.com/jamia/advance-article-abstract/doi/10.1093/jamia/ocag104/8711207

PubMed:
https://pubmed.ncbi.nlm.nih.gov/42314749/

## What this means for your project

A project framed only as:

> “Use a temporal graph neural network to predict hypoglycemia from CGM + insulin + meals”

is now too close to existing work.

### Your differentiation should be explicit

The proposed **T1D-TKG** should model a **semantic knowledge graph**, not only a graph of neighboring time points.

| Existing temporal graph idea | Proposed patient-centric TKG |
|---|---|
| Time point = node | Clinical event/entity = typed node |
| Neighboring time points = edges | Clinical + temporal + patient-specific relations |
| Mostly numerical temporal graph | Semantic heterogeneous graph |
| CGM window represented geometrically | CGM, insulin, meal, activity, sleep, context represented as entities/events |
| GNN explanation | Graph paths + relation-level explanations + optional GNN explanation |
| Graph structure derived mainly from time | Graph structure derived from clinical semantics **and** time |
| Prediction focus | Prediction + semantic reasoning + provenance-aware explanation |
| Limited interoperability | Schema can map to FHIR/LOINC/standard temporal vocabularies |

This distinction should appear in the title, introduction, contribution statement, architecture diagram, ablation study, and discussion.

---

# 3. Refined research objective

## Primary objective

Develop and evaluate a **patient-centric temporal knowledge graph framework** that integrates multimodal T1D events and predicts upcoming hypoglycemia while providing faithful, patient-specific explanations.

## Secondary objectives

1. Construct a reusable ontology/schema for patient-level T1D temporal data.
2. Determine whether semantic graph relations improve prediction beyond time-series features alone.
3. Determine whether patient-specific subgraphs improve generalization across patients.
4. Compare graph-based explanations with conventional feature-attribution methods.
5. Test whether the model generalizes to an external T1D dataset.
6. Quantify which event types—insulin, meals, exercise, CGM dynamics, physiological context—contribute most.
7. Assess performance separately for Level-1 and, if sample size permits, Level-2 hypoglycemia.

---

# 4. Clinical target and labels

Use the **ADA Standards of Care in Diabetes—2026** definitions.

- **Level 1 hypoglycemia:** glucose `<70 mg/dL` and `>=54 mg/dL`.
- **Level 2 hypoglycemia:** glucose `<54 mg/dL`.
- **Level 3 hypoglycemia:** a severe clinical event requiring assistance, irrespective of glucose value.

Source:
https://diabetesjournals.org/care/article/49/Supplement_1/S132/163927/6-Glycemic-Goals-Hypoglycemia-and-Hyperglycemic

For a first ML study, the safest primary endpoint is:

> **Will the patient experience CGM glucose <70 mg/dL within the next H minutes?**

where:

- `H = 30 minutes`;
- `H = 60 minutes`.

### Recommended primary label

At an eligible non-low index time \(t\), apply the coverage and recovery rules in the [revised protocol](docs/research_protocol.md):

```text
y(t,H) = unknown if required future CGM coverage is incomplete;
otherwise 1 if any valid future CGM in (t, t+H] is <70 mg/dL;
otherwise 0.
```

This is a CGM-defined threshold-crossing endpoint, including Level 2 values. Sustained-episode detection is a separate secondary evaluation.

### Recommended secondary labels

- Level-2 event: `<54 mg/dL`.
- Sustained hypoglycemia: values below threshold for a chosen minimum duration.
- Minimum future glucose within 30/60 minutes.
- Time-to-hypoglycemia.
- Future glucose regression at +30/+60 minutes.

Do **not** make all these primary tasks initially. Start with binary CGM-defined hypoglycemia prediction and add secondary analyses after the pipeline is reliable.

---

# 5. Precise research questions

## RQ1 — Predictive value

**Does a semantic temporal knowledge graph improve 30- and 60-minute hypoglycemia prediction compared with tabular and sequence models?**

## RQ2 — Semantic value

**Does explicitly encoding relations among insulin, meals, activity, CGM, and patient context provide value beyond simply placing the same variables in a temporal feature vector?**

This is one of the most important questions because it validates the *knowledge graph contribution*.

## RQ3 — Personalization

**Does incorporating patient-specific historical context improve prediction for unseen or sparsely observed patients?**

## RQ4 — Explainability

**Can the graph produce clinically plausible explanation paths for an individual prediction while maintaining measurable fidelity to the predictive model?**

## RQ5 — Generalization

**Does the learned representation generalize across datasets, devices, treatment modalities, or unseen patients?**

## RQ6 — Event importance

**Which combinations of recent insulin, carbohydrate, exercise, glucose trajectory, and contextual signals are most associated with future hypoglycemia?**

---

# 6. Testable hypotheses

### H1

A temporal heterogeneous KG model will achieve higher **PR-AUC** than non-graph baselines for 30/60-minute hypoglycemia prediction.

### H2

Removing semantic relation types will reduce performance, demonstrating that the graph contributes information beyond raw temporal ordering.

### H3

Adding insulin and meal event nodes will improve prediction over CGM-only graphs.

### H4

Adding exercise/physiological context will provide additional benefit, particularly for post-exercise risk.

### H5

Patient-aware embeddings or personalization will improve per-patient calibration and recall compared with a single global model.

### H6

Explanation paths derived from the semantic graph will be more understandable to domain reviewers than raw feature-attribution scores alone.

---

# 7. What exactly is a “Temporal Patient-Centric Knowledge Graph”?

A useful operational definition for this project is:

> A heterogeneous graph in which a **Patient** is linked to time-stamped observations, treatment events, behavioral events, physiological states, derived glycemic states, and outcomes using typed semantic and temporal relations.

Formally, a temporal KG can be represented as time-aware facts:

\[
(s, r, o, \tau)
\]

where:

- \(s\) = subject node;
- \(r\) = relation;
- \(o\) = object node;
- \(\tau\) = timestamp or interval.

Example:

```text
(InsulinBolus_8291, administeredTo, Patient_559, 08:15)
(Meal_391, consumedBy, Patient_559, 08:30)
(Meal_391, containsCarbohydrate, Carb_45g, 08:30)
(Exercise_410, performedBy, Patient_559, 09:40-10:10)
(CGM_921, observedFor, Patient_559, 10:20)
(CGM_921, hasGlucoseValue, 76mg/dL, 10:20)
(CGM_921, precedes, Hypoglycemia_62, +30min)
```

---

# 8. Proposed ontology / graph schema

Do not make the ontology enormous in version 1. The graph must be useful for the prediction experiment.

## 8.1 Core node types

### Patient

Possible properties:

```yaml
patient_id:
sex:
age_group:
diabetes_duration:
therapy_type:
pump_type:
cgm_device:
baseline_hba1c:
insulin_carb_ratio:
insulin_sensitivity_factor:
```

Only use fields actually available in the chosen dataset.

### CGMReading

```yaml
reading_id:
timestamp:
glucose_mg_dl:
rate_of_change:
rolling_mean_15m:
rolling_mean_30m:
rolling_std_30m:
trend_category:
source_device:
quality_flag:
```

### InsulinEvent

Subtypes:

- BolusInsulin
- BasalInsulin
- TemporaryBasal
- CorrectionBolus
- MealBolus

Possible properties:

```yaml
timestamp:
dose_units:
rate_units_per_hour:
insulin_type:
delivery_mode:
```

### MealEvent

```yaml
timestamp:
carbohydrate_g:
meal_type:
estimated_or_measured:
```

### ExerciseEvent

```yaml
start_time:
end_time:
activity_type:
intensity:
duration_minutes:
heart_rate_mean:
heart_rate_peak:
```

### PhysiologicalObservation

Examples:

- HeartRate
- Steps
- SkinTemperature
- GSR
- Acceleration

### ContextEvent

Examples:

- Sleep
- Stress
- Illness
- Work
- TimeOfDay
- DayOfWeek

### GlycemicState

Derived state at time \(t\), e.g.:

- Stable
- Rising
- Falling
- RapidlyFalling
- InRange
- Hypoglycemic
- Hyperglycemic

### HypoglycemiaEvent

```yaml
start_time:
end_time:
minimum_glucose:
severity_level:
duration_minutes:
```

### PredictionWindow

Useful for model bookkeeping:

```yaml
index_time:
history_start:
prediction_horizon:
label:
```

---

# 9. Recommended relation types

## Patient relations

```text
Patient --hasReading--> CGMReading
Patient --received--> InsulinEvent
Patient --consumed--> MealEvent
Patient --performed--> ExerciseEvent
Patient --hasPhysiology--> PhysiologicalObservation
Patient --experienced--> HypoglycemiaEvent
```

## Event relations

```text
MealEvent --contains--> CarbohydrateAmount
InsulinEvent --hasDose--> Dose
ExerciseEvent --hasType--> ExerciseType
ExerciseEvent --hasIntensity--> Intensity
CGMReading --hasState--> GlycemicState
```

## Temporal relations

```text
eventA --before--> eventB
eventA --after--> eventB
eventA --overlaps--> eventB
eventA --during--> interval
eventA --within_30m_before--> eventB
eventA --within_60m_before--> eventB
eventA --within_120m_before--> eventB
```

For a standards-aware implementation, consider the W3C **OWL-Time** vocabulary, which defines temporal instants, intervals, and relations such as before, after, during, contains, overlaps, starts, and finishes.

Source:
https://www.w3.org/TR/owl-time/

## Derived physiological relations

Be conservative here. These should be computational/observational, not falsely causal.

Prefer:

```text
InsulinEvent --temporallyAssociatedWith--> GlucoseChange
MealEvent --temporallyAssociatedWith--> GlucoseChange
ExerciseEvent --temporallyAssociatedWith--> GlucoseChange
```

Avoid asserting:

```text
X --causes--> Hypoglycemia
```

unless causality has actually been established.

---

# 10. Example patient subgraph

At 18:00:

```text
Patient_559
    |
    +--hasReading--> CGM_1800 [88 mg/dL]
    |
    +--received----> Bolus_1630 [3.0 U]
    |
    +--consumed----> Meal_1640 [35 g carbohydrate]
    |
    +--performed---> Exercise_1720_1750
                         |
                         +--type------> Aerobic
                         +--duration--> 30 min
```

Temporal structure:

```text
Bolus_1630 --------before-------> CGM_1800
Meal_1640 ---------before-------> CGM_1800
Exercise_1720_1750-before-------> CGM_1800

CGM_1745 --> CGM_1750 --> CGM_1755 --> CGM_1800
    105         99          93          88
```

Derived features:

```text
CGM_1800 --hasTrend--> Falling
Bolus_1630 --contributesTo--> EstimatedIOB_1800
Meal_1640  --contributesTo--> EstimatedCOB_1800
```

Prediction:

```text
PredictionWindow_1800
    --usesContext--> PatientSubgraph_[16:00,18:00]
    --predicts-----> HypoglycemiaWithin60Min
```

Possible explanation:

```text
Recent bolus
   -> residual insulin estimate
   -> falling glucose trajectory
   -> recent aerobic activity
   -> predicted hypoglycemia risk
```

The explanation must be phrased as a **model explanation/association**, not a clinical diagnosis or dosing recommendation.

---

# 11. Interoperability choices

You do not need full clinical interoperability for the first experiment, but mapping the schema to recognized standards strengthens the methodology.

## FHIR

Useful mappings include:

- CGM/physiological measurements → **FHIR Observation**
- insulin administration → **FHIR MedicationAdministration**
- patient → **FHIR Patient**
- food intake, if using FHIR R5 → **FHIR NutritionIntake**
- device → **FHIR Device**

FHIR Observation:
https://hl7.org/fhir/R4/observation.html

FHIR MedicationAdministration:
https://www.hl7.org/fhir/R4/medicationadministration.html

FHIR R5 NutritionIntake:
https://hl7.org/fhir/R5/nutritionintake.html

## LOINC

LOINC provides standardized codes for laboratory and clinical measurements, including CGM-related concepts.

Aggregate example only:
https://loinc.org/97510-2

This code describes the proportion of glucose measurements in range, not an individual CGM glucose concentration. Review a separate code for individual observations.

## OWL-Time

Use for temporal concepts and relations.

https://www.w3.org/TR/owl-time/

## PROV-O

Useful if you want provenance such as:

```text
CGMReading --wasGeneratedBy--> DexcomDevice
DerivedFeature --wasGeneratedBy--> PreprocessingPipeline_v1
Prediction --wasGeneratedBy--> ModelCheckpoint_17
```

W3C PROV-O:
https://www.w3.org/TR/prov-o/

### Recommendation

For the first publication:

1. Define a **small domain schema**.
2. Map its concepts to FHIR/LOINC where reasonable.
3. Use OWL-Time-like temporal relations.
4. Keep provenance metadata.
5. Do not spend months building a complete diabetes ontology before training a model.

---

# 12. Dataset strategy

## 12.1 OhioT1DM — best starting dataset

**Recommended role:** prototype + reproducible main experiment.

The OhioT1DM dataset contains approximately eight weeks of data for each of 12 people with T1D. It includes:

- CGM every 5 minutes;
- finger-stick glucose;
- basal insulin;
- bolus insulin;
- meals/carbohydrate estimates;
- exercise;
- sleep;
- work;
- stress;
- illness;
- physiological wearable data for some participants.

Dataset description:
https://pmc.ncbi.nlm.nih.gov/articles/PMC7881904/

Current access page:
https://webpages.charlotte.edu/rbunescu/ohiot1dm.html

**Important:** the current access page states that the old server was taken down and researchers should complete a Data Use Agreement and contact the listed coordinator to obtain the data.

### Strengths

- extremely relevant feature set;
- 5-minute CGM resolution;
- widely used benchmark;
- appropriate for multimodal event graph construction;
- manageable size for a laptop/Kaggle environment.

### Weaknesses

- only 12 patients;
- substantial missingness;
- device/patient heterogeneity;
- self-reported event noise;
- high risk of overfitting;
- not enough for strong claims without patient-level validation.

---

## 12.2 T1DEXI — strongest external/personalization dataset

**Recommended role:** external validation and exercise-aware extension.

T1DEXI is a real-world T1D exercise study. Published analyses include **497 adults with sufficient CGM data**, with information including:

- CGM;
- structured and non-structured exercise;
- food intake;
- insulin dosing;
- pump data where relevant;
- heart rate.

Study:
https://pmc.ncbi.nlm.nih.gov/articles/PMC10090894/

Public dataset directory:
https://public.jaeb.org/datasets/diabetes

A review of public CGM datasets:
https://pmc.ncbi.nlm.nih.gov/articles/PMC10658693/

### Strengths

- hundreds of participants;
- excellent for unseen-patient testing;
- strong exercise component;
- multiple insulin delivery modalities;
- real-world observations.

### Weaknesses

- data harmonization is harder;
- missingness and device differences;
- access/processing is more involved than a small benchmark;
- graph schema must handle treatment modality variation.

### Recommended strategy

Do **not** wait to understand T1DEXI before building anything.

Start with OhioT1DM, freeze the graph specification, then adapt it to T1DEXI for external validation.

---

## 12.3 D1NAMO — optional physiological extension

The open D1NAMO dataset contains data from 29 participants, including 9 with T1D, and multimodal signals such as:

- glucose;
- ECG;
- breathing;
- accelerometry;
- heart rate-related wearable signals;
- annotated food images.

Repository:
https://github.com/PSI-TAMU/D1NAMO

### Best use in this project

Use only as an optional proof-of-concept showing that the graph can integrate additional physiological modalities.

It is **not** my first choice as the main hypoglycemia-prediction dataset because the T1D sample is small.

---

## 12.4 BrisT1D — useful comparison dataset

BrisT1D contains T1D data involving glucose, insulin, carbohydrate intake, and activity. Publicly visible processed competition descriptions use historical windows to predict glucose one hour ahead.

Example repository/description:
https://github.com/mansoor181/brist1d

Processing information:
https://github.com/SamAJames/brist1d_processing

It is especially important because the 2026 JAMIA GAT-BiGRU paper reports results on BrisT1D.

---

# 13. Recommended dataset sequence

```text
Stage 1
OhioT1DM
   ↓
Build complete preprocessing + KG + baseline pipeline
   ↓
Stage 2
Patient-level cross-validation / leave-one-subject-out
   ↓
Stage 3
T1DEXI
   ↓
Map into same semantic schema
   ↓
Stage 4
External validation / transfer learning
```

If dataset access slows you down, build and test the software architecture using a tiny synthetic event dataset first, then substitute the real data.

---

# 14. Data representation design

## 14.1 Do not create a node for every scalar if it explodes the graph

Bad design:

```text
CGMReading -> ValueNode -> 117
CGMReading -> UnitNode -> mg/dL
```

for millions of readings.

Better:

```text
(:CGMReading {
    glucose: 117,
    unit: "mg/dL",
    timestamp: ...
})
```

Use nodes for semantically meaningful entities/events and properties for simple scalar values.

## 14.2 Recommended hybrid graph

**Node types**

- Patient
- CGMReading
- InsulinEvent
- MealEvent
- ExerciseEvent
- ContextEvent
- HypoglycemiaEvent
- PredictionWindow

**Optional semantic concept nodes**

- Insulin
- AerobicExercise
- ResistanceExercise
- Hypoglycemia
- T1D
- CGMDevice

This gives both computational efficiency and semantic structure.

---

# 15. Temporal construction strategy

You have three main options.

## Option A — discrete dynamic snapshots

Create one graph snapshot every 5 minutes.

```text
G_t-23, G_t-22, ..., G_t
```

Each snapshot contains:

- patient node;
- recent CGM state;
- active/recent insulin;
- recent meals;
- active/recent exercise;
- contextual variables.

### Pros

- easy to pair with recurrent models;
- fits PyTorch Geometric Temporal;
- straightforward batching.

### Cons

- repeated graph structure;
- can become memory-heavy.

---

## Option B — event-based temporal graph

Keep one event graph and attach timestamps to nodes/edges.

```text
event = (source, relation, target, timestamp)
```

Use a temporal graph network or temporal KG model.

### Pros

- natural for irregular events;
- compact;
- more semantically faithful.

### Cons

- implementation is harder.

---

## Option C — hybrid snapshot + event graph

**Recommended.**

Use a regular 5-minute prediction index for CGM, but attach all relevant event nodes within the historical context window.

For prediction at time \(t\):

```text
History window:
(t - 120 min, t]

Contains:
- 24 CGM grid readings on (t - 120 min, t], including t
- insulin events
- meal events
- exercise/context events
- patient node
```

This graph predicts:

```text
hypoglycemia during:
(t, t + 30 min]
or
(t, t + 60 min]
```

This is manageable and clearly different from a graph consisting only of neighboring time points.

---

# 16. Recommended history windows

Start with:

- **120-minute history**;
- 30-minute prediction horizon;
- 60-minute prediction horizon.

Then perform an ablation:

- 60-minute history;
- 120-minute history;
- 180-minute history;
- 360-minute history.

Do not choose the best history length using the test set.

---

# 17. Data preprocessing pipeline

## Step 1 — patient separation

Never mix rows from different patients before patient identifiers and timestamps are validated.

## Step 2 — time standardization

Convert all sources to:

```text
patient_id
timestamp
event_type
value
unit
source
```

Use one timezone/time reference if timestamps contain timezone information.

## Step 3 — unit normalization

Prefer:

```text
glucose -> mg/dL
insulin -> units
carbohydrate -> grams
duration -> minutes
heart rate -> bpm
```

If glucose is in mmol/L:

\[
mg/dL \approx mmol/L \times 18.0182
\]

Record the original unit and conversion in the data dictionary.

## Step 4 — temporal alignment

For CGM-based prediction, use the CGM sampling grid (commonly 5 min in OhioT1DM).

Events such as insulin and meals should retain their true timestamps and be linked to the appropriate historical window.

Avoid shifting future events backward.

## Step 5 — missing-data analysis

Before imputation, create a report per patient:

```text
% missing CGM
% missing insulin
% missing carbohydrate
% missing activity
longest CGM gap
number of hypo events
number of valid 30-min windows
number of valid 60-min windows
```

## Step 6 — CGM missingness

Do not interpolate through large gaps.

Define a maximum acceptable gap before constructing a prediction window.

Potential rule for initial experiments:

```text
discard window if a large portion of historical CGM is missing
or if future label interval has insufficient CGM coverage
```

The exact threshold should be chosen and documented before test evaluation.

## Step 7 — derive CGM dynamics

Useful features include:

```text
current glucose
delta_5m
delta_10m
delta_15m
slope_15m
slope_30m
rolling_mean_15m
rolling_mean_30m
rolling_std_30m
rolling_min
rolling_max
coefficient_of_variation
time_below_range_recent
time_in_range_recent
```

## Step 8 — insulin-derived variables

If feasible:

```text
recent_bolus_30m
recent_bolus_60m
recent_bolus_120m
basal_rate
cumulative_insulin_2h
estimated_insulin_on_board
time_since_last_bolus
```

**Important:** insulin-on-board requires assumptions about insulin action. Document the model and do not present it as a measured value.

## Step 9 — carbohydrate-derived variables

```text
carbs_30m
carbs_60m
carbs_120m
time_since_last_meal
recent_meal_size
estimated_carbohydrate_on_board
```

Again, COB is a modeled/derived variable.

## Step 10 — activity/context

```text
exercise_active
minutes_since_exercise
exercise_duration
exercise_type
heart_rate_mean
heart_rate_change
step_count
sleep_state
stress_flag
illness_flag
time_of_day
day_of_week
```

---

# 18. Avoiding data leakage

This section is critical.

## Never use future CGM values as input

For an index time \(t\), only information available at or before \(t\) can enter the graph.

## Split by patient where possible

Random row-level splits are dangerous because neighboring windows from the same person are highly correlated.

Preferred evaluations:

### Experiment A — within-dataset generalization

**Leave-one-subject-out (LOSO)** or grouped cross-validation.

### Experiment B — temporal generalization

For each patient:

```text
earlier time -> training
later time   -> validation/test
```

### Experiment C — external generalization

Train on Dataset A, test/adapt on Dataset B.

## Prevent overlapping-window leakage

If adjacent samples share most of the same 2-hour history, a random sample split will produce overly optimistic performance.

Use grouped or temporally separated splits.

## Normalize correctly

Fit scaler/statistics only on training data.

Do not calculate means, standard deviations, imputation statistics, or thresholds using test data.

---

# 19. Class imbalance

Hypoglycemia windows will usually be much rarer than non-hypoglycemia windows.

Do not rely on accuracy.

Consider:

- weighted binary cross entropy;
- focal loss;
- balanced mini-batches;
- controlled negative sampling.

Avoid naive oversampling that causes near-duplicate temporal windows to appear across splits.

---

# 20. Baseline models you should implement

A strong paper needs baselines.

## Baseline 0 — persistence / rule baseline

Examples:

- current glucose threshold;
- linear extrapolation from recent slope;
- “if current glucose is low and falling”.

This shows whether sophisticated ML really adds value.

## Baseline 1 — Logistic Regression

Feature vector from the same historical window.

Useful because it is transparent.

## Baseline 2 — Random Forest or XGBoost

Strong tabular baseline.

## Baseline 3 — LSTM / GRU

Input:

```text
[time, CGM, insulin, carbs, HR, activity, ...]
```

## Baseline 4 — Transformer/Temporal sequence model

Useful modern non-graph comparator.

## Baseline 5 — non-semantic temporal graph

Reproduce the concept of:

```text
time point -> node
adjacent time -> edge
```

as closely as feasible.

This comparison is extremely important.

If your semantic KG beats a basic time-neighborhood graph, your knowledge-graph contribution becomes much more convincing.

---

# 21. Recommended main model

For the first implementation, avoid an excessively exotic temporal KG architecture.

## Model: Heterogeneous Graph Encoder + Temporal Encoder

### Stage A — graph encoder

Use relation-aware message passing:

- R-GCN;
- Heterogeneous Graph Transformer (HGT);
- relation-aware GAT.

Node embeddings:

```text
Patient
CGMReading
InsulinEvent
MealEvent
ExerciseEvent
ContextEvent
```

Relation types are explicitly encoded.

### Stage B — temporal encoding

Possible choices:

- GRU;
- LSTM;
- temporal attention;
- Transformer.

### Stage C — prediction head

```text
z_patient_context(t)
        ↓
MLP
        ↓
P(hypoglycemia within 30 min)
P(hypoglycemia within 60 min)
```

You can implement either:

1. separate models for 30 and 60 min; or
2. one multi-task model with two output heads.

For a first paper, a multi-task version is attractive but not essential.

---

# 22. More advanced temporal model options

After the baseline TKG works, evaluate:

- Temporal Graph Networks (TGN);
- TGAT;
- DyRep-style event modeling;
- recurrent graph convolution;
- HGT with explicit time encodings;
- temporal relational GCN;
- temporal KG embedding methods.

Do not begin by implementing five graph architectures. First establish whether **semantic graph construction itself provides value**.

PyTorch Geometric Temporal documentation:
https://pytorch-geometric-temporal.readthedocs.io/en/latest/

---

# 23. Suggested model architecture

```text
RAW DATA
│
├── CGM
├── insulin
├── meals
├── exercise
├── physiology
└── patient/context
        │
        ▼
EVENT NORMALIZATION
        │
        ▼
T1D SEMANTIC SCHEMA
        │
        ▼
PATIENT TEMPORAL SUBGRAPH
[t - history, t]
        │
        ├── Patient node
        ├── CGM nodes
        ├── Insulin nodes
        ├── Meal nodes
        ├── Exercise nodes
        └── Context nodes
        │
        ▼
RELATION-AWARE GRAPH ENCODER
(R-GCN / HGT / relational GAT)
        │
        ▼
TEMPORAL ENCODER
(GRU / Transformer)
        │
        ▼
PATIENT-CONTEXT EMBEDDING
        │
        ├───────────────┐
        ▼               ▼
30-min risk head    60-min risk head
        │               │
        └───────┬───────┘
                ▼
       EXPLANATION MODULE
                │
        ┌───────┼──────────┐
        ▼       ▼          ▼
relation     event      path-based
importance  importance   explanation
```

---

# 24. Explainability design

A graph project should do more than add SHAP to a neural network.

Use **three layers of explanation**.

## Layer 1 — semantic evidence path

Example:

```text
Prediction_18:00
   <-supportedBy- CGM_18:00 [88]
   <-precededBy-- CGM_17:45 [105]
   <-context------ Exercise_17:20
   <-context------ Bolus_16:30
```

Natural-language rendering:

> The model's elevated risk was primarily associated with a falling recent glucose trajectory, a recent insulin event, and recent exercise.

Do **not** state:

> The insulin caused the hypoglycemia.

unless causality has been established.

## Layer 2 — graph model explanation

Possible approaches:

- GNNExplainer;
- PGExplainer;
- attention analysis, with caution;
- edge masking;
- node/edge perturbation.

## Layer 3 — baseline feature explanation

For XGBoost / RF:

- SHAP.

This allows comparison between:

```text
Feature explanation:
"CGM slope has high SHAP value"

versus

Graph explanation:
"Bolus -> recent patient state <- falling CGM <- exercise context"
```

---

# 25. Explanation evaluation

“Looks reasonable” is not enough.

## Fidelity

Remove the nodes/edges identified as important and measure how much prediction changes.

## Sparsity

How many nodes/edges are required to explain a prediction?

## Stability

Do similar input windows produce similar explanations?

## Relation importance

Measure explanation frequency for:

- CGM temporal edges;
- insulin relations;
- meal relations;
- exercise relations;
- patient/context relations.

## Clinical plausibility

If you can obtain expert review, give clinicians or diabetes researchers anonymized explanations and ask them to rate:

- understandable;
- clinically plausible;
- useful;
- misleading risk.

Even a small structured review can significantly strengthen the paper if performed appropriately and ethically.

---

# 26. Evaluation metrics

Because hypoglycemia is imbalanced, make **PR-AUC** a primary metric.

## Classification

Report:

- PR-AUC;
- ROC-AUC;
- sensitivity / recall;
- specificity;
- precision / PPV;
- F1;
- balanced accuracy;
- MCC;
- false alarms per day if meaningful;
- event detection rate.

## Calibration

Report:

- Brier score;
- calibration curve;
- expected calibration error if appropriate.

A clinically useful risk predictor should not only rank patients/windows correctly; its probabilities should be reasonably calibrated.

## Lead-time evaluation

For actual hypoglycemic events:

```text
How many were predicted:
>= 15 min before?
>= 30 min before?
>= 45 min before?
```

This is more informative than window-level classification alone.

## Optional glucose forecasting metrics

If you add a regression head:

- MAE;
- RMSE;
- MARD.

Do not let glucose forecasting distract from the primary hypoglycemia research question.

---

# 27. Event-level evaluation

Window-level prediction can overcount the same hypoglycemic episode many times.

Create an **event-level evaluation**.

Example:

```text
Hypo episode:
10:15 - 10:45

Was an alert produced during:
09:15 - 10:15?
```

Then report:

- detected episodes;
- missed episodes;
- average lead time;
- false alert burden.

This will make the evaluation much more clinically meaningful.

---

# 28. Recommended experimental design

## Experiment 1 — CGM-only baseline

Input:

```text
CGM history
```

Models:

- logistic/rule;
- XGBoost;
- LSTM.

Purpose:

Establish a reference point.

---

## Experiment 2 — multimodal sequence baseline

Input:

```text
CGM + insulin + carbohydrate + activity/context
```

Models:

- XGBoost;
- LSTM/GRU;
- Transformer.

Purpose:

Test whether multimodality alone improves prediction.

---

## Experiment 3 — time-neighborhood graph

```text
time point -> node
time adjacency -> edge
```

Purpose:

Compare against the 2026-style temporal graph family.

---

## Experiment 4 — semantic TKG

Nodes:

```text
CGM
Insulin
Meal
Exercise
Patient
Context
```

Relations:

```text
hasReading
received
consumed
performed
before
within_X_minutes
```

Purpose:

Main proposed model.

---

## Experiment 5 — semantic TKG + patient personalization

Add:

- patient embedding;
- patient history representation;
- fine-tuning or meta-learning if needed.

Purpose:

Test patient-specific value.

---

## Experiment 6 — external validation

Train/develop on one dataset and evaluate on a second after schema mapping.

Purpose:

Generalization.

---

# 29. Essential ablation studies

Ablations are arguably more important than trying many architectures.

## A0 — full model

```text
CGM + insulin + meals + exercise/context + semantic edges
```

## A1 — remove insulin nodes

Test contribution of insulin.

## A2 — remove meal nodes

Test contribution of carbohydrates.

## A3 — remove exercise nodes

Test activity context.

## A4 — remove patient node/patient embedding

Test personalization.

## A5 — remove semantic relation types

Replace all relations with generic `CONNECTED_TO`.

If performance decreases, this supports the claim that semantics matter.

## A6 — remove graph structure

Flatten node/event information into a temporal vector.

This is perhaps the most important ablation.

## A7 — temporal edges only

Keeps chronology but removes clinical semantic relations.

## A8 — no derived IOB/COB

Determines whether graph relations work without hand-engineered physiological features.

---

# 30. Minimum publishable contribution

Do **not** make the first version too large.

A defensible minimum study is:

1. OhioT1DM preprocessing pipeline.
2. Typed patient-centric temporal event graph.
3. 30- and 60-minute CGM-defined hypoglycemia prediction (<70 mg/dL, including Level 2 values).
4. XGBoost + LSTM baselines.
5. Temporal adjacency graph baseline.
6. One relation-aware graph model.
7. Patient-level validation.
8. Graph-specific ablation.
9. Explanation paths + one graph explainer.
10. External validation if feasible.

Everything else is an extension.

---

# 31. Revised novelty formulation

> This study tests when individual clinical event relations improve advance prediction of CGM-defined hypoglycemia, after controlling for input information, temporal resolution, model capacity and patient separation. It compares semantic event graphs with individual-event sequences, generic event graphs, modality-summary physiology graphs and temporal-neighborhood graphs, and audits whether prediction explanations use only admissible, traceable event evidence.

The intended contribution is a rigorous scientific comparison and reproducible event representation. Generic knowledge graphs, heterogeneous temporal learning, two-time records and graph explanation methods are established ideas. See the [novelty assessment](docs/novelty_assessment.md) for the evidence and the [experiment specification](docs/decisive_experiments.md) for claim boundaries. Do not claim “first” or superiority from this proposal alone.

---

# 32. Literature-search strategy before claiming novelty

Search at minimum:

## PubMed

```text
("type 1 diabetes" OR T1D)
AND
(hypoglycemia OR hypoglycaemia)
AND
("knowledge graph" OR "graph neural network" OR "temporal graph")
```

```text
("continuous glucose monitoring" OR CGM)
AND
hypoglycemia
AND
(prediction OR forecasting)
AND
(explainable OR interpretable)
```

## Google Scholar / Scopus / Web of Science

```text
"type 1 diabetes" "knowledge graph"
"type 1 diabetes" "temporal graph"
"type 1 diabetes" "heterogeneous graph"
"type 1 diabetes" GNN hypoglycemia
"hypoglycemia prediction" graph neural network
"patient-centric knowledge graph" diabetes
"personal health knowledge graph" diabetes
```

## IEEE Xplore

Search:

```text
T1D + glucose prediction + graph
CGM + graph neural network
hypoglycemia + explainable AI
```

Maintain a spreadsheet with:

```text
paper_id
title
year
dataset
n_patients
inputs
prediction_horizon
model
graph_type
semantic_KG?
personalized?
explainability?
external_validation?
metrics
code_available?
gap_for_our_work
```

---

# 33. Priority reading list

## Must-read first

### 1. Sarwar et al., 2026

**GAT-BiGRU: explainable multi-task temporal graph learning for glucose forecasting, hypoglycemia risk, and counterfactual insulin adjustment**

Why:
Direct competitor / closest paper.

https://academic.oup.com/jamia/advance-article-abstract/doi/10.1093/jamia/ocag104/8711207

---

### 2. Rad et al., 2024

**Personalized Diabetes Management with Digital Twins: A Patient-Centric Knowledge Graph Approach**

Why:
Core patient-centric KG design inspiration.

DOI:
https://doi.org/10.3390/jpm14040359

Open full text:
https://pmc.ncbi.nlm.nih.gov/articles/PMC11051158/

---

### 3. Marling & Bunescu, 2020

**The OhioT1DM Dataset for Blood Glucose Level Prediction: Update 2020**

Why:
Understand the main prototype dataset.

https://pmc.ncbi.nlm.nih.gov/articles/PMC7881904/

---

### 4. Riddell/T1DEXI study group literature

**Examining the Acute Glycemic Effects of Different Types of Structured Exercise Sessions in Type 1 Diabetes in a Real-World Setting: The Type 1 Diabetes and Exercise Initiative (T1DEXI)**

Why:
Understand the external validation dataset and activity/glucose interactions.

https://pmc.ncbi.nlm.nih.gov/articles/PMC10090894/

---

### 5. Duckworth et al.

**Explainable Machine Learning for Real-Time Hypoglycemia and Hyperglycemia Prediction and Personalized Control Recommendations**

Why:
Strong explainable non-graph baseline perspective.

DOI:
https://doi.org/10.1177/19322968221103561

Open full text:
https://pmc.ncbi.nlm.nih.gov/articles/PMC10899844/

---

### 6. Cui et al., 2023

**Jointly Predicting Postprandial Hypoglycemia and Hyperglycemia Using Continuous Glucose Monitoring Data in Type 1 Diabetes**

Why:
Relevant event prediction formulation.

DOI:
https://doi.org/10.1109/EMBC40787.2023.10340094

PubMed:
https://pubmed.ncbi.nlm.nih.gov/38082964/

Code:
https://github.com/r-cui/PostprandialHyperHypoPrediction

---

### 7. Moon et al., 2025

**Personalized blood glucose prediction in type 1 diabetes using meta-learning with bidirectional long short term memory-transformer hybrid model**

Why:
Personalization and sequence-model baseline.

https://www.nature.com/articles/s41598-025-13491-5

---

### 8. Explainable cluster-based postprandial prediction study

**Explainable cluster-based learning for prediction of postprandial glycemic events and insulin dose optimization in type 1 diabetes**

Why:
Modern interpretable prediction and personalized clustering.

https://journals.plos.org/digitalhealth/article?id=10.1371/journal.pdig.0000996

---

### 9. ADA Standards of Care—2026, Glycemic Goals and Hypoglycemia

Why:
Clinical label definitions and CGM outcome terminology.

https://diabetesjournals.org/care/article/49/Supplement_1/S132/163927/6-Glycemic-Goals-Hypoglycemia-and-Hyperglycemic

---

### 10. W3C OWL-Time

Why:
Formal temporal ontology vocabulary.

https://www.w3.org/TR/owl-time/

---

### 11. HL7 FHIR Observation

Why:
Clinical measurement representation.

https://hl7.org/fhir/R4/observation.html

---

### 12. HL7 FHIR MedicationAdministration

Why:
Semantic representation of insulin administration.

https://www.hl7.org/fhir/R4/medicationadministration.html

---

### 13. W3C PROV-O

Why:
Provenance model for observations, transformations, and predictions.

https://www.w3.org/TR/prov-o/

---

### 14. PyTorch Geometric Temporal

Why:
Implementation resource for temporal graph learning.

https://pytorch-geometric-temporal.readthedocs.io/en/latest/

---

### 15. Public CGM datasets overview

**Publicly Available Data Set Including Continuous Glucose Monitoring Data**

Why:
Dataset landscape and T1DEXI information.

https://pmc.ncbi.nlm.nih.gov/articles/PMC10658693/

---

# 34. Recommended software stack

## Core

```text
Python 3.11/3.12
pandas
numpy
scikit-learn
PyTorch
PyTorch Geometric
PyTorch Geometric Temporal
```

## Tabular baselines

```text
xgboost
lightgbm (optional)
scikit-learn
```

## Knowledge graph storage

For research modeling, you can initially use:

```text
NetworkX
or
PyTorch Geometric HeteroData
```

For exploration/querying:

```text
Neo4j
```

For RDF/ontology experiments:

```text
rdflib
OWL/RDF
```

### Recommendation

Do **not** require Neo4j during neural training.

Use:

```text
raw data
 -> normalized event tables
 -> semantic graph builder
 -> PyG HeteroData
 -> model
```

Neo4j can be a visualization/query layer, not the training bottleneck.

---

# 35. Suggested repository structure

```text
t1d-tkg/
│
├── README.md
├── pyproject.toml
├── requirements.txt
├── configs/
│   ├── ohiot1dm.yaml
│   ├── t1dexi.yaml
│   └── model.yaml
│
├── data/
│   ├── raw/
│   │   ├── ohiot1dm/
│   │   └── t1dexi/
│   ├── interim/
│   └── processed/
│
├── docs/
│   ├── data_dictionary.md
│   ├── graph_schema.md
│   ├── label_definition.md
│   └── experiment_protocol.md
│
├── src/
│   ├── data/
│   │   ├── load_ohiot1dm.py
│   │   ├── load_t1dexi.py
│   │   ├── normalize_events.py
│   │   └── quality_checks.py
│   │
│   ├── features/
│   │   ├── glucose.py
│   │   ├── insulin.py
│   │   ├── meals.py
│   │   └── activity.py
│   │
│   ├── graph/
│   │   ├── schema.py
│   │   ├── build_patient_graph.py
│   │   ├── build_windows.py
│   │   └── export_pyg.py
│   │
│   ├── models/
│   │   ├── xgboost_baseline.py
│   │   ├── lstm_baseline.py
│   │   ├── temporal_graph_baseline.py
│   │   └── semantic_tkg.py
│   │
│   ├── explain/
│   │   ├── graph_explainer.py
│   │   ├── path_explainer.py
│   │   └── shap_baseline.py
│   │
│   └── evaluation/
│       ├── metrics.py
│       ├── calibration.py
│       ├── event_metrics.py
│       └── bootstrap.py
│
├── notebooks/
│   ├── 01_data_audit.ipynb
│   ├── 02_hypoglycemia_labels.ipynb
│   ├── 03_graph_visualization.ipynb
│   ├── 04_baselines.ipynb
│   └── 05_explanations.ipynb
│
├── scripts/
│   ├── preprocess.py
│   ├── build_graphs.py
│   ├── train.py
│   └── evaluate.py
│
└── results/
    ├── tables/
    ├── figures/
    ├── predictions/
    └── explanations/
```

---

# 36. Minimal graph object design in PyTorch Geometric

Conceptually:

```python
data["patient"].x
data["cgm"].x
data["insulin"].x
data["meal"].x
data["exercise"].x

data["patient", "has_reading", "cgm"].edge_index
data["patient", "received", "insulin"].edge_index
data["patient", "consumed", "meal"].edge_index
data["patient", "performed", "exercise"].edge_index

data["cgm", "next", "cgm"].edge_index
data["insulin", "before", "cgm"].edge_index
data["meal", "before", "cgm"].edge_index
data["exercise", "before", "cgm"].edge_index
```

Edge attributes may contain:

```text
time_difference_minutes
event_recency
edge_confidence
```

Node attributes may contain normalized numerical features.

---

# 37. Pseudocode for generating one prediction graph

```python
for patient in patients:
    timeline = load_patient_events(patient)

    for t in valid_prediction_times(patient):

        history = events_between(
            timeline,
            start=t-history_minutes,
            end=t
        )

        graph = create_graph()

        graph.add_patient(patient)

        for cgm in history.cgm:
            graph.add_cgm(cgm)

        for insulin in history.insulin:
            graph.add_insulin(insulin)

        for meal in history.meals:
            graph.add_meal(meal)

        for exercise in history.exercise:
            graph.add_exercise(exercise)

        add_patient_edges(graph)
        add_temporal_edges(graph)
        add_semantic_edges(graph)

        y30 = future_hypo(patient, t, horizon=30)
        y60 = future_hypo(patient, t, horizon=60)

        save(graph, y30, y60)
```

---

# 38. Edge-construction rules

Make edge creation deterministic and documented.

Example:

```text
CGM_i --next--> CGM_j
if j is the next valid CGM observation.

InsulinEvent --within_120m_before--> CGM_t
if:
0 <= t - insulin_time <= 120 minutes

MealEvent --within_120m_before--> CGM_t
if:
0 <= t - meal_time <= 120 minutes

ExerciseEvent --within_180m_before--> CGM_t
if:
exercise ended <= t
and
t - exercise_end <= 180 minutes
```

Do not choose dozens of arbitrary thresholds without validation.

A cleaner approach is to include `time_difference_minutes` as an edge attribute and let the model learn recency.

---

# 39. Patient personalization strategies

Start simple.

## Strategy 1 — patient node embedding

Each subgraph contains the patient node.

For within-patient evaluation this captures individual context, but for unseen patients a pure learned ID embedding will fail.

## Strategy 2 — patient phenotype features

Encode available stable characteristics:

```text
age group
therapy modality
baseline HbA1c
diabetes duration
insulin sensitivity
ICR
```

if available.

## Strategy 3 — history-derived patient representation

Compute features from the patient's previous days:

```text
mean glucose
glucose variability
TIR
TBR
typical basal
daily insulin
typical meal timing
hypoglycemia frequency
```

This works for unseen patient IDs.

## Strategy 4 — fine-tuning/meta-learning

Only after simpler methods are established.

---

# 40. Loss functions

For binary hypoglycemia prediction:

\[
L = -w_1 y \log(p) - w_0(1-y)\log(1-p)
\]

where class weights compensate for imbalance.

For multi-horizon prediction:

\[
L = \lambda_{30}L_{30} + \lambda_{60}L_{60}
\]

Optional multi-task glucose forecast:

\[
L_{total}
=
\lambda_h L_{hypo}
+
\lambda_g L_{glucose}
\]

Do not add a regression task unless it improves the research question.

---

# 41. Model-selection protocol

1. Fix patient-level test set/splits.
2. Use training patients for training.
3. Tune hyperparameters only on validation patients or training folds.
4. Select threshold on validation data.
5. Evaluate test set once per finalized configuration.
6. Report uncertainty.

Do not repeatedly inspect test performance while changing the graph schema.

---

# 42. Statistical analysis

Recommended:

- patient-level bootstrap confidence intervals;
- paired comparison across identical test windows;
- per-patient metric distributions;
- median + IQR in addition to pooled metrics;
- calibration analysis;
- sensitivity analysis for label/window definitions.

For a small dataset such as OhioT1DM, per-patient results are important.

Do not present dozens of p-values without a preplanned analysis.

---

# 43. Core result tables for the paper

## Table 1 — dataset characteristics

```text
Dataset
Patients
CGM duration
Sampling
Insulin
Meals
Exercise
Physiology
Hypo events
```

## Table 2 — prediction performance

```text
Model
30m PR-AUC
30m ROC-AUC
30m Recall
30m Precision
60m PR-AUC
60m ROC-AUC
60m Recall
60m Precision
```

## Table 3 — ablation

```text
Full TKG
- semantic relation types
- insulin
- meal
- exercise
- patient context
temporal edges only
flat multimodal model
```

## Table 4 — external validation

```text
Train dataset
Test dataset
Model
PR-AUC
Recall
Precision
Calibration
```

## Table 5 — explanation evaluation

```text
Model
Fidelity
Sparsity
Stability
Clinical plausibility
```

---

# 44. Core figures for the paper

1. **Overall T1D-TKG architecture**
2. **Knowledge graph schema**
3. **Example patient temporal subgraph**
4. **Hypoglycemia labeling/window diagram**
5. **PR curves**
6. **Per-patient performance plot**
7. **Calibration plot**
8. **Ablation performance**
9. **Example explanation path**
10. **External validation performance**

---

# 45. Important comparison with the 2026 GAT-BiGRU work

Your paper should have a section similar to:

```text
Temporal Graph:
Time nodes + temporal neighborhood + GAT

vs.

Temporal Knowledge Graph:
Typed patient events
+ semantic clinical relations
+ temporal relations
+ provenance
+ heterogeneous message passing
+ path-based explanation
```

The key experiment:

```text
Same dataset
Same prediction horizon
Same available modalities
Comparable training split

Temporal adjacency graph
        VS
Semantic temporal KG
```

This directly tests your thesis.

---

# 46. Risks and mitigation

## Risk 1 — graph adds no predictive value

This is scientifically possible.

### Mitigation

Make the contribution broader:

- semantic representation;
- interoperability;
- explanation;
- cross-dataset harmonization;
- relation-level ablation.

A negative predictive result can still be informative if rigorously evaluated.

---

## Risk 2 — OhioT1DM is too small

### Mitigation

- LOSO validation;
- strong regularization;
- simpler model;
- T1DEXI external validation;
- report per-patient metrics;
- avoid huge neural architectures.

---

## Risk 3 — severe class imbalance

### Mitigation

- PR-AUC;
- event-level evaluation;
- class-weighted loss;
- calibrated thresholds;
- report false-alert burden.

---

## Risk 4 — missing multimodal events

### Mitigation

- missingness indicators;
- explicit `Unknown/Unavailable` status where appropriate;
- modality ablation;
- avoid assuming missing means zero.

---

## Risk 5 — self-reported meal/exercise noise

### Mitigation

- preserve source/provenance;
- add confidence/data-source property;
- perform sensitivity analysis;
- do not treat self-reports as perfectly accurate.

---

## Risk 6 — misleading explanation

Attention weight is not automatically an explanation.

### Mitigation

Combine:

- graph perturbation;
- GNNExplainer/PGExplainer;
- path-based evidence;
- explanation fidelity tests.

---

## Risk 7 — clinical overclaiming

This is a retrospective research model, not a medical device.

### Mitigation

Avoid:

- insulin dosing recommendations;
- treatment instructions;
- “prevents hypoglycemia” claims;
- causal language without causal methods;
- prospective clinical claims.

Use:

> “retrospective predictive performance”

and

> “model-associated explanatory evidence”.

---

# 47. Ethical and safety considerations

Even when using de-identified public/research data:

- follow dataset DUAs;
- follow institutional ethics/IRB requirements;
- do not attempt re-identification;
- do not publish patient-level identifiable timelines;
- store data securely;
- report subgroup performance if demographic data permit;
- explicitly analyze false-negative risk;
- state that predictions are not intended for clinical use without prospective validation.

A false negative could fail to warn of hypoglycemia; a false positive could create alert burden. Both should be discussed.

---

# 48. Reproducibility requirements

Before serious modeling:

```text
✓ fixed random seeds
✓ environment lock file
✓ dataset checksum/version
✓ preprocessing config
✓ graph schema version
✓ train/val/test patient IDs saved
✓ model config saved
✓ threshold selection recorded
✓ all prediction outputs saved
✓ experiment tracking
```

Possible tools:

```text
MLflow
Weights & Biases
DVC
Git
```

You do not need all of them. Git + config files + saved splits is enough to begin.

---

# 49. Compute requirements

This project does **not** need a large GPU initially.

## CPU/laptop work

Suitable for:

- preprocessing;
- graph construction;
- data audit;
- Neo4j/RDF exploration;
- XGBoost;
- small LSTM;
- graph visualization.

## GPU

Useful for:

- HGT/GAT;
- repeated LOSO experiments;
- hyperparameter search;
- large T1DEXI training.

A Kaggle or modest cloud GPU should be sufficient for the initial model if graph sizes are controlled.

Do not design the methodology around very large models.

---

# 50. Recommended development order

```text
1. Literature matrix
2. Dataset access
3. Data dictionary
4. Data quality audit
5. Hypoglycemia labels
6. Leakage-safe splits
7. CGM-only baseline
8. Multimodal baseline
9. Graph schema
10. Graph builder
11. Graph visualization
12. Temporal adjacency graph baseline
13. Semantic TKG model
14. Ablations
15. Explanations
16. External validation
17. Statistical analysis
18. Paper
```

Do not start by writing the GNN.

---

# 51. 12-week practical research plan

## Week 1 — literature + exact gap

Read the priority papers.

Deliverables:

```text
literature_matrix.csv
research_gap.md
final_research_questions.md
```

Main task:

Determine exactly what the 2026 GAT-BiGRU paper does and does not model.

---

## Week 2 — dataset and data audit

Obtain OhioT1DM.

Produce:

```text
patient summary
missingness table
hypoglycemia event counts
feature availability
timeline visualization
```

---

## Week 3 — labeling + leakage-safe benchmark

Implement:

- 30-minute labels;
- 60-minute labels;
- patient-level splits;
- event-level hypoglycemia detection.

Train:

- rule baseline;
- logistic regression;
- XGBoost.

---

## Week 4 — sequence baselines

Train:

- LSTM/GRU;
- optional Transformer.

Freeze the preprocessing and evaluation protocol.

---

## Week 5 — graph schema

Produce:

```text
graph_schema.md
node_types.yaml
relation_types.yaml
```

Create visual graphs for 5-10 patient windows.

Check for accidental future information.

---

## Week 6 — temporal graph baseline

Implement a graph where:

```text
time point = node
```

This is the non-semantic graph comparator.

---

## Week 7 — semantic TKG v1

Implement heterogeneous nodes and typed relations.

Train one model:

```text
R-GCN + GRU
or
HGT + temporal pooling
```

---

## Week 8 — ablations

Run:

```text
full
no semantic edges
no insulin
no meal
no exercise
no patient context
```

This week decides whether the thesis works.

---

## Week 9 — explainability

Implement:

- GNNExplainer or edge masking;
- path extraction;
- SHAP for XGBoost;
- explanation fidelity.

Produce 10-20 case studies.

---

## Week 10 — T1DEXI mapping

Map external data into the same graph schema.

Measure:

- data-field overlap;
- schema compatibility;
- distribution shift.

---

## Week 11 — external validation

Evaluate:

```text
direct transfer
and/or
limited fine-tuning
```

Compare patient-level results.

---

## Week 12 — paper package

Produce:

```text
final tables
figures
statistical tests
method diagram
draft manuscript
clean repository
reproducibility instructions
```

---

# 52. Your first seven days in detail

## Day 1

Read:

1. 2026 GAT-BiGRU paper/abstract and any available supplementary material.
2. OhioT1DM dataset paper.
3. Patient-centric diabetes KG paper.

Write:

```text
What exists?
What is missing?
What exactly is my graph?
```

## Day 2

Create literature matrix with at least 20 papers.

Classify:

```text
time-series prediction
explainable prediction
graph learning
knowledge graph
personalized diabetes
dataset papers
```

## Day 3

Start OhioT1DM access process.

At the same time, create the code repository and synthetic data format.

## Day 4

Define:

```text
Hypoglycemia threshold
Prediction horizons
History window
Valid sample definition
Missingness rule
```

## Day 5

Write the first graph schema.

Limit it to approximately 6-8 node types and 10-15 useful relation types.

## Day 6

Build one synthetic patient graph and visualize it.

Example:

```text
2 hours of CGM
1 bolus
1 meal
1 exercise event
1 target event
```

## Day 7

Write a two-page research protocol containing:

```text
question
hypothesis
dataset
label
split
baselines
main model
metrics
ablation
novelty
```

Do not move to serious GNN training until this protocol is coherent.

---

# 53. Go/no-go checkpoints

## Checkpoint 1 — after data audit

Continue if:

- enough valid CGM windows exist;
- hypoglycemia events exist for meaningful evaluation;
- event modalities can be temporally aligned.

If not:

- adjust dataset or endpoint before modeling.

## Checkpoint 2 — after baselines

Continue if:

- leakage-free baseline results are stable;
- labeling code is validated.

## Checkpoint 3 — after semantic graph ablation

Strong result:

```text
semantic graph > temporal-only graph
```

Interesting result:

```text
similar predictive performance
but better explanation/generalization
```

Weak result:

```text
graph worse
and explanations unstable
and no external advantage
```

If weak, investigate whether graph design is adding noise rather than useful inductive bias.

---

# 54. Suggested primary paper structure

## Abstract

1. Background
2. Gap
3. Method
4. Datasets
5. Results
6. Conclusion

## 1. Introduction

Discuss:

- T1D hypoglycemia burden;
- multimodal drivers;
- CGM prediction;
- limitations of flat time series;
- recent graph approaches;
- why semantic patient-centric TKG;
- contributions.

## 2. Related work

### 2.1 Hypoglycemia prediction
### 2.2 Personalized glucose forecasting
### 2.3 Explainable ML in T1D
### 2.4 Graph neural networks for glucose prediction
### 2.5 Patient health knowledge graphs
### 2.6 Research gap

## 3. Methods

### 3.1 Datasets
### 3.2 Cohort/sample construction
### 3.3 Outcome definition
### 3.4 Preprocessing
### 3.5 T1D-TKG ontology/schema
### 3.6 Temporal subgraph construction
### 3.7 Models
### 3.8 Explainability
### 3.9 Evaluation
### 3.10 Statistical analysis

## 4. Results

### 4.1 Dataset characteristics
### 4.2 Primary performance
### 4.3 Per-patient results
### 4.4 Ablation
### 4.5 Explainability
### 4.6 External validation

## 5. Discussion

### 5.1 Main findings
### 5.2 Why semantic relations helped/did not help
### 5.3 Clinical interpretation
### 5.4 Generalization
### 5.5 Limitations
### 5.6 Future work

## 6. Conclusion

---

# 55. Revised intended contributions

1. A versioned patient-event representation and benchmark separating event resolution, relation typing, timing and information availability.
2. Controlled evidence about when clinical event relations help beyond matched sequence and graph comparators.
3. Prediction-specific event explanations with input-version provenance and measured fidelity/stability.

These are intended research outputs, not achieved results. A new neural architecture, clinical benefit and a successful publication are not assumed. The [refined proposal](docs/refined_proposal.md) defines the current scope; the older title variants below remain brainstorming options.

---

# 56. Recommended initial research title variants

### Main

**T1D-TKG: A Temporal Patient-Centric Knowledge Graph for Explainable Hypoglycemia Prediction in Type 1 Diabetes**

### More ML-oriented

**Semantic Temporal Graph Learning for Patient-Specific Hypoglycemia Prediction in Type 1 Diabetes**

### More informatics-oriented

**A Patient-Centric Temporal Knowledge Graph for Multimodal and Explainable Hypoglycemia Risk Prediction in Type 1 Diabetes**

### More concise

**Explainable Hypoglycemia Prediction Using Temporal Patient Knowledge Graphs**

---

# 57. One-paragraph problem statement

People with Type 1 Diabetes generate longitudinal multimodal data from continuous glucose monitors, insulin delivery systems, meal records, activity trackers, and contextual events. Although machine-learning systems can use these observations to forecast glucose or predict hypoglycemia, most models represent them as flat tabular or sequential features, limiting their ability to explicitly encode clinically meaningful relationships and to produce relational explanations. This project proposes a patient-centric temporal knowledge graph in which glucose observations, insulin administrations, meals, exercise, physiological context, and hypoglycemic outcomes are modeled as time-stamped typed entities and relations. A relation-aware temporal graph model will use these patient subgraphs to predict hypoglycemia 30 and 60 minutes ahead, and the contribution of semantic structure will be assessed against tabular, sequence, and non-semantic temporal graph baselines using patient-level validation and graph-specific ablation.

---

# 58. Candidate abstract skeleton

**Background:** Predicting hypoglycemia before it occurs could support safer T1D management, but glucose dynamics depend on interactions among insulin, meals, activity, physiology, and individual context. Existing prediction models predominantly encode these observations as flat temporal features, while recent graph-based approaches often derive graph structure from temporal neighborhoods rather than explicit clinical semantics.

**Objective:** To investigate whether a patient-centric temporal knowledge graph can improve hypoglycemia prediction and provide interpretable relation-level evidence.

**Methods:** Multimodal T1D observations are transformed into heterogeneous patient subgraphs containing CGM measurements, insulin administrations, meals, exercise and contextual events connected through typed clinical and temporal relations. A relation-aware graph encoder and temporal model predict CGM-defined hypoglycemia (<70 mg/dL) at 30- and 60-minute horizons. Performance is compared against tabular, recurrent, Transformer, and temporal-adjacency graph baselines using patient-level evaluation. Explanation fidelity and graph ablations test the contribution of semantic entities and relations.

**Results:** *To be filled after experiments.*

**Conclusion:** *To be filled after experiments.*

---

# 59. What NOT to do

Avoid the following project designs:

### “Build a KG from diabetes papers”

That is not this research question.

### “Put CGM rows into Neo4j and call it a knowledge graph”

Storage in a graph database is not automatically a scientific KG contribution.

### “Use GAT on consecutive time points”

That is too close to existing temporal graph work unless semantics are clearly added and tested.

### “Use an LLM to explain predictions”

An LLM-generated story is not necessarily faithful to the model.

### “Randomly split windows”

This can produce severe leakage.

### “Optimize accuracy”

Class imbalance can make accuracy misleading.

### “Recommend insulin dose”

That moves the study toward high-risk clinical decision support and requires much stronger validation.

### “Claim causality”

Association/prediction is not causality.

---

# 60. Definition of success

The project is successful if it demonstrates at least one of these convincingly:

1. **Better hypoglycemia prediction** from semantic graph structure.
2. **Better cross-patient or cross-dataset generalization**.
3. **More faithful/usable explanation** than non-graph models.
4. **A reusable interoperable T1D event representation** demonstrated across multiple datasets.

The strongest publication would demonstrate all four.

---

# 61. Recommended priority order for your research contribution

```text
PRIORITY 1
Rigorous leakage-free hypoglycemia prediction

PRIORITY 2
Demonstrate semantic graph value

PRIORITY 3
Patient-level personalization/generalization

PRIORITY 4
Faithful explanation

PRIORITY 5
Cross-dataset validation

PRIORITY 6
Extra modalities / digital twin / GraphRAG
```

Do not add GraphRAG or an LLM until the core predictive TKG has been validated.

---

# 62. Future extensions after the first paper

These are **not required for version 1**.

## GraphRAG

Allow questions such as:

```text
Which recent events contributed most to this risk score?
```

The LLM should verbalize retrieved graph evidence rather than invent explanations.

## Causal graph layer

Move from:

```text
associatedWith
```

toward causal hypotheses using appropriate causal inference methods.

## Digital twin

Maintain a continuously updated patient graph and simulate state changes.

## Federated temporal graph learning

Train across institutions without centralizing data.

## Multi-horizon risk

Predict:

```text
15 min
30 min
60 min
120 min
```

## Nocturnal hypoglycemia

Create a dedicated sub-study for overnight events.

## Exercise-associated hypoglycemia

Use T1DEXI to study event-specific post-exercise risk.

---

# 63. Immediate action checklist

Start with these tasks.

- [ ] Read Sarwar et al. 2026 carefully.
- [ ] Read the OhioT1DM dataset paper.
- [ ] Read Rad et al. 2024 patient-centric KG paper.
- [ ] Request/download OhioT1DM according to current access instructions.
- [ ] Create `literature_matrix.csv`.
- [ ] Create `data_dictionary.md`.
- [ ] Define 30/60-minute labels.
- [ ] Define patient-level split.
- [ ] Audit hypoglycemia counts per patient.
- [ ] Train XGBoost baseline.
- [ ] Train LSTM baseline.
- [ ] Define v1 graph schema.
- [ ] Build one patient subgraph.
- [ ] Visualize graph.
- [ ] Implement temporal-only graph baseline.
- [ ] Implement semantic TKG.
- [ ] Run semantic-edge ablation.
- [ ] Add graph explanation.
- [ ] Map the schema to T1DEXI.
- [ ] Run external validation.
- [ ] Write the paper from the experiment log rather than from memory.

---

# 64. Suggested first milestone

Your **first real milestone** should not be a GNN.

It should be a table like:

| Patient | Valid days | CGM coverage | Hypo events <70 | Hypo events <54 | Valid 30m windows | Valid 60m windows | Insulin coverage | Meal coverage | Activity coverage |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|

Once you can generate this automatically, you understand the data well enough to begin modeling.

---

# 65. Suggested second milestone

Produce this exact experiment:

```text
Dataset: OhioT1DM
History: 120 min
Horizon: 30 min
Label: future CGM <70 mg/dL
Split: leave-one-subject-out
Features: CGM-only
Models:
    1. persistence/slope rule
    2. logistic regression
    3. XGBoost
    4. LSTM
Metric:
    PR-AUC primary
```

Only after this works should you add the knowledge graph.

---

# 66. Suggested third milestone

Run the decisive KG test:

```text
Model A:
Multimodal LSTM

Model B:
Temporal adjacency graph

Model C:
Semantic T1D-TKG

Same patients
Same windows
Same labels
Same input modalities
Same evaluation protocol
```

Then ablate:

```text
C1 = full semantic relations
C2 = all edges converted to generic relation
C3 = temporal edges only
```

If:

```text
C1 > C2 and C1 > C3
```

you have direct evidence that **relation semantics matter**.

---

# 67. Final recommended research specification

## Title

**T1D-TKG: A Temporal Patient-Centric Knowledge Graph for Explainable Hypoglycemia Prediction in Type 1 Diabetes**

## Population

People with Type 1 Diabetes using CGM.

## Index data

Multimodal longitudinal observations available up to time \(t\).

## Primary outcome

Hypoglycemia `<70 mg/dL` within the next:

- 30 minutes;
- 60 minutes.

## Primary representation

Patient-centric heterogeneous temporal knowledge graph.

## Main model

Relation-aware graph encoder + temporal encoder.

## Baselines

- rule;
- logistic/XGBoost;
- LSTM/GRU;
- Transformer if resources allow;
- temporal adjacency GNN.

## Primary metric

PR-AUC.

## Secondary metrics

ROC-AUC, recall, precision, F1/MCC, specificity, calibration, event detection, lead time.

## Main validation

Patient-level / leave-one-subject-out.

## Main novelty test

Semantic-relation ablation.

## Explainability

Graph paths + perturbation/GNN explainer, with fidelity/stability evaluation.

## Prototype dataset

OhioT1DM.

## External validation

T1DEXI preferred.

## Optional modality extension

D1NAMO or exercise-focused T1DEXI analysis.

## Key methodological rule

**Never allow future information into the graph used at prediction time.**

---

# 68. Key references and resources

1. **American Diabetes Association. Standards of Care in Diabetes—2026: Glycemic Goals, Hypoglycemia, and Hyperglycemic Crises.**  
   https://diabetesjournals.org/care/article/49/Supplement_1/S132/163927/6-Glycemic-Goals-Hypoglycemia-and-Hyperglycemic

2. **Sarwar MA, et al. GAT-BiGRU: explainable multi-task temporal graph learning for glucose forecasting, hypoglycemia risk, and counterfactual insulin adjustment. JAMIA. 2026.**  
   https://academic.oup.com/jamia/advance-article-abstract/doi/10.1093/jamia/ocag104/8711207  
   https://pubmed.ncbi.nlm.nih.gov/42314749/

3. **Rad FS, Hendawi R, Yang X, Li J. Personalized Diabetes Management with Digital Twins: A Patient-Centric Knowledge Graph Approach. J Pers Med. 2024;14(4):359.**  
   https://doi.org/10.3390/jpm14040359  
   https://pmc.ncbi.nlm.nih.gov/articles/PMC11051158/

4. **Marling C, Bunescu R. The OhioT1DM Dataset for Blood Glucose Level Prediction: Update 2020.**  
   https://pmc.ncbi.nlm.nih.gov/articles/PMC7881904/

5. **OhioT1DM current access page.**  
   https://webpages.charlotte.edu/rbunescu/ohiot1dm.html

6. **T1DEXI: Examining the Acute Glycemic Effects of Different Types of Structured Exercise Sessions in Type 1 Diabetes in a Real-World Setting.**  
   https://pmc.ncbi.nlm.nih.gov/articles/PMC10090894/

7. **Jaeb public diabetes dataset directory.**  
   https://public.jaeb.org/datasets/diabetes

8. **Publicly Available Data Set Including Continuous Glucose Monitoring Data.**  
   https://pmc.ncbi.nlm.nih.gov/articles/PMC10658693/

9. **D1NAMO repository.**  
   https://github.com/PSI-TAMU/D1NAMO

10. **Duckworth C, et al. Explainable Machine Learning for Real-Time Hypoglycemia and Hyperglycemia Prediction and Personalized Control Recommendations.**  
    https://pubmed.ncbi.nlm.nih.gov/35695284/  
    https://pmc.ncbi.nlm.nih.gov/articles/PMC10899844/

11. **Cui R, et al. Jointly Predicting Postprandial Hypoglycemia and Hyperglycemia Using Continuous Glucose Monitoring Data in Type 1 Diabetes. EMBC 2023.**  
    https://pubmed.ncbi.nlm.nih.gov/38082964/  
    https://github.com/r-cui/PostprandialHyperHypoPrediction

12. **Moon K, et al. Personalized blood glucose prediction in type 1 diabetes using meta-learning with bidirectional long short term memory-transformer hybrid model. Scientific Reports. 2025.**  
    https://www.nature.com/articles/s41598-025-13491-5

13. **Explainable cluster-based learning for prediction of postprandial glycemic events and insulin dose optimization in type 1 diabetes. PLOS Digital Health.**  
    https://journals.plos.org/digitalhealth/article?id=10.1371/journal.pdig.0000996

14. **W3C Time Ontology in OWL.**  
    https://www.w3.org/TR/owl-time/

15. **W3C PROV-O.**  
    https://www.w3.org/TR/prov-o/

16. **HL7 FHIR Observation.**  
    https://hl7.org/fhir/R4/observation.html

17. **HL7 FHIR MedicationAdministration.**  
    https://www.hl7.org/fhir/R4/medicationadministration.html

18. **FHIR R5 NutritionIntake.**  
    https://hl7.org/fhir/R5/nutritionintake.html

19. **LOINC CGM-related terminology example.**  
    https://loinc.org/97510-2

20. **PyTorch Geometric Temporal.**  
    https://pytorch-geometric-temporal.readthedocs.io/en/latest/

---

# 69. Bottom line

The most defensible version of this project in late 2026 is **not**:

> “Apply a temporal GNN to T1D glucose data.”

That space already contains very close work.

Your stronger thesis is:

> **Represent each person’s glucose, insulin, meals, exercise, physiology, and contextual events as a semantic temporal knowledge graph, then determine experimentally whether typed patient-event relations improve hypoglycemia prediction and provide faithful explanation paths beyond conventional time-series and temporal-neighborhood graph models.**

If the full-vs-generic-edge ablation shows a real improvement and the result generalizes across patients or datasets, the project has a clear scientific story.

---

## Research-use note

This handbook describes a retrospective machine-learning research project. It is **not a clinical decision-support protocol**, should not be used to recommend insulin dosing or treatment, and would require substantially stronger prospective and clinical validation before any real-world medical use.
