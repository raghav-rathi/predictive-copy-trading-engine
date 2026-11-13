# MACD Signal-Line Crossover — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| MACD fast / slow / signal | 12 / 26 / 9 | Appel's published defaults, confirmed by the Investopedia MACD reference (12-period EMA minus 26-period EMA, 9-period EMA signal line). |
| Entry / exit | Signal-line crossover, exit on the opposite cross | Per spec: the crossover is the trigger in both directions. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | EMA(26) + EMA(9) of the MACD line needs ~35 bars to stabilise; 60 gives margin. |

## Spec deviations

1. **Harness stop/trail as the practical exit.** Appel's system exits
   on the opposite cross alone. The batch-standard risk layer
   (2xATR stop, 2.5xATR trail, 120-bar max hold) is applied on top,
   per the spec's own instruction, so most trades end on the
   stop/trail rather than the opposite cross.

No bug fixes requiring re-runs, no PnL-selected tuning.
