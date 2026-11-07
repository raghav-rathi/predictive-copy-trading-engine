# Chaikin Oscillator — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Money Flow Multiplier | ((c−l)−(h−c))/(h−l), 0 when h == l | Chaikin's definition (source). |
| ADL | Cumulative sum of MFV | Chaikin's definition (source). |
| CHO | EMA(3, ADL) − EMA(10, ADL) | Chaikin's definition (source). |
| Trend filter | SMA(50) | Spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 100 | Indicator warmup + margin. |

No spec corrections were needed: the oscillator rules are
implementable exactly as specified.

No bug fixes requiring re-runs, no PnL-selected tuning.
