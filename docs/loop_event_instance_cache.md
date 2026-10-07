# Loop canonical event-instance cache

This protected cache is the first implementation step after the recorded-event
summary result. It creates one stable input contract for the event residual,
individual-event sequence comparator and later graph controls. It is not a
model result and does not change the locked-holdout restriction.

## What it preserves

The builder reads the Loop basal, bolus and food tables, partitions and orders
them by participant and UTC occurrence time, then writes one compressed JSONL
partition per modality and participant hash bucket. Each event instance has:

- protected participant and event IDs;
- UTC occurrence time, modality and source subtype;
- the permitted modeling value, unit and an explicit known-value flag;
- private source fields for later audit;
- the number of collapsed exact re-exports; and
- a same-time variant count, so simultaneous distinct source records are never
  silently merged.

Exact duplicates use the same fields and occurrence time and collapse to the
lowest numeric `RecID` after sorting. Different records at the same timestamp
remain separate event instances. Basal rates are retained as reported pump
state, normal bolus is the only bolus amount allowed in the initial contract,
and non-gram or missing carbohydrate values are retained with
`model_value_known=false` rather than converted to zero. Extended bolus source
fields remain private provenance only until their occurrence-time meaning is
validated.

All event features remain an optimistic retrospective occurrence-time replay:
the Loop upload-linkage audit did not establish an observed availability time.

## Compatibility and provenance gates

The builder accepts only the development participants in the protected model
manifest. It refuses a CGM cache with a different manifest checksum or
partition count. Its metadata stores the manifest checksum, frozen CGM window
identity hash, per-file content digests, record counts and aggregate duplicate,
unknown-value and same-time-variant counts. The public summary contains only
aggregate metadata; it emits no participant or event identifiers.

## Build command

The full build partitions and sorts the raw auxiliary event tables and can use
substantial temporary disk space. Run it only after confirming at least 20 GiB
free space (the default safety floor), from the project root:

```bash
PYTHONPATH=src python3 scripts/build_loop_event_instance_cache.py \
  'data/Loop study public dataset 2023-01-31' \
  --model-manifest private/loop_model_manifest.json \
  --cgm-cache-directory private/loop_cgm_feature_cache \
  --output-directory private/loop_event_instance_cache \
  --summary-output audit/loop_event_instance_cache.json
```

The output paths must be new. This protects the already frozen cache from an
accidental overwrite. If a full build stops, remove only its incomplete output
directory after inspecting it, then rerun; the temporary sorting workspace is
removed automatically.

Successful completion should produce 192 private files (three modalities × 64
partitions), `private/loop_event_instance_cache/metadata.json`, and the
aggregate `audit/loop_event_instance_cache.json`. Preserve both checksums for
all later residual, sequence and graph experiments.

## Validation

The software tests cover exact-repeat collapse, same-time variants, normal
versus extended bolus handling, unknown carbohydrate units, metadata checksum
gating and a small end-to-end build. Run:

```bash
PYTHONPATH=src pytest -q
```

After the production build, inspect the aggregate summary only. It is expected
to report a nonzero unknown-value count and potentially same-time variants;
these are data-quality states to model explicitly, not failures to discard.
