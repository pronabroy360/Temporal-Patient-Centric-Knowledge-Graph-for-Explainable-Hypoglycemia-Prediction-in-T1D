# Loop event-to-window alignment

The alignment audit measures whether a frozen eligible CGM prediction window
has one or more canonical auxiliary events in its 120-minute history. It uses
the event occurrence time and the explicit `assumed_immediate` availability
assumption; the release cannot establish observed event-arrival times.

Run each modality separately so temporary event partitions remain bounded:

```bash
PYTHONPATH=src python3 scripts/audit_loop_window_event_alignment.py \
  'data/Loop study public dataset 2023-01-31' bolus \
  --window-index-directory private/loop_window_index \
  --output audit/loop_bolus_window_alignment.json
```

Repeat with `food` and `basal`. The report contains aggregate coverage only.
It retains differing same-time non-CGM records, collapses exact re-exports,
and never permits events after the prediction timestamp.
