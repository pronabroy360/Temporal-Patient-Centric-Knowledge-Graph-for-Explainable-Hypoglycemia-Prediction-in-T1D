# Loop cadence-tolerance selection

Status: frozen 13 September 2026. Selection used only the 652-person protected development set. The identifier-free evidence is [loop_cgm_development_tolerance_audit.json](../audit/loop_cgm_development_tolerance_audit.json).

| Per-interval tolerance | Complete contiguous 30-minute futures | Contiguous-history input-eligible indices | Positive future-low labels |
|---|---:|---:|---:|
| 0 seconds | 14,162,385 | 2,804,581 | 858,367 |
| **±1 second** | **53,959,546** | **41,391,103** | **3,216,982** |
| ±2 seconds | 54,914,271 | 43,483,180 | 3,275,847 |

The primary timestamp rule is **300 seconds ±1 second between adjacent observed readings**. It is the smallest candidate that captures the prevalent 299/301-second device-clock jitter. Moving from ±1 to ±2 seconds adds a comparatively small 1.8% of complete contiguous future segments, while admitting less clearly nominal 298/302-second intervals.

This selection is based on chronology and coverage only, not model performance or held-out outcomes. It preserves raw timestamps and values, creates no readings, and applies to every comparator. The exact-300-second result remains a sensitivity analysis.

These are strict contiguous-run diagnostics. The final benchmark will separately implement the protocol's permitted 22/24 observed history with at most two consecutive missing slots; it must report that rule independently rather than mislabeling this diagnostic as final window eligibility.
