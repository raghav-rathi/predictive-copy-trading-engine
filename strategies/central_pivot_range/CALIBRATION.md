# Central Pivot Range — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Pivot | (H+L+C)/3 | Spec. Ochoa's formula. |
| BC | (H+L)/2 | Spec. Ochoa's formula. |
| TC | 2*Pivot - BC | Spec. Ochoa's formula. |
| Level source | prior UTC day | Spec. Completed days only, no lookahead. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 48 | 24 bars for one full UTC day + margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
