# Multi-Timeframe Stack — Backtest

**Data:** Hyperliquid 1h candles read directly from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) — `fetch_candles` was NOT called,
so the cache was not rewritten. Window t in [1773525600000,
1793318400000] (2026-03-14 22:00 UTC → 2026-10-30 00:00 UTC), duplicates
dropped (keep first). $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off. WARMUP = 230 bars.

**Bar counts used:** BTC 5499, ETH 5499, HYPE 5497 — exactly the expected
counts. Before dedup the window held 5505 / 5505 / 5503 rows, i.e. 6
exact-duplicate bars per coin were dropped. First bar BTC/ETH
1773525600000 (2026-03-14 22:00 UTC), HYPE 1773532800000 (2026-03-15
00:00 UTC); last bar all coins 1793318400000 (2026-10-30 00:00 UTC).

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 110 | 32.7% | +$176.20 | +0.35 | -10.9% | +$1.60 | 1.03 |
| ETH | 124 | 30.6% | +$295.06 | +0.41 | -14.6% | +$2.38 | 1.06 |
| HYPE | 99 | 28.3% | +$689.32 | +0.69 | -9.0% | +$6.96 | 1.15 |
| **Combined** | **333** | **30.6%** | **+$1,160.58** | **+0.52** | **-9.0%** | **+$3.49** | — |

Fees: BTC $1,361.83, ETH $1,184.15, HYPE $553.43 (total $3,099.40).
Exits: 260 stop / 73 signal / 0 max-hold — the stop still manages most
trades despite the trend filter. Combined Sharpe / MaxDD are computed
on the summed $30k three-coin equity curve.

## Verdict: mildly green, not a demonstrated edge

+$1,161 across 333 trades on $30k starting capital is 3.9% over ~7.5
months before funding — with a ~31% win rate, profit factors barely
above 1.0, and the stop managing 78% of exits, this reads as noise
around breakeven, not a tradeable edge. It is the only green strategy
of batch 21, but "least bad" is not a recommendation.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Grouping is positional, not wall-clock (see README limitation).
- Never tune the shipped parameters on this window.
