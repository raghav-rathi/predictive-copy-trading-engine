# FRAMA Trend — Backtest

**Data:** Hyperliquid 1h candles read directly from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) — `fetch_candles` was NOT called,
so the cache was not rewritten. Window t in [1773525600000,
1793318400000] (2026-03-14 22:00 UTC → 2026-10-30 00:00 UTC), duplicates
dropped (keep first). $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off. WARMUP = 40 bars.

**Bar counts used:** BTC 5499, ETH 5499, HYPE 5497 — exactly the expected
counts. Before dedup the window held 5504 / 5504 / 5502 rows, i.e. 5
exact-duplicate bars per coin were dropped. First bar BTC/ETH
1773525600000 (2026-03-14 22:00 UTC), HYPE 1773532800000 (2026-03-15
00:00 UTC); last bar all coins 1793318400000 (2026-10-30 00:00 UTC).

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 1020 | 20.5% | -$8,210.33 | -8.01 | -82.3% | -$8.05 | 0.56 |
| ETH | 1056 | 22.1% | -$6,707.98 | -5.02 | -67.6% | -$6.35 | 0.67 |
| HYPE | 990 | 23.5% | -$4,918.44 | -3.22 | -51.1% | -$4.97 | 0.77 |
| **Combined** | **3066** | **22.0%** | **-$19,836.75** | **-6.74** | **-66.4%** | **-$6.47** | **0.67** |

Fees: BTC $5,509.52, ETH $5,344.21, HYPE $3,496.94 (total $14,350.67).
Exits: 2233 signal / 833 stop / 0 max-hold. Combined Sharpe / MaxDD
are computed on the summed $30k three-coin equity curve.

## Verdict: clear loser — the fast FRAMA whipsaws, as warned

-$19,837 across 3066 trades on $30k starting capital over ~7.5 months
before funding, with a 22% win rate, a 0.67 profit factor, and a -66%
combined max drawdown, is a decisive loser on every coin. The
mechanism explains it: at N = 16, alpha approaches 1 in trends, so
FRAMA hugs price and crosses fire on ordinary noise — over 1,000
trades per coin, most exited by the next opposite cross. This matches
the source's own caution that the fast FRAMA tracks price too well
and whipsaws. Do not trade this configuration.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.
- Paper only, no live execution.
