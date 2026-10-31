# Chande Momentum Oscillator — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| CMO period | 14 | Spec; the standard CMO lookback (also the source's typical period alongside 9/20). |
| Overbought / oversold | +50 / -50 | Spec; the source's standard CMO extreme levels. |
| Neutral level | 0 | Spec; the midpoint of the -100/+100 range, where up and down sums balance. |
| Entry rule | Cross out of the extreme zone | Spec; entering on the cross rather than on first touch avoids buying into a still-deepening extreme. |
| Exit rule | Cross of 0 or into the opposite extreme | Spec; either momentum has faded (0) or reversed into the opposite extreme. |
| Flat-window CMO | 0.0 | Spec; no movement means no momentum in either direction. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 20 | Spec minimum: 15 bars for CMO(14), 14 for ATR(14), +5 margin. |

No bug fixes requiring re-runs, no PnL-selected tuning. The losing
backtest (BACKTEST.md) was not tuned upward.
