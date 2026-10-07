# Loop streaming adapter

The Loop release is too large to load into memory or duplicate locally. The
adapter in `src/t1d_tkg/loop_adapter.py` therefore exposes two separate
operations:

- `loop_event` maps one already-selected source row to the canonical `Event`
  schema. It preserves `RecID`, parent upload ID, raw units and modality
  attributes. It does not deduplicate, sort, interpolate, or resolve
  conflicting timestamps.
- `iter_loop_table` reads a pipe-delimited table line by line and optionally
  filters to the protected participant manifest. It yields canonical events
  without materializing the raw table or a derived copy.

Loop records without transaction/arrival timestamps are marked
`availability_assumption="assumed_immediate"`; this is an explicit benchmark
assumption and must be varied in the planned delayed-availability sensitivity.
CGM values are converted from mmol/L to mg/dL while retaining the raw value
and unit. Their quality remains `observed_pending_range_validation` until the
range policy is frozen from the development audit.

The streaming reader intentionally runs after the release-specific
canonicalization audit. Exact repeats are collapsed and ambiguous CGM
timestamps are excluded by the audit policy; the reader itself never silently
changes source records. This separation makes provenance and reconciliation
checks possible and prevents an accidental second copy of the 19 GB release.

The next data-preparation step is a manifest-driven window index that stores
only participant, fold, index time, horizon and eligibility/label status. Event
payloads will be streamed separately for each modality when a model is run.
