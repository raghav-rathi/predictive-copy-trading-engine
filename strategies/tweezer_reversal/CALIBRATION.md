# Tweezer Reversal — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Trend filter | Close below/above SMA(50) for 5 bars | Spec. |
| Equality tolerance | \|low2 − low1\| (or \|high2 − high1\|) ≤ 0.1 × ATR(14) | Spec. |
| Midpoint rule | Bar 2 closes past bar 1's midpoint (o1+c1)/2 | Spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 100 | Indicator warmup + margin. |

Spec interpretation decisions (no tuning involved):

- "The 5 bars before the pattern" is read as the five bars
  immediately preceding bar 1 of the pattern (indices i−6..i−2 for
  a pattern completing on bar i). The tolerance uses ATR(14) at
  bar 2 (the completing bar).
- twz_low / twz_high hold the tweezer extremes on the pattern bar
  and are forward-filled afterwards so the exit rule can reference
  the most recent pattern's extremes.

No bug fixes requiring re-runs, no PnL-selected tuning.
