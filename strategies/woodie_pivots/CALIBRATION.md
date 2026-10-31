# Woodie Pivots — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Pivot day | UTC calendar day | Spec. Crypto trades 24/7, so the UTC day is the natural daily session. |
| Prior-day only | Shifted daily table | Spec. A day's levels must be known before its first bar; using the current day's H/L/C would be lookahead. |
| PP formula | (H + L + 2C) / 4 | Spec. Woodie's definition; double weight on the close. |
| Entry levels | R1 / S1 | Spec. First resistance/support: the nearest breakout levels, so entries are not rare. R2/S2 computed but not traded. |
| Exit level | PP | Spec. Mean reversion back to the pivot closes the breakout trade; a failed breakout returns to PP first. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 50 | Spec minimum: 48 bars (two UTC days) before levels are defined on every bar, +2 margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
