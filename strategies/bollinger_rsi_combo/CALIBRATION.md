# Bollinger + RSI Mean Reversion — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Bollinger Bands | 20 periods, 2.0 std (sample std, ddof=1) | Spec. |
| RSI period | 2 (Wilder) | Spec. |
| RSI extremes | < 10 oversold, > 90 overbought | Spec. |
| Entry | Recovery close back inside the band on the bar after the setup bar | Spec: entry signal true on bar i when the setup held on bar i−1 and close[i] is back inside the band. |
| Exit | Close at/through the middle band, or opposite RSI(2) extreme | Spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 100 | Indicator warmup + margin. |

No spec corrections were needed: the (20, 2) Bollinger Bands, RSI(2),
the prior-bar setup + recovery-close entry, and the middle-band /
opposite-extreme exits are all implementable exactly as specified on
24/7 crypto data (no session gaps involved).

No bug fixes requiring re-runs, no PnL-selected tuning.
