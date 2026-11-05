# Heikin Ashi Trend — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| HA construction | (o+h+l+c)/4 close, recursive open seeded with first real open | Published Valcu definition. |
| EMA filter | 50 | Standard trend-filter length from the published strategy. |
| Entry trigger | 2 consecutive same-colour HA candles with an opposite-colour HA candle in the 10 bars before the run | Published mechanism: confirmation of the HA colour flip; the 10-bar window lets the entry still fire when the close needs a few bars to reclaim EMA(50) after the flip. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 60 | Indicator warmup + margin. |

No bug fixes requiring re-runs, no PnL-selected tuning.
