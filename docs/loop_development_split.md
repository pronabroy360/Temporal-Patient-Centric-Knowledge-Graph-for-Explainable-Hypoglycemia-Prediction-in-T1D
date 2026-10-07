# Loop development split for grid-tolerance selection

Status: completed 13 September 2026. The identifier-free [summary](../audit/loop_development_manifest_summary.json) records the protected manifest checksum.

The 835-person multimodal candidate pool is deterministically divided into 652 development participants and 183 holdout participants using the versioned `loop-tolerance-v1` hash assignment. Participant IDs exist only in `private/loop_development_manifest.json`, which is excluded from version control.

Grid-tolerance candidates will be compared using development participants only. The holdout group is excluded from that choice and remains unavailable for tolerance selection, model design, calibration, threshold selection, and other development decisions.
