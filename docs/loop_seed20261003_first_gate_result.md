# Loop first-gate paired result: seed 20261003

## Result

On the frozen outer-0 validation cohort, the capacity-matched CGM-only MLP outperformed the clean event-sequence GRU on participant-macro average precision (AP). The paired comparison used the same 130 participants and all 8,885,621 verified validation windows, including 274,044 positive labels.

| Metric | CGM-only MLP | Clean event GRU | Paired difference (MLP − GRU) |
|---|---:|---:|---:|
| Participant-macro AP | 0.48196 | 0.47422 | +0.00774 (95% participant-bootstrap interval: +0.00618 to +0.00927) |
| Participant-macro Brier | 0.02115 | 0.02132 | −0.000174 (95% interval: −0.000220 to −0.000127) |
| Pooled Brier | 0.02079 | 0.02096 | −0.000176 |

The MLP had higher AP for 103 participants and lower AP for 27; there were no ties. It had lower participant Brier for 100 participants and higher Brier for 30. Lower Brier is better. The interval resamples participants from fixed prediction archives; it does not include training-seed variability or model refitting.

## Validation and provenance

Both prediction archives passed exact window-identity checks against the frozen development cache. They share the same manifest checksum (`69b41e4acfae7d2afc990c8cd15d8fc3f969784d4e5f6534a9263033d341ad52`) and window-identity checksum (`26036d7d3d27c21a4407d15aacd916b98ba598dfded5da319288a74b54a592aa`). The models use matched two-epoch training settings and nearly equal capacity (22,047 MLP parameters; 22,065 GRU parameters). The GRU resumed from its saved epoch-1 checkpoint; the epoch-2 checkpoint and its optimizer state were retained.

The inference archive was generated in checkpoint-evaluation mode. Its metadata records that mode and the fact that it came from the completed trained checkpoint; the comparator then verified the reported metrics against the saved predictions. The run is development-only. It did not inspect the locked holdout.

The event stream is a retrospective occurrence-time replay with immediate availability assumed, not measured. A zero event count means no retained source record, not verified clinical absence. This experiment compares a temporal event-sequence architecture with a CGM-only model; it does not yet establish the value of explicit graph relations or clinical event semantics.

## Interpretation and next gate

For this seed and this model pair, the event-sequence GRU did not improve prediction beyond the matched CGM-only model. This is a useful negative first-gate result, not a final conclusion about event relations: one seed does not measure training variability, and the GRU is only one way to encode event histories.

The next gate is the prespecified second seed, 20261004, with both models trained under the same split, inputs, architecture definitions, and optimizer settings. If the direction replicates, subsequent work should isolate relation structure and event timing/value information with controlled ablations before making a knowledge-graph benefit claim. Keep the locked holdout unopened until all model and analysis choices are frozen.

## Artifact location

The private Colab/Drive run directory is `loop_seed_replication_20261013T095921Z_42ed4995`. It contains both prediction archives, the epoch-1 and epoch-2 GRU checkpoints, the paired comparison JSON, run metadata, and the campaign manifest. Prediction rows include protected participant identifiers and must remain private.

## Second-seed status (15 October 2026)

Seed `20261004` is now a completed paired development-validation comparison.
The clean GRU completed two epochs; both archives passed the strict
participant/time/label pairing on 130 participants and 8,885,621 windows.
The CGM-only MLP again led in participant-macro AP and Brier. The original
MLP report was backed up before reconciling a small CPU-replay metric mismatch
to the saved prediction files. The paired comparison and campaign-completion
checks then passed. See the [second-seed result](loop_seed20261004_second_gate_result.md)
for exact metrics, provenance, limitations, and the aggregate bundle checksum.
The earlier private MLP checkpoint-recovery bundle remains a historical
artifact; the locked holdout remains unopened.
