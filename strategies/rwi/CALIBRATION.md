# Random Walk Index — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Lookback n | 14 bars | Chande & Kroll's published RWI period. |
| ATR | Wilder ATR(14) | The spec's yardstick for one bar's typical movement; shared `strategies.base.atr` primitive. |
| Signal level | 1.0 | The published RWI threshold: a move larger than the random-walk expectation. Crosses are strict (previous value ≤ 1.0, current > 1.0). |
| Long entry | RWI-high crosses above 1.0 | Per spec. |
| Short entry | RWI-low crosses above 1.0 | Per spec. |
| Exits | Opposite RWI crosses above 1.0 | Per spec: the exit is the reversal signal itself, so a long exit and a short entry fire on the same bar (and vice versa). |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 30 | Covers the 14-bar lookback plus ATR(14) convergence with margin. |

## Spec deviations

None. The implementation follows the spec exactly as written.

No bug fixes requiring re-runs, no PnL-selected tuning.
