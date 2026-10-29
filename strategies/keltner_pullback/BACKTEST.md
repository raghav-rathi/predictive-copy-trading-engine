# Keltner Pullback — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`), filtered to the task
window t >= 1773446400000 and t <= 1793145600000
(2026-03-14 00:00 UTC → 2026-10-28 00:00 UTC), $10k start, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee
+ 0.01% slippage per side, funding off. WARMUP=60 bars.

**Actual candle window used (per coin, after filtering):**
the cache's first candle postdates the window's start bound
and the filter caps the end at the bound itself, so the
effective window is narrower than the nominal one:

- BTC: 5,451 bars, first 1773525600000 (2026-03-14 22:00 UTC),
  last 1793145600000 (2026-10-28 00:00 UTC)
- ETH: 5,451 bars, first 1773525600000 (2026-03-14 22:00 UTC),
  last 1793145600000 (2026-10-28 00:00 UTC)
- HYPE: 5,449 bars, first 1773532800000 (2026-03-15 00:00 UTC),
  last 1793145600000 (2026-10-28 00:00 UTC)

Note: `fetch_candles` extended the cache forward during this
run (the cache previously ended 2026-10-27 13:00 UTC). The
unfiltered `scripts/run_strategy_backtest.py` path therefore
includes post-window bars (to Oct 29) and reports slightly
different numbers; the table below is the filtered-window run
and is authoritative.

## Results (shipped config: EMA20 Keltner midline pullback in
an EMA50 trend, 2xATR stop, 3xATR trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor | Fees $ |
|---|---|---|---|---|---|---|---|---|
| BTC | 408 | 20.6% | -$5,552 | -4.85 | -55.6% | -$13.61 | 0.51 | $3,009 |
| ETH | 454 | 18.5% | -$4,499 | -3.35 | -48.5% | -$9.91 | 0.66 | $3,112 |
| HYPE | 391 | 24.0% | -$1,410 | -0.64 | -27.5% | -$3.61 | 0.89 | $1,892 |
| **Combined** | **1,253** | **20.9%** | **-$11,461** | — | — | **-$9.15** | — | **$8,012** |

Exits: 865 signal (opposite midline cross) / 388 stop — the
trade reverses on the next midline touch in over two-thirds
of cases. That is the strategy whipsawing, not exiting
cleanly.

## Verdict: loser, badly

-$11,461 across 1,253 trades, red on every coin, win rates
18–24%, profit factors 0.51–0.89, and drawdowns (-55.6% BTC,
-48.5% ETH) that would have blown up a live book several
times over. The midline-cross pullback on 1h crypto is
predominantly chop. Do not trade this as shipped.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.
