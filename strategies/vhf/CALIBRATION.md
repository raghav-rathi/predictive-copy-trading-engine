# VHF Trend Regime — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| VHF period | 28 | Spec. White's standard window. |
| Regime on / off | 0.45 / 0.35 | Spec. Trending above ~0.4, ranging below ~0.3 in the literature; 0.45/0.35 brackets the gap. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 42 | 28 bars for VHF + ATR/margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
