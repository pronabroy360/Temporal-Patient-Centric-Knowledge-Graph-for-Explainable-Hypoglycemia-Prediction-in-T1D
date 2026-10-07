# Research correctness review

Review date: 15 September 2026.

**Implementation follow-up:** [corrected pilot recovery](corrected_pilot_recovery.md)
records fixes made after this review. Findings below preserve the original
review evidence; corrected empirical AP results still require new computation.

## Verdict and scope

The direction remains defensible: determine when event relations improve
prediction under matched information, timing, capacity and evaluation. The
repository has reached data preparation and development baseline evaluation;
it has not demonstrated a graph benefit. This review inspected the protocol,
decisive experiments, actual protected manifest (aggregate checks only),
metric implementation, logistic runners and result aggregation. It did not
reprocess the 111-million-row release, independently reproduce training, or
renew the literature search. Novelty remains provisional.

## Confirmed strengths

- The actual model manifest contains 652 development and 183 holdout
  participants, with no intersection. Every fold covers the development set.
  Its checksum matches the reported
  `69b41e4acfae7d2afc990c8cd15d8fc3f969784d4e5f6534a9263033d341ad52`.
- Model fitting receives training participants only and computes feature
  standardization from training rows. Participant separation avoids sharing
  overlapping windows from the same person between groups within a fold.
- Missing future labels are not treated as negatives. The primary endpoint is
  an observed threshold crossing, explicitly distinguished from a confirmed
  sustained episode.
- The planned generic-edge, endpoint-type/time and event-sequence controls
  directly address the research question. Their implementation and empirical
  evaluation remain outstanding.

## Findings requiring correction or restricted interpretation

### 1. Existing AP values require recomputation — confirmed metric defect

`average_precision` previously ranked equal scores in their input order.
For labels `[1,0]` and scores `[0.5,0.5]`, it returned 1.0; reversing the
labels returned 0.5. Standard threshold-based AP is 0.5 in both cases.
This particularly affects the binary persistence rule, and may also affect
logistic predictions with ties. The shared metric now groups tied scores;
four regression tests were added and all 73 tests pass.

Treat all previously recorded AP values, including the 0.4474 versus 0.2251
summary and the AP-based epoch choice, as pending re-evaluation. The bug does
not itself invalidate Brier scores, window counts, splits or model fitting.
Do not overwrite old artifacts; retain them as results of the old metric.
Existing aggregate AP values cannot reconstruct corrected participant AP.
Rescore saved predictions if available; the inspected pilot runners do not
save predictions or fitted model checkpoints, so a rerun may be necessary.

### 2. Event-value semantics need a gate before interpreting training

The current event runner sums `Normal + Extended` at the bolus occurrence
time, without using duration. Verify which fields could be known at that
time; retrospective extended-delivery totals can contain later information.
Until verified, this is a potential as-of violation, not a proven source leak.

The latest basal rate is chosen from the final same-time record in sort order.
Distinct same-time pump states are retained, so that choice is deterministic
but not yet clinically justified. Missing numeric values also become zero in
summaries. Add explicit missing/conflict indicators and a documented basal
state rule. Record counts and summed meal entries describe retained records;
they do not establish delivered insulin or uniquely consumed meals.

Food rows with unsupported units are dropped entirely, including from event
counts. Documentation currently describes only excluding their carbohydrate
totals. Reconcile the intended policy and implementation.

### 3. Development results are exploratory, not clean nested-CV estimates

Epoch selection used outer-0 validation, whose participants become outer-1
test participants. Temporal preprocessing was also selected across the
development pool. The five-fold summary therefore includes participants who
informed shared choices. This is acceptable as development evidence, but must
not be described as an independent confirmatory estimate or nested CV.

The holdout is excluded from fitting and predictive scoring in these runners,
but its raw records are scanned and aggregate label/coverage counts have been
reported. Say "not used for model fitting or predictive evaluation" rather
than "never read" or wholly "unseen". Freeze remaining choices before scoring it.

### 4. Reporting and reproducibility need strengthening

- Fold aggregation weights macro AP by all participants, although AP excludes
  participants with no positives. Archive and weight by the actual AP-defined
  denominator; the current aggregate artifacts cannot verify that assumption.
- Save protected participant predictions, model state, metric version, code
  revision, configuration and exact window identities. This enables paired
  intervals and rescoring without repeated raw-data preprocessing.
- The logistic runners regenerate windows instead of consuming/verifying the
  frozen index. Matching total counts is useful but is not proof of identical
  window membership; add a streaming identity/label reconciliation gate.
- The binary rule's Brier score is a squared error for 0/1 outputs. Its
  comparison with probabilistic logistic outputs is not by itself evidence of
  better calibration. Add calibration plots and a training-prevalence reference.
- `validate_manifest` does not enforce locked-holdout separation itself,
  although this actual manifest is disjoint. Encode the verified invariant.
- `tests/` is ignored in `.gitignore`. Ensure the new regression tests are
  included in version control before publishing or moving environments.

### 5. Runtime and status claims were too strong

The event iterator avoids rescanning the full event history, but still sums
active bolus/food records per window. It is not strictly linear in total
windows plus records. Free-space checks occur during sorting, not throughout
partition writes. Twenty GiB is an entry threshold, not a guarantee of enough
space. Missing source tables also need explicit rejection before training.

The protocol and implementation-status documents contain older pending-data
statements that conflict with completed audits. Consolidate them around the
actual milestone and this correction notice. Passing synthetic tests validates
the covered cases; it does not establish scientific validity of the pipeline.

## Ordered next steps

1. Preserve old results and correct AP-based evaluation/configuration selection.
2. Resolve event-value availability, same-time basal states, missingness and
   the history-boundary contract before the next interpreted event comparison.
3. Add prediction/checkpoint archives, metric denominators and window identity
   verification. Cache reusable protected features to reduce repeated scans.
4. Evaluate a matched CGM versus event-summary comparison on development data.
   This establishes value of recorded context, not value of graph relations.
5. Implement the prespecified event-sequence and generic/typed graph controls,
   matching information, search budgets and capacity. Add paired participant
   uncertainty, calibration, episode metrics and availability sensitivity.
6. Freeze the final protocol, then evaluate the protected holdout once under
   that plan. Pursue common-field external validation in another supplied
   cohort; do not imply the other datasets already supplied empirical results.

The project does not need restarting. It needs these evaluation and event
semantics corrections before stronger claims or further large training runs.
