# Fibonacci Retracement — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Fractal pivots | 5-bar local extrema, min swing 0.9x ATR(14), confirmed 2 bars late | Spec: swing detector shared across batch 29 geometric strategies. |
| Impulse leg | A→B ≥ 1.0x ATR(14) | Spec. |
| Golden zone | 38.2%–61.8% retracement of A→B | Spec. |
| Entry | First green candle closing in or above the zone after the first touch (long); first red candle closing in or below the zone (short); once per swing | Spec. |
| Exit | Close ≥ B (long) / ≤ B (short); close beyond A invalidates | Spec; the harness 2xATR stop is the enforced stop. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 100 | Indicator warmup + margin. |

Spec-interpretation decisions (not PnL tuning):

- The swing state machine is latched: a new pivot extreme after B is
  the pullback itself and never flips the swing; a newer
  same-direction swing replaces the active one only while it is
  untouched (most recent impulse wins); once the zone is touched the
  swing is locked so the armed setup's A/B/zone cannot shift under
  it; opposite-direction swings only activate when no swing is
  active. Without the lock, a touched setup's target could move
  mid-trade.
- Entries are suppressed when the close is already at/beyond the
  target (long: close ≥ B) or beyond the invalidation level (long:
  close < A) on the signal bar — entering at the target is not a
  trade.
- Entry/exit levels are latched at entry in the signal layer so the
  trade's levels survive the swing clearing or being replaced.

No bug fixes requiring re-runs, no PnL-selected tuning.
