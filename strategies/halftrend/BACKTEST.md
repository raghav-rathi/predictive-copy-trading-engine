# HalfTrend — Backtest

**Data:** Hyperliquid 1h candles read directly from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) — `fetch_candles` was NOT called,
so the cache was not rewritten. Window t in [1773525600000,
1793318400000] (2026-03-14 22:00 UTC → 2026-10-30 00:00 UTC), duplicates
dropped (keep first). $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off. WARMUP = 110 bars.

**Bar counts used:** BTC 5499, ETH 5499, HYPE 5497 — exactly the expected
counts. Before dedup the window held 5504 / 5504 / 5502 rows, i.e. 5
exact-duplicate bars per coin were dropped. First bar BTC/ETH
1773525600000 (2026-03-14 22:00 UTC), HYPE 1773532800000 (2026-03-15
00:00 UTC); last bar all coins 1793318400000 (2026-10-30 00:00 UTC).

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 233 | 31.3% | -$2,887.46 | -2.02 | -31.5% | -$12.39 | 0.71 |
| ETH | 255 | 34.5% | -$1,390.17 | -0.75 | -22.8% | -$5.45 | 0.88 |
| HYPE | 253 | 37.5% | +$1,759.60 | +1.05 | -12.8% | +$6.95 | 1.14 |
| **Combined** | **741** | **34.5%** | **-$2,518.04** | **-0.61** | **-16.1%** | **-$3.40** | **0.93** |

Fees: BTC $2,248.92, ETH $2,063.57, HYPE $1,465.98 (total $5,778.47).
Exits: 588 stop / 153 signal / 0 max-hold — the stop manages ~79% of
trades. Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: loser overall, HYPE-only green

-$2,518 across 741 trades on $30k starting capital over ~7.5 months
before funding, with a 34.5% win rate and a 0.93 profit factor, is a
loser, not an edge. HYPE alone was green (+$1,760, Sharpe +1.05), but
one green coin out of three with BTC at -31.5% max drawdown does not
rescue the strategy. The amplitude-2 state machine flips too often in
chop and the stop, not the flip, decides most trades.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.
- Paper only, no live execution.
