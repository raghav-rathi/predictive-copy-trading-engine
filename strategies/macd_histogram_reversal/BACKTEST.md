# MACD Histogram Reversal — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`), filtered to the batch-20
window t >= 1773446400000 and t <= 1793145600000, $10k start,
1% risk per trade on the 2xATR stop, 3x leverage cap, 0.045%
fee + 0.01% slippage per side, funding off. WARMUP=50 bars.

**Actual candle window used:** the requested window is
2026-03-14 00:00 UTC → 2026-10-28 00:00 UTC
(t 1773446400000–1793145600000). The cache starts later than
the window start, so the filtered run covers: BTC/ETH first
candle 1773525600000 (2026-03-14 22:00 UTC), HYPE first candle
1773532800000 (2026-03-15 00:00 UTC), all coins last candle
1793145600000 (2026-10-28 00:00 UTC) — i.e. the run reaches
exactly the requested window end. Note: the cache was extended
forward by another process during this build (it initially
ended 2026-10-27 13:00 UTC); the numbers below are from the
re-run on the extended cache and therefore cover the full
requested window. (The `scripts/run_strategy_backtest.py` path
uses `fetch_candles` without the window filter, so it would
include post-Oct-28 bars and would NOT reproduce these
numbers; the numbers below come from the equivalent filtered
inline run described above.)

## Results (shipped config: Elder histogram slope flips with
the sign filter — trough flip below zero / peak flip above
zero, opposite-flip or zero-cross exit, 2xATR stop, 2xATR
trail, 72-bar max hold)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor | Fees $ |
|---|---|---|---|---|---|---|---|---|
| BTC | 602 | 34.9% | -$6,522 | -5.41 | -66.7% | -$10.83 | 0.58 | $3,803 |
| ETH | 598 | 34.6% | -$5,366 | -3.79 | -56.3% | -$8.97 | 0.70 | $3,461 |
| HYPE | 644 | 37.1% | -$6,712 | -6.34 | -68.0% | -$10.42 | 0.56 | $1,775 |
| **Combined** | **1,844** | **35.6%** | **-$18,600** | — | — | **-$10.09** | — | **$9,039** |

Exits: 1,193 stop / 651 signal — two-thirds of trades end at
the stop. The histogram flips constantly (1,844 trades, the
highest count in this batch), and each flip is a coin toss
with a 2xATR stop attached: the strategy trades noise at
maximum frequency.

## Verdict: loser — and the worst in this batch

-$18,600 across 1,844 trades, red on all three coins with
Sharpe between -3.79 and -6.34 and max drawdowns of -56% to
-68% of starting equity. The Elder slope flip without a
stronger filter (e.g. requiring the flip to occur at a
histogram extreme, or confirming with the MACD line's own
direction) is untradeable on 1h crypto: it fires on every
local wiggle of a second-derivative series.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled;
  next-bar-open execution vs idealized entry.
- Never tune the shipped parameters on this window.
