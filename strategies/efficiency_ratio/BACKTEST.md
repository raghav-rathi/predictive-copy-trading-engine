# Efficiency Ratio — Backtest

**Data:** Hyperliquid 1h candles read directly from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) — `fetch_candles` was NOT called,
so the cache was not rewritten. Window t in [1773525600000,
1793318400000] (2026-03-14 22:00 UTC → 2026-10-30 00:00 UTC), duplicates
dropped (keep first). $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off. WARMUP = 30 bars.

**Bar counts used:** BTC 5499, ETH 5499, HYPE 5497. Before dedup the
window held 5504 / 5504 / 5502 rows, i.e. 5 exact-duplicate bars per
coin were dropped. First bar BTC/ETH 1773525600000 (2026-03-14 22:00
UTC), HYPE 1773532800000 (2026-03-15 00:00 UTC); last bar all coins
1793318400000 (2026-10-30 00:00 UTC).

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 121 | 29.8% | -$2,074.05 | -2.08 | -23.7% | -$17.14 | 0.65 |
| ETH | 126 | 38.1% | +$1,934.21 | +1.62 | -11.6% | +$15.35 | 1.33 |
| HYPE | 117 | 36.8% | +$1,735.93 | +1.43 | -14.1% | +$14.84 | 1.31 |
| **Combined** | **364** | **34.9%** | **+$1,596.09** | **+0.74** | **-7.7%** | **+$4.38** | **1.09** |

Fees: BTC $1,294.81, ETH $1,300.93, HYPE $722.58 (total $3,318.32).
Exits: 314 stop / 50 signal / 0 max-hold — the stop manages 86% of
trades. Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: mildly green, not a demonstrated edge

+$1,596 across 364 trades on $30k starting capital is 5.3% over ~7.5
months before funding, with a profit factor of just 1.09 and a BTC leg
that lost -$2,074 with a -23.7% drawdown. The green ETH/HYPE legs do
not offset a coin that bleeds this badly; this reads as noise around
breakeven, not a tradeable edge.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- The ER gate is weak against spike-driven readings (see README).
- Never tune the shipped parameters on this window.
