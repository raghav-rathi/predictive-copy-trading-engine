# Rising Three Methods — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Trend filter | Close above/below SMA(50) | Spec. |
| Bar-1 body | ≥ 1.0 × ATR(14) | Spec. |
| Inside bars | Bars 2–4 fully inside bar 1's range (high < h1, low > l1) | Spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 100 | Indicator warmup + margin. |

Spec interpretation decisions (no tuning involved):

- The trend filter is checked on bar 5's close vs SMA(50) (the
  entry bar). Bar 1's body is compared against ATR(14) measured
  at bar 1 (the bar whose body is being judged).
- rtm_bar1_high / rtm_bar1_low hold bar 1's extremes on the
  pattern bar and are forward-filled from the most recent pattern
  of either direction, so the exit rule can reference them.

No bug fixes requiring re-runs, no PnL-selected tuning.
