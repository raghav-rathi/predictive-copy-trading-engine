# Connors Cumulative RSI

Larry Connors & Cesar Alvarez's Cumulative RSI (*High Probability ETF
Trading*, 2009): take Wilder RSI(2) and cumulate it — the running sum
of (RSI(2) − 50) over all bars, never reset. Sustained oversold
readings drag the sum deep negative; sustained overbought readings
push it deep positive. Entries fire when the sum recovers back
through Connors' published extremes.

## Rules

- **Indicator:** RSI(2) (Wilder), `cum_rsi = cumsum(RSI(2) − 50)`,
  never reset.
- **Long entry:** `cum_rsi` crosses above −100 from below.
- **Short entry:** `cum_rsi` crosses below +100 from above.
- **Long exit:** `cum_rsi` crosses above 0.
- **Short exit:** `cum_rsi` crosses below 0.
- ATR stop / trail from the risk layer also applies; max hold 120 bars.

All computation is causal, so signals on bar i use only data through
bar i's close.

**Warning:** the cumulative sum drifts with history length — the
longer the series, the further `cum_rsi` can wander from zero. The
±100 levels are Connors' published extremes on the cumulative scale,
not bounds of a stationary oscillator; on a long 1h crypto series the
sum can sit far outside ±100 for extended stretches.

## Source

- Larry Connors & Cesar Alvarez, *High Probability ETF Trading*
  (2009); also *Short Term Trading Strategies That Work* (2009)
- Cumulative RSI system summary: https://trader.autochartist.com/cumulative-rsi-system/
- Trading Setups Review, "Cumulative RSI": https://www.tradingsetupsreview.com/cumulative-rsi/

Paper only, no live execution.
