# Chaikin Money Flow — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| CMF period | 20 | Spec. The standard Chaikin window (20 or 21 periods in the literature); 20 matches the StockCharts/Fidelity presentation. |
| Zero-cross trigger | 0 | Spec. The sign of CMF is the accumulation/distribution read; no threshold band was added. |
| H == L guard | MFM = 0 | Spec. Degenerate flat bar carries no location information; avoids division by zero. |
| Zero-volume guard | CMF = 0 | Spec. No volume, no money-flow read. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 25 | Spec minimum: 20 bars for CMF + 5 margin. |

No bug fixes requiring re-runs, no PnL-selected tuning. The heavily
negative backtest (BACKTEST.md) was not tuned upward.
