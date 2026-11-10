# Intraday Momentum Index — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| IMI period | 14 bars | Chande's published IMI window (14-period gain/loss sums). |
| Gain / loss per bar | max(close − open, 0) / max(open − close, 0) | Published IMI definition: intraday (open-to-close) movement, not close-to-close changes. |
| IMI formula | 100 * sum(gains) / (sum(gains) + sum(losses)) | Published formula; bounded [0, 100] by construction. |
| Zero-movement window | IMI = 50 | Spec-mandated neutral value when sum(gains) + sum(losses) == 0. |
| Long entry | IMI crosses up through 30 | RSI-style oversold exit, per spec. |
| Short entry | IMI crosses down through 70 | RSI-style overbought exit, per spec. |
| Long exit | IMI crosses above 70 | Opposite-extreme cross, per spec. |
| Short exit | IMI crosses below 30 | Opposite-extreme cross, per spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 30 | Indicator warmup (14-bar IMI window + margin). |

No spec deviations were needed: the published IMI formula, the
zero-movement = 50 rule, and the 30/70 cross rules are all
implementable exactly as specified on 24/7 crypto data (no session
gaps involved). The implementation was verified against hand-computed
cases: all-gain window → 100, all-loss window → 0, 30/10 gain/loss
sums → 75, equal sums → 50, flat window → 50, and a flat
close-to-close series with intraday gains → 100 (confirming the
open-to-close, not close-to-close, construction).

No bug fixes requiring re-runs, no PnL-selected tuning.
