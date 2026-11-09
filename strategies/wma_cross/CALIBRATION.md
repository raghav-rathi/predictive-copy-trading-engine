# WMA Crossover — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Fast WMA | 9 | Spec. |
| Slow WMA | 21 | Spec. |
| WMA weights | linear n..1, newest weighted n | Standard WMA definition. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 50 | Indicator warmup (slow WMA seed + margin). |

No spec corrections were needed: the WMA(9)/WMA(21) cross rules
and the opposite-cross exits are implementable exactly as specified
on 24/7 crypto data (no session gaps involved). The WMA math was
verified against a hand-recomputed linear-weight dot product on a
random walk, and flat data returns the flat price from the seed bar
onward.

No bug fixes requiring re-runs, no PnL-selected tuning.
