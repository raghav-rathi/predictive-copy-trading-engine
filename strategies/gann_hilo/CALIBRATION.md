# Gann HiLo Activator — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| SMA period | 3 | Spec. Krausz's standard activator window. |
| Flip rule | close beyond previous opposite SMA | Spec. The activator's state rule, not a same-bar cross. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 20 | 3 bars for the SMAs + ATR/margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
