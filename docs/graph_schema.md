# Graph schema v0.2

Status: minimal candidate for an as-of-time graph, pending the novelty and dataset audits. This describes a temporal property graph with typed domain relations; a validated RDF/OWL export is a separate deliverable.

Each prediction gets an independent graph G(t). A node or field is admissible only if its event and availability conditions are satisfied by t. Unknown reporting latency is recorded as an assumption. Outcomes live outside G(t). See the [refined proposal](refined_proposal.md) for field-version selection and [decisive experiments](decisive_experiments.md) for endpoint-derived relation controls. Separate field availability from event occurrence; if a later edit changes an earlier value, use the latest version known at t. Do not expose withheld events through a per-event missing flag.

## Nodes

| Node type | Predictive content |
|---|---|
| PatientContext | Available stable attributes and missingness indicators; no learned identity in unseen-patient testing. A constant context token is acceptable when no attributes exist. |
| CGMReading | Glucose, age relative to t, quality mask, causal dynamics shared with baselines. |
| InsulinEvent | Bolus dose or basal rate with subtype and valid interval; no future delivery. |
| MealEvent | Recorded carbohydrate amount and timing; distinguish no record from verified zero intake. |
| ExerciseEvent | Type/intensity if available, elapsed duration; completed duration and summary physiology only after available. |
| ContextEvent | Optional audited context; omit speculative/unrecorded modalities. |

Keep scalar quantities as attributes. Do not create a node for every unit or number. Do not include HypoglycemiaEvent, target classes, outcome-dependent GlycemicState, or label-bearing PredictionWindow nodes in v1 inputs.

## Relations

| Source → target | Relation | Construction |
|---|---|---|
| PatientContext → CGMReading | has_reading | Same participant and admissible history. |
| PatientContext → InsulinEvent | received | Known admissible event only. |
| PatientContext → MealEvent | consumed_record | Recorded admissible event only. |
| PatientContext → ExerciseEvent | activity_record | Known event only. |
| PatientContext → ContextEvent | context_record | Known context only. |
| CGMReading → CGMReading | next_observation | Consecutive historical readings; retain elapsed time and gap mask. |
| InsulinEvent → CGMReading | prior_insulin | Event known by t and event time <= reading time, within configured support. |
| MealEvent → CGMReading | prior_meal | Same temporal rule and provenance. |
| ExerciseEvent → CGMReading | prior_or_active_activity | Relation derived only from admissible interval fields. |

Use elapsed time as an attribute, not dozens of overlapping arbitrary bins. Declare inverse edges explicitly if needed for message passing; their endpoints still lie entirely within G(t). Inverse message edges do not assert reversed clinical causality. Bound neighborhood size deterministically without selecting edges using future glucose.

V1 support is (t−120,t] for point events and readings; include a known interval active within this support even if it began earlier. Log that interval-start history as extra support and provide it to baselines. Longer insulin/activity summaries require a versioned support extension for all models and temporal split purging.

The initial encoder reads graph-updated CGM embeddings in historical order into a GRU and uses its final state for risk. This defines the readout without depending on messages reaching a patient node. A node/edge unit check must show every claimed modality has a path to the readout.

## What this schema can establish

Relations such as prior_insulin and prior_meal may be inferable from node types and timestamps. They test structured inductive bias, not additional observations or established physiological causality. Any proposed meal–bolus pairing needs direct source evidence or a labeled heuristic with its own sensitivity analysis; do not infer a verified treatment relationship from proximity alone.

Required checks: no future timestamps/availability fields; no outcome-dependent edge construction; no cross-patient edges; deterministic topology; no hidden state carried across evaluation partitions; no graph statistics fit on held-out patients; counterfactual future-data edits leave G(t) unchanged.

## Semantic and provenance validation

Keep mapping metadata outside the learned feature vector unless its predictive inclusion is planned. Choose one versioned FHIR release and validate representative examples; do not equate conceptual mapping with full conformance. Review individual glucose terminology separately from aggregate time-in-range terminology.

Use an entity for an observation, an activity for acquisition/transformation and an agent for a device/software actor when applying PROV-O. Example: observation → wasGeneratedBy → acquisition activity → wasAssociatedWith → device agent. Derived features point to their transform and input entities.

Three initial competency queries: retrieve known insulin events preceding a prediction; recover raw provenance for a displayed evidence event; list events excluded because they became available after t. Validate their answers against source records before claiming interoperability or reliable evidence retrieval.
