# Point & Figure — Backtest

**Data:** Hyperliquid 1h candles read directly from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) — `fetch_candles` was NOT called,
so the cache was not rewritten. Window t in [1773525600000,
1793318400000] (2026-03-14 22:00 UTC → 2026-10-30 00:00 UTC), duplicates
dropped (keep first). $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off. WARMUP = 30 bars.

**Bar counts used:** BTC 5499, ETH 5499, HYPE 5497 — exactly the expected
counts. Before dedup the window held 5505 / 5505 / 5503 rows, i.e. 6
exact-duplicate bars per coin were dropped. First bar BTC/ETH
1773525600000 (2026-03-14 22:00 UTC), HYPE 1773532800000 (2026-03-15
00:00 UTC); last bar all coins 1793318400000 (2026-10-30 00:00 UTC).

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 30 | 23.3% | -$406.85 | -0.62 | -5.2% | -$13.56 | 0.68 |
| ETH | 48 | 29.2% | -$365.93 | -0.38 | -9.8% | -$7.62 | 0.87 |
| HYPE | 108 | 28.7% | -$808.25 | -0.69 | -14.9% | -$7.48 | 0.84 |
| **Combined** | **186** | **28.0%** | **-$1,581.03** | **-0.91** | **-7.8%** | **-$8.50** | — |

Fees: BTC $255.81, ETH $325.92, HYPE $430.59 (total $1,012.31).
Exits: 174 stop / 12 signal / 0 max-hold — the stop, not the reversal
exit, manages nearly every trade. Combined Sharpe / MaxDD are computed
on the summed $30k three-coin equity curve.

## Verdict: loser

Loses on all three coins with a sub-30% win rate. The double-top /
double-bottom breakout on 1h bars with 1% boxes is a lagging breakout
signal: by the time a new X column exceeds the prior X high, the move is
usually extended, and the 2xATR stop absorbs the reversal. No edge
demonstrated as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 1% boxes on 1h bars are coarse (see README limitation); daily-bar P&F
  would be a different strategy, not a parameter tweak.
- Never tune the shipped parameters on this window.
