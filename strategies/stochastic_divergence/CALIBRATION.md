# Stochastic Divergence — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Slow %K / %D | (14,3) / 3 | Classic George Lane slow stochastic. |
| Swing pivots | 5-bar centered window, confirmed 2 bars later | Spec: confirmed pivots only, no lookahead. |
| Divergence lookback | consecutive pivots within 40 bars | Spec. |
| Hidden-divergence trend filter | SMA(50) | Spec: hidden divergence is a continuation signal. |
| Exit levels | %K crosses 80 (long) / 20 (short) | Standard stochastic overbought/oversold exits. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 60 | Indicator warmup + margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
