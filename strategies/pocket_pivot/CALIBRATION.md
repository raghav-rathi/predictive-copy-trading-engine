# Pocket Pivot — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Day length | 24 bars | 1h bars; one trading day = 24 hourly bars. |
| Volume window | 240 bars (10 trading days) | Morales/Kacher: volume must exceed the largest down-day volume of the previous 10 days. |
| Volume test | v > max volume of any DOWN bar (c < o) in previous 240 bars, excluding current bar | Core pocket-pivot test, per LuxAlgo / New Trader U summaries of the rule. |
| Fast MA | EMA(240) | 10-day MA analogue (240 hourly bars). EMA chosen over SMA because the shared `strategies.base.ema` primitive is the batch convention and EMAs are the standard O'Neil-style trend filter; see deviation note. |
| Slow MA | EMA(1200) | 50-day MA analogue (1200 hourly bars). |
| EMA rising | EMA(240)[i] > EMA(240)[i-24] | 1-trading-day rise check. |
| Extension limit | close < 1.10 * EMA(240) | "Not extended" qualifier; 10% above the 10-day line is the standard O'Neil/Morales extension guard. |
| Long exit | close < EMA(240) | Base broken / support lost. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 240 bars | Batch-standard risk layer; max hold 240 bars = 10 trading days, matching the setup's own horizon. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 1250 | EMA(1200) needs 1200 bars + margin; also covers the 240-bar volume window. |

## Spec deviations

1. **EMA instead of SMA for the 10-day / 50-day lines.** The source
   describes the pocket pivot against 10-day and 50-day moving averages
   without specifying EMA vs SMA. EMA was used (via the shared
   `strategies.base.ema` primitive, the batch convention for trend
   filters). An SMA variant would lag more and change entry counts
   slightly; the choice was fixed before seeing results and not
   revisited.
2. **Volume window uses `min_periods=1`.** `max_down_vol_240` is defined
   as soon as any down bar exists in history, rather than staying NaN
   for the first 240 bars. The value is always the max over the
   *available* previous bars (max 240). Trading is gated by WARMUP
   1250 anyway, so no signal can fire on a partial window.
3. **"Base" context is trend filters only.** The original method also
   requires the stock to be basing (a chart-pattern / base-count
   judgement). That discretionary pattern read has no faithful
   mechanical translation and was replaced by the spec's own mechanical
   qualifiers (close above EMA(240), EMA(240) above EMA(1200), EMA(240)
   rising, not extended). This is the closest faithful mechanical
   version of the setup.
4. **No "volume dry-up" / base-count rules.** Ancillary Morales/Kacher
   pocket-pivot rules (e.g. prior base structure, volume dry-up before
   the pivot) are discretionary and were not implemented; only the
   volume test plus the listed qualifiers define the entry.

No bug fixes requiring re-runs, no PnL-selected tuning.
