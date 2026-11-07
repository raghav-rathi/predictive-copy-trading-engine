# 1-2-3 Reversal — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Fractal pivots | 5-bar local extrema, min swing 0.9x ATR(14), confirmed 2 bars late | Spec: swing detector shared across batch 29 geometric strategies. |
| 1→2 leg | ≥ 1.0x ATR(14) | Spec (Joe Ross 1-2-3). |
| Point 3 | Pullback extreme holding beyond point 1 | Spec; pattern void if point 3 falls to/below point 1. |
| Entry | Close above point 2 (long) / below point 2 (short), once per pattern | Spec. |
| Exit | Close below point 3 (long) / above point 3 (short), or opposite 1-2-3 completion | Spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 100 | Indicator warmup + margin. |

Spec-interpretation decisions (not PnL tuning):

- Void is evaluated on bar closes (a close through point 1 voids the
  pattern); the point-3 level itself is a pivot price, so the close
  test is the executable form of "point 3 falls to/below point 1".
- While a pattern is active, a newer confirmed pullback extreme below
  the current point 3 (but still beyond point 1) updates point 3 to
  the deeper pullback low — the classic reading of point 3 as the
  lowest low of the pullback.
- Point-3 exit levels are latched at entry in the signal layer
  because the pattern clears from the indicator columns once it
  completes; the latch belongs to the entered trade.

No bug fixes requiring re-runs, no PnL-selected tuning.
