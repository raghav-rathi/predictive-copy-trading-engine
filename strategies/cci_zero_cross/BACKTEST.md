# CCI Zero Cross — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`), filtered to the batch-20
window t >= 1773446400000 and t <= 1793145600000, $10k start,
1% risk per trade on the 2xATR stop, 3x leverage cap, 0.045%
fee + 0.01% slippage per side, funding off. WARMUP=60 bars.

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

## Results (shipped config: CCI(20) zero crosses filtered by
SMA(50) trend, opposite-zero-cross exit, 2xATR stop, 3xATR
trail, 240-bar max hold)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor | Fees $ |
|---|---|---|---|---|---|---|---|---|
| BTC | 309 | 25.6% | -$4,217 | -3.48 | -43.8% | -$13.65 | 0.62 | $2,703 |
| ETH | 333 | 24.0% | -$3,356 | -2.46 | -40.0% | -$10.08 | 0.71 | $2,545 |
| HYPE | 278 | 25.2% | -$2,353 | -1.79 | -25.4% | -$8.46 | 0.74 | $1,234 |
| **Combined** | **920** | **24.9%** | **-$9,926** | — | — | **-$10.79** | — | **$6,482** |

Exits: 563 signal / 357 stop — the zero-cross exit fires
often, but a 25% win rate means most with-trend crosses are
whipsaws that reverse straight back through zero, and the
losers are large enough (357 stops) to swamp the winners.

## Verdict: loser

-$9,926 across 920 trades, the worst win rate of this batch
(24.9%) and red on all three coins, with BTC down -42.2% of
starting equity and a -43.8% max drawdown. The SMA(50) filter
does not save the zero cross: on 1h crypto, CCI crosses zero
far more often as noise than as regime change.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled;
  next-bar-open execution vs idealized entry.
- Never tune the shipped parameters on this window.
