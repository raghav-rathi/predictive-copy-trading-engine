# Dark Cloud Cover — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| SMA trend window | 50 | Spec. |
| Min bar-1 body | 0.6 × bar 1's range | Spec. |
| Bar-2 gap / midpoint | Open beyond bar 1's high/low, close past bar 1's midpoint | Spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 100 | Indicator warmup + margin. |

Spec clarifications (documented, no tuning): the trend check uses bar
1's close vs its SMA(50) (the bar that establishes the trend). Bar
2's extremes are forward-filled from the pattern bar and the exit is
checked from the following bar on (shifted by 1), so the exit cannot
trigger on the pattern bar itself; the level stays armed until a
newer pattern refreshes it.

No bug fixes requiring re-runs, no PnL-selected tuning.

Near-zero-trade outcome (verified genuine, not a bug): the pattern
completes exactly once across all three coins (one HYPE piercing
pattern). A diagnostic on real BTC data found the gap condition is
the binding constraint — bar 2 opening above bar 1's high happened
only twice in 5,223 bars, because 24/7 crypto has no session gaps.
The unit tests prove the pattern fires on crafted data, so the
implementation is correct and the gap-based spec as written is
essentially untestable on 1h crypto.
