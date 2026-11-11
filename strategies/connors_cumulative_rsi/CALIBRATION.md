# Connors Cumulative RSI — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| RSI period | 2 | Connors' short-term pullback gauge; RSI(2) swings hard enough to make the cumulative sum move. |
| Cumulative sum | sum of (RSI(2) − 50) over all bars, never reset | The spec's definition of Cumulative RSI as implemented here. |
| Long entry level | cum_rsi crosses above −100 | Connors' published cumulative extreme on the downside. |
| Short entry level | cum_rsi crosses below +100 | Connors' published cumulative extreme on the upside. |
| Exit level | cum_rsi crosses 0 | Mean reversion complete once the cumulative sum is back to neutral. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | RSI(2) needs 2 bars; 60 bars of margin before any signal can fire. |

## Spec deviations

1. **Cumulative over ALL bars, not a 2-day window.** The published
   Connors/Alvarez system sums only the last 2 RSI(2) readings
   (a 2-day cumulative RSI, range 0–200, with entry below 35/50 and
   exit on RSI(2) above 65, long-only above the 200-day SMA). This
   batch's spec instead defines `cum_rsi` as the running sum of
   (RSI(2) − 50) over the entire history with ±100 entry levels and
   a 0 exit, long/short symmetric, no SMA filter. The spec was
   implemented exactly as written; the published 2-day variant is a
   different, bounded indicator and was not substituted.
2. **No 200-day SMA trend filter.** The published system trades longs
   only above the 200-day SMA. The spec omits it, so none was added.
3. **RSI(2) first-bar value is 0.0.** The shared `strategies.base.rsi`
   fills its initial NaN with 0.0, so `cum_rsi` starts at −50 on bar 0
   and is defined from the first bar. Trading is gated by WARMUP 60
   anyway.
4. **History-length drift.** Because the sum never resets, `cum_rsi`
   drifts with series length: on a 5,800-bar window it can sit far
   outside ±100 for long stretches, so entries cluster after long
   one-sided runs and can be rare. This is inherent to the spec's
   definition and is documented in the README rather than "fixed"
   by windowing the sum.

No bug fixes requiring re-runs, no PnL-selected tuning.
