# Relative Strength Breakout — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`), filter window
2026-03-14 → 2026-10-28 (t >= 1773446400000 and t <=
1793145600000), $10k start, 1% risk per trade on the 2xATR
stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off. WARMUP=30 bars. BTC benchmark loaded from the
shipped cache by `add_indicators` (see README.md for the
sourcing order); the run below uses the standard
single-frame path, so it is exactly reproducible via the
harness.

**Actual candle window used (the cache, not the filter
bounds):** BTC and ETH first candle 2026-03-14 22:00 UTC
(t=1773525600000), HYPE first candle 2026-03-15 00:00 UTC
(t=1773532800000); all coins last candle 2026-10-27 13:00
UTC (t=1793106000000). The cache starts 22 hours after the
filter's lower bound and ends ~11 hours before its upper
bound — no candles were added or shifted; the window is
reported as actually returned.

## Results (shipped config: coin/BTC ratio breakout of the
prior 20-bar range, mean-fade exit, 2xATR stop, 2.5xATR trail,
168-bar max hold)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 0 (benchmark) | — | $0 | — | — | — | — |
| ETH | 277 | 33.9% | -$2,559 | -1.91 | -29.6% | -$9.24 | 0.75 |
| HYPE | 254 | 38.2% | -$1,051 | -0.70 | -17.7% | -$4.14 | 0.90 |
| **Combined (traded legs only)** | **531** | **36.0%** | **-$3,610** | — | — | **-$6.80** | — |

Fees: ETH $2,111, HYPE $1,284 (total $3,394). Traded-leg
exits: 334 stop / 197 signal (mean-fade).

**BTC leg note:** BTC is the benchmark, so its ratio is 1 by
construction, its prior 20-bar range is flat, and no breakout
can ever fire (0 entries, 0 trades, verified in the unit
tests). It is reported here as benchmark/no-trade and
EXCLUDED from the combined total — counting it as a flat leg
would dilute the traded-leg loss without changing it.

## Verdict: loser

-$3,610 across 531 traded-leg trades, negative on both traded
legs. Ratio breakouts fail back through the stop more often
than they extend, and the mean-fade exit rescues only a
minority of trades.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled;
  next-bar-open execution vs idealized entry.
- The BTC cache carries 5 duplicated timestamps (exact
  duplicate rows); the indicator loader dedupes on `t`
  before joining, so no rows are multiplied. The CSVs
  themselves were not edited.
- Never tune the shipped parameters on this window.
