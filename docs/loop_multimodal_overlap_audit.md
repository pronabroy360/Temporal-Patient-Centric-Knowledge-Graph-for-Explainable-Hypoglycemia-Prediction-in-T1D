# Loop multimodal event overlap audit

Individual modality coverage does not show whether the same prediction windows
contain basal, bolus, and food records. This audit measures all eight recorded
presence patterns in the frozen 120-minute histories.

```bash
PYTHONPATH=src python3 scripts/audit_loop_window_event_overlap.py \
  'data/Loop study public dataset 2023-01-31' \
  --window-index-directory private/loop_window_index \
  --output audit/loop_multimodal_window_overlap.json
```

It uses temporary canonical projections of all three event modalities and may
stop at its 15 GiB free-space safety floor. A completed report is needed before
defining the primary multimodal comparison population.

## Result

The completed audit reconciled exactly to 56,375,850 frozen windows.

| Recorded 120-minute history pattern | Windows | Share |
|---|---:|---:|
| No basal, bolus, or food | 11,400,398 | 20.222% |
| Basal only | 24,676,750 | 43.772% |
| Basal and bolus only | 5,377,819 | 9.539% |
| Basal and food only | 1,256,426 | 2.229% |
| Basal, bolus, and food | 12,771,176 | 22.654% |
| Other non-basal patterns combined | 893,281 | 1.585% |

The 12,771,176 all-three windows form a viable strict multimodal sensitivity
cohort. The main information-matched comparison should retain all frozen
windows and represent missing recorded-event history explicitly, rather than
equating a missing record with a clinical zero.

Source artifact: `audit/loop_multimodal_window_overlap.json`.
