# RSI Bollinger Bands — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| RSI period | 14 | Spec. Wilder's standard RSI. |
| Band period / width | 20 / 2σ | Spec. The Bollinger standard, applied to RSI. |
| Exit | RSI middle band | Spec. Reversion to RSI's own mean. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 50 | 34 bars for RSI(14) + bands(20) + margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
