# Time Segmented Volume — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| TSV window | 18 bars | Spec: Worden TSV(18); Worden's default, confirmed in the Wickra docs. |
| Flow | (close − close[1]) × volume, rolling sum | Spec; matches the documented TSV formula exactly. |
| Entry / exit | Zero-line cross / opposite cross | Spec. Worden's published rules use a 9-bar EMA of TSV as the signal line instead of the zero line — that variant was NOT implemented; the briefed zero-line cross was shipped exactly. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 50 | Indicator warmup + margin (TSV needs 19 bars; 50 is margin). |

No spec corrections were needed: the (close − close[1]) × volume
rolling-sum formula and the zero-line cross rules are implementable
exactly as specified on 24/7 crypto data (no session gaps involved).

No bug fixes requiring re-runs, no PnL-selected tuning.
