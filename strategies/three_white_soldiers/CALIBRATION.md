# Three White Soldiers — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| SMA trend window | 50, 5 bars before the pattern | Spec. |
| ATR window | 14 | Spec. |
| Max wick fraction | 25% of the candle's range | Spec. |
| Min body | 0.5 × ATR(14) | Spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 100 | Indicator warmup + margin. |

Spec clarifications (documented, no tuning): "each open inside the
previous candle's body" is applied as open strictly between the
previous candle's body bounds min(o, c) and max(o, c), which also
covers the 1st soldier/crow whose previous candle is a trend bar of
the opposite direction. The trend check is the 5 bars immediately
before the 3-candle pattern (bars i-7..i-3 for a pattern completing
on bar i). The exit level is the 1st soldier/crow's open, tracked
forward until a newer pattern refreshes it.

No bug fixes requiring re-runs, no PnL-selected tuning.

Zero-trade outcome (verified genuine, not a bug): the pattern never
completes on any of the three coins in the backtest window. A
diagnostic on real BTC data found 169 qualifying bullish candles and
153 bearish ones, but zero runs of three in a row — the four-way
conjunction three bars running is too strict for 1h crypto. The unit
tests prove the pattern fires on crafted data, so the implementation
is correct and the spec as written is simply untestable on this
market/timeframe.
