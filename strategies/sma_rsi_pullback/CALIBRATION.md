# SMA-RSI Pullback — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Trend | SMA50 vs SMA200 | Spec. |
| Pullback RSI band (long) | 40–55 inclusive | Spec. |
| Pullback RSI band (short) | 45–60 inclusive | Spec. |
| Entry window | 5 bars after a pullback bar | Spec. |
| Long exit | RSI(14) > 70 or close below SMA200 | Spec. |
| Short exit | RSI(14) < 30 or close above SMA200 | Spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 250 | Indicator warmup (SMA200) + margin. |

Implementation notes (closest faithful variant, no spec change to
the trading rules):

- "First bar whose close is back above SMA50" is implemented as a
  cross back up through SMA50: close > SMA50 with the prior bar's
  close ≤ its SMA50, within 5 bars after a pullback bar. A
  pullback bar whose close never went below SMA50 (intraday dip
  only) therefore produces no entry until a later genuine cross
  back — there is no "back above" bar to take.
- RSI bands are inclusive on both ends.

No bug fixes requiring re-runs, no PnL-selected tuning.
