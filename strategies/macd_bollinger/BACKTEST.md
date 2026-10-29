# MACD Bollinger — Backtest

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

## Results (shipped config: MACD(12,26,9) with Bollinger
(20, 2) on the MACD line, band-edge re-entry crosses with the
zero-side filter, midline/signal exit, 2xATR stop, 2.5xATR
trail, 168-bar max hold)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor | Fees $ |
|---|---|---|---|---|---|---|---|---|
| BTC | 140 | 32.1% | -$2,377 | -2.41 | -26.5% | -$16.98 | 0.62 | $1,330 |
| ETH | 140 | 33.6% | -$1,933 | -1.87 | -23.6% | -$13.81 | 0.69 | $1,028 |
| HYPE | 137 | 29.9% | -$1,400 | -1.19 | -20.7% | -$10.22 | 0.80 | $669 |
| **Combined** | **417** | **31.9%** | **-$5,711** | — | — | **-$13.70** | — | **$3,026** |

Exits: 320 stop / 97 signal — the stop dominates on every
coin, i.e. most band-edge releases keep running against the
trade rather than mean-reverting to the midline.

## Verdict: loser

-$5,711 across 417 trades, red on all three coins with
Sharpe negative everywhere and profit factor below 0.81 on
every leg. The band-edge release on 1h crypto is not a
mean-reversion edge in this window: the MACD line crossing
back inside its own band more often marks a pause inside a
continuing move than a turn.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled;
  next-bar-open execution vs idealized entry.
- Never tune the shipped parameters on this window.
