# Novelty evidence audit correction (31 October 2026)

## What was found

The `novelty_evidence_bundle_20261031_v4.json` and `v5.json` outputs contained
`null` for the first-seed, outer-0 time-aligned-control section. The audit
function loaded and asserted the paired JSON contract but did not return its
verification summary. The missing return made the report schema incomplete;
it did not change any model predictions or the independently saved result.

## What changed

The audit now also reads both outer-0 run records, checks their completion,
development-only split, training configuration, source and membership
agreement, validation prediction identity, and paired point estimates, then
returns an explicit `verified` record. The corrected
[`v6 audit`](../audit/novelty_evidence_bundle_20261031_v6.json) reports all
eight experiment sections as verified or verified-summary-contract. It
checks the first-seed outer-0 pair and all five second-seed pairs. The
[manuscript verification](../manuscript/verification.json) separately checks
all ten time-aligned-control fold pairs and the ten graph-versus-sequence
pairs.

The summary recomputation receipt remains separate: both the two-seed
participant summary and second-seed five-fold summary were regenerated from
saved predictions and match their archived JSON byte-for-byte. The corrected
audit is a reporting and provenance repair; it does not alter the reported
experimental effects.
