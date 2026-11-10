# Full-history Colab retry handoff — 2026-10-16

## Current state

The corrected full-history controlled comparison has been launched in the existing Colab runtime through Kimi WebBridge. It is a development-only outer-0 run; the locked holdout remains excluded.

- Colab notebook: [Loop full-history comparison](https://colab.research.google.com/drive/1w_Vz96ROeR1Ci5b1Qh_orE2eUd60DoqA)
- Input staging: `/content/t1d_loop_full_history_input`
- Corrected trainer: `/content/t1d_full_history_code_3c4112501447/kaggle_event_sequence_gru/train_history_controlled.py`
- Drive run folder: `/content/drive/MyDrive/loop_full_history_runs/loop_full_history_20261016T134913Z_retry_6a97d29f`
- Launcher process: `27930`; current preflight process at last check: `27946`
- Launcher log folder: `/content/drive/MyDrive/loop_full_history_runs/retry_launcher_20261016T134913Z`

The first retry completed input verification but failed while writing the receipt: `input_stat_digest()` called `object_digest`, which was imported locally inside `main()` and therefore was not visible to the helper. No checkpoint was produced. I fixed the helper to hash its JSON payload directly and added a regression test.

A second attempt started as a foreground notebook cell. Colab then disconnected the runtime during the cache scan. After reconnecting, Colab refused another GPU allocation with the message that the account had reached its GPU usage limit. No receipt or checkpoint was produced by this attempt. The staged inputs were present in Drive; the temporary Colab `/content` workspace may be lost when the next runtime is allocated.

The Colab GPU quota is now the blocker. Kaggle's previous notebook URLs returned “We can't find that page” in the connected browser session, so no alternate GPU runtime was available to verify. Do not start another Colab GPU attempt until GPU access returns, and do not purchase compute without the user's explicit approval. The safest next step is to wait for quota reset; the corrected code and notebook are ready locally.

The earlier failed run's `input_preflight.log` records a completed input preflight and the expected content fingerprint `3c142f9e6fbeeac7afbb30bb745f67593fad1282c0463dd9a8a5b15314af4c28`. Its failure occurred afterward in the GPU smoke test, before any epoch checkpoint. It did not save the reusable receipt. This retry performs the expensive verification once, writes `input_preflight_receipt.json`, then reuses it for both model variants.

## Fix and local verification

`train_history_controlled.py` now tests whether changing the full CGM missingness channel changes model output with a numerical tolerance instead of requiring bit-exact GPU equality. Its preflight receipt is bound to the manifest, window identity, fold, input file metadata, and the verified participant/window counts. The Colab notebook generator passes the receipt to the preflight and both training runs.

Regenerated notebook artifacts:

- `kaggle_event_sequence_gru/loop_full_history_comparison.ipynb`
- `kaggle_event_sequence_gru/loop_full_history_comparison_colab.ipynb`

Local validation: `PYTHONPATH=src pytest -q` — **132 passed, 3 skipped**.

## Resume and monitor

When Colab GPU access is available again, use the notebook's recovery cell and keep it running in the foreground. The Drive run folder from the latest attempt was `/content/drive/MyDrive/loop_full_history_runs/loop_full_history_20261016T142838Z_retry_76f0191a`. Earlier incomplete attempts are kept under their own run folders; do not mistake their logs for training results.

After reconnecting, check:

```bash
RUN=/content/drive/MyDrive/loop_full_history_runs/loop_full_history_20261016T142838Z_retry_76f0191a
tail -n 30 "$RUN/input_preflight.log"
tail -n 30 /content/drive/MyDrive/loop_full_history_runs/retry_launcher_20261016T134913Z/launcher.log
ls -lh "$RUN/input_preflight_receipt.json" "$RUN/history-only/checkpoint-epoch-1.pt" "$RUN/history-event/checkpoint-epoch-1.pt"
nvidia-smi
```

After a new runtime is connected, restage the full-history inputs from Drive before running. Then the driver runs `history-only` and `history-event`, two epochs each, followed by a paired comparison. Logs, checkpoints, predictions, and results are written to Drive. Do not launch a second training driver while one is active.
