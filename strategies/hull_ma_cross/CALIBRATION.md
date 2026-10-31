# Hull MA Cross — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Fast HMA | 16 (8 / 16 / 4) | Spec. Alan Hull's own default period for HMA. |
| Slow HMA | 64 (32 / 64 / 8) | Spec. 4x the fast period, the standard fast/slow spacing; 64 1h bars ≈ 2.7 days of trend context. |
| WMA weights | 1..n, newest heaviest | Spec. Hull's definition. |
| sqrt(n) rounding | round to nearest int | Spec. 16 → 4 and 64 → 8 are exact, so no rounding choice arises. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 80 | Spec minimum: 64 + 8 = 71 bars for HMA(64) to exist, +9 margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
