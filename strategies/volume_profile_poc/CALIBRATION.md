# Volume Profile POC — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Profile window | 168 trailing bars incl. current | Spec. |
| Price bins | 24 equal bins over min low → max high | Spec. |
| Value area | ≥70% of window volume | Spec. |
| Dip tolerance | 0.5x ATR(14) | Spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 200 | Indicator warmup (168-bar window) + margin. |

Implementation notes (closest faithful variant, no spec change to
the trading rules):

- POC is the volume-weighted mean close of the highest-volume bin,
  not the geometric bin midpoint. The two coincide when closes are
  spread evenly across the bin; the mean degrades gracefully to the
  exact traded price when every close in the bin is identical, where
  a geometric midpoint would sit half a bin-width away from the
  price and flag a spurious signal on exactly-flat data.
- VAH/VAL expansion is greedy: start at the POC bin and add one
  neighbouring bin at a time, taking the heavier neighbour first
  (ties go right), until the contiguous set holds ≥70% of window
  volume. A zero-range window collapses POC/VAH/VAL to the close.
- The "prior bar's close was above POC" check compares the prior
  bar's close against the prior bar's POC (not the current POC).

No bug fixes requiring re-runs, no PnL-selected tuning.
