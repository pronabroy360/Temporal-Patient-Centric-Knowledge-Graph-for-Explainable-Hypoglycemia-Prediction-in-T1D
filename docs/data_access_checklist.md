# Data access and release-audit checklist

Status: candidate selection, 10 September 2026. No data request, download, account action, DUA acceptance or external correspondence has been made in this session.

The researcher reports that the OhioT1DM DUA permits a student to use the data only when their supervising advisor submits the request and that the requester must be a current institutional employee. Direct application by this researcher is therefore unavailable. OhioT1DM remains conditional on an eligible advisor taking responsibility for the request. The project must first apply the [fallback and dataset selection strategy](dataset_fallback_strategy.md).

The [Jaeb diabetes directory](https://public.jaeb.org/datasets/diabetes) contains public-use and controlled-access candidates. T1DEXI remains conditional on its study-specific Vivli review and usable field dictionary. A public-use form or open repository does not establish scientific suitability; inspect permitted use and raw fields before selection.

The supplied AIDE T1D release was obtained from the Jaeb directory. Its [release audit](aide_t1d_release_audit.md) found a usable CGM source but no timestamped meal, activity or insulin-delivery stream. It is therefore a CGM benchmark or validation candidate, not the sole source for the core event-relation experiment. Apply the same provenance and release-specific audit fields to each additional Jaeb dataset added locally.

## Access register

Complete this table before importing any patient file into the analysis environment.

| Field | OhioT1DM (advisor route) | Primary candidate | External candidate |
|---|---|---|---|
| Custodian and request URL |  |  |  |
| Request date and requestor |  |  |  |
| Eligibility basis/institutional affiliation | Advisor must be eligible; not yet confirmed |  |  |
| DUA/IRB or exemption identifier |  |  |  |
| Approved users and storage location |  |  |  |
| Release/version identifier |  |  |  |
| Permitted analyses and redistribution limits |  |  |  |
| Expiration/deletion requirements |  |  |  |
| Raw-file checksum manifest |  |  |  |
| Data dictionary version |  |  |  |

Do not put patient data, credentials, signed agreements, or private contact details in this repository.

## Pre-import gate

- Record the approved storage path, encryption/access controls, named users, and deletion process.
- Save the release identifier and a checksum manifest outside the raw-data directory.
- Keep raw files immutable; write normalized events and audit outputs to a separate derived-data location.
- Record the source timezone and clock convention from the release documentation. The Ohio adapter requires an explicit timezone because the documented XML timestamps are timezone-naive.
- Confirm whether each modality has an occurrence time, first-usable/arrival time, revision history, quality flag, and missing-value convention.
- Confirm whether the release contains development/training and held-out/testing participants and whether any participant appears in more than one split.

## Release-specific audit

For OhioT1DM, run the existing adapter only if the advisor-mediated route is approved and the pre-import gate is complete:

```bash
PYTHONPATH=src python3 scripts/audit_ohio.py /path/to/ohiot1dm --split training --timezone Region/City
```

For an auditable run, persist the report and generate the shared fold manifest in the same command:

```bash
PYTHONPATH=src python3 scripts/audit_ohio.py /path/to/ohiot1dm --split training --timezone Region/City \
  --output audit/training-audit.json --manifest-output audit/training-folds.json
```

The report records the manifest checksum. Keep that checksum with the model and prediction archives. A different selected dataset requires a release-specific adapter and tests before its audit; do not force non-Ohio data through the Ohio parser.

Save the JSON output with the release and code version. Review, at minimum:

- participant and file counts, split membership, coverage dates and longest CGM gaps;
- duplicate timestamps, non-monotonic or malformed records, exact missing-value spellings, and parse failures;
- valid readings below 70 and 54 mg/dL, confirmed episode onsets, censored boundaries, and labelable 30/60-minute windows;
- event counts by modality and capture status; absent meal or bolus records are not evidence of fasting or zero delivery;
- availability-time metadata and whether the `assumed_immediate` fallback is justified for each source block;
- timestamp alignment, native sampling cadence, and any device or participant clock changes.

Do not freeze labels, graph topology, duplicate handling, or model splits until these findings are written into the release-specific audit report. If transaction times are unavailable, retain the explicit assumption and make the delayed-arrival analysis a declared simulation rather than a measured latency result.

## Stop/go decision

Proceed to benchmark freezing only if the release has enough participant-disjoint, future-observable CGM windows and documented modality semantics for the proposed claim. If event capture is sparse or timing semantics are unresolved, narrow the claim to a CGM-only or summary comparison and record the limitation before selecting models.
