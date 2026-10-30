# POC Migration — Backtest

**Data:** Hyperliquid 1h candles read directly from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) — `fetch_candles` was NOT called,
so the cache was not rewritten. Window t in [1773525600000,
1793318400000] (2026-03-14 22:00 UTC → 2026-10-30 00:00 UTC), duplicates
dropped (keep first). $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off. WARMUP = 65 bars.

**Bar counts used:** BTC 5499, ETH 5499, HYPE 5497 — exactly the expected
counts. Before dedup the window held 5505 / 5505 / 5503 rows, i.e. 6
exact-duplicate bars per coin were dropped. First bar BTC/ETH
1773525600000 (2026-03-14 22:00 UTC), HYPE 1773532800000 (2026-03-15
00:00 UTC); last bar all coins 1793318400000 (2026-10-30 00:00 UTC).

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 467 | 37.3% | -$4,646.50 | -3.96 | -48.2% | -$9.95 | 0.62 |
| ETH | 443 | 41.8% | -$1,814.90 | -1.20 | -21.8% | -$4.10 | 0.86 |
| HYPE | 477 | 41.5% | -$3,858.00 | -3.30 | -38.6% | -$8.09 | 0.71 |
| **Combined** | **1,387** | **40.2%** | **-$10,319.41** | **-4.42** | **-34.9%** | **-$7.44** | — |

Fees: BTC $3,666.19, ETH $3,399.64, HYPE $1,879.81 (total $8,945.64).
Exits: 881 signal / 506 stop / 0 max-hold. Combined Sharpe / MaxDD are
computed on the summed $30k three-coin equity curve.

## Verdict: clear loser — do not trade as shipped

Loses heavily on all three coins, with catastrophic drawdowns on BTC
(-48.2%) and HYPE (-38.6%). The failure mode is overtrading: 1,387
trades in ~5,500 bars (a new trade roughly every 12 bars) means the POC
direction flips constantly as heavy bars roll in and out of the 50-bar
window, and each flip exits one trade and often enters the opposite one
into the same noise. Fees alone ($8,946) nearly equal the total loss.
The migration thesis does not survive contact with a rolling-window
step function.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Close-assigned bins are a coarse proxy for true volume-at-price
  (see README limitation).
- Never tune the shipped parameters on this window.
