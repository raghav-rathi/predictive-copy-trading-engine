# FVG Mitigation — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Gap definition | 3-bar non-overlap | Spec. The textbook SMC/ICT FVG. |
| Gap lifetime | 200 bars | Spec. Stale gaps stop mattering after ~8 days. |
| Uses per gap | 1 (first mitigation) | Spec. First touch reacts; later touches break. |
| Entry zone | full gap | Spec. Any dip into the zone counts as mitigation. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 20 | 3 bars to form a gap + ATR(14) + margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
