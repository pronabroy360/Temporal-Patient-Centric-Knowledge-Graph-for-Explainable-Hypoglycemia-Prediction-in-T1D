# Dataset intake record

Create one copy of this record for every release added from the Jaeb directory or another lawful source. Do not mark a candidate as primary until the required fields have evidence from the release documentation and files.

## Identity and provenance

| Field | Record |
|---|---|
| Dataset/study name |  |
| Directory or landing-page URL |  |
| Download/release filename |  |
| Date obtained |  |
| Local release path |  |
| Readme/terms/protocol versions |  |
| Required attribution/disclaimer |  |
| Access basis and permitted users |  |
| Raw-file checksum manifest |  |

## Cohort and chronology

| Field | Record |
|---|---|
| Roster rows and unique participants |  |
| Eligibility/completion/dropout definitions |  |
| Participant overlap across tables |  |
| Source treatment/device periods |  |
| Timestamp fields and documented clock basis |  |
| Date de-identification or random offsets |  |
| Timezone/offset available? |  |
| First-usable/arrival time available? |  |
| Duplicate and out-of-order policy |  |

## Mandatory field gate

| Requirement | Evidence | Pass? |
|---|---|---|
| Lawful access for intended analysis and compute environment |  |  |
| Stable pseudonymous participant ID |  |  |
| Longitudinal CGM with timestamps |  |  |
| Enough future CGM for complete 30-minute labels |  |  |
| Enough participants and episodes for patient-disjoint evaluation |  |  |
| Timestamped insulin delivery for event-relation claim |  |  |
| Timestamped meals/carbohydrates for event-relation claim |  |  |
| Timestamped activity/exercise, if claimed |  |  |
| Release-stable split or enough participants for grouped nested validation |  |  |

## Audit outputs

- [ ] File inventory recorded without modifying raw files.
- [ ] Header and glossary mappings recorded for every candidate input table.
- [ ] Participant counts and table intersections audited.
- [ ] CGM values, units, missingness and invalid records audited.
- [ ] Within-participant timestamps sorted; source-order anomalies counted.
- [ ] Duplicate timestamps retained and a development-frozen policy documented.
- [ ] Coverage, gaps, labelable windows and confirmed episodes recomputed after sorting.
- [ ] Event timing and capture status distinguished from retrospective summaries.
- [ ] Patient-disjoint fold manifest generated only after the release-specific audit.
- [ ] Scope decision recorded: `core event-relation`, `CGM-only`, `external validation`, or `exploratory`.

## Decision

**Status:** `pending` / `passes core gate` / `CGM-only` / `external validation` / `rejected`

**Reason and limitations:**

**Audit report:**
