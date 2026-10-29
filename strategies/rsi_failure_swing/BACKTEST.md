# RSI Failure Swing — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`), filtered to the task
window t >= 1773446400000 and t <= 1793145600000
(2026-03-14 00:00 UTC → 2026-10-28 00:00 UTC), $10k start, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee +
0.01% slippage per side, funding off. WARMUP=50 bars.

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
includes ~37 extra post-window BTC bars (to Oct 29) and reports
slightly different numbers (BTC 118 trades, -$1,441); the table
below is the filtered-window run and is authoritative.

## Results (shipped config: RSI(14) failure swings, 30/70
thresholds, 2-bar-lagged pivots, 2xATR stop, 2.5xATR trail,
168-bar max hold)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor | Fees $ |
|---|---|---|---|---|---|---|---|---|
| BTC | 33 | 21.2% | -$1,187 | -2.33 | -11.9% | -$35.97 | 0.44 | $341 |
| ETH | 38 | 39.5% | -$359 | -0.58 | -6.1% | -$9.45 | 0.75 | $281 |
| HYPE | 29 | 27.6% | -$764 | -1.50 | -8.2% | -$26.36 | 0.50 | $138 |
| **Combined** | **100** | **30.0%** | **-$2,310** | — | — | **-$23.10** | — | **$760** |

Exits: 94 stop / 6 signal — the opposite-swing exit almost
never fires; the stop does nearly all the work.

## Verdict: loser

-$2,310 across 100 trades, red on every coin, win rates
21–40% and profit factors 0.44–0.75. On 1h crypto, an RSI
swing-extreme break is a continuation print far more often
than a turn. Do not trade this as shipped.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.
