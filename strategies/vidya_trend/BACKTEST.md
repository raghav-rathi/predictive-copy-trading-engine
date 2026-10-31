# VIDYA Trend — Backtest

**Data:** Hyperliquid 1h candles read directly from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) — `fetch_candles` was NOT called,
so the cache was not rewritten. Window t in [1773525600000,
1793318400000] (2026-03-14 22:00 UTC → 2026-10-30 00:00 UTC), duplicates
dropped (keep first). $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off. WARMUP = 30 bars.

**Bar counts used:** BTC 5499, ETH 5499, HYPE 5497 — exactly the expected
counts. Before dedup the window held 5504 / 5504 / 5502 rows, i.e. 5
exact-duplicate bars per coin were dropped. First bar BTC/ETH
1773525600000 (2026-03-14 22:00 UTC), HYPE 1773532800000 (2026-03-15
00:00 UTC); last bar all coins 1793318400000 (2026-10-30 00:00 UTC).

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 404 | 21.5% | -$4,117.78 | -3.20 | -44.8% | -$10.19 | 0.67 |
| ETH | 465 | 19.6% | -$3,836.25 | -2.91 | -45.7% | -$8.25 | 0.71 |
| HYPE | 434 | 20.0% | -$2,564.44 | -1.87 | -28.9% | -$5.91 | 0.79 |
| **Combined** | **1303** | **20.3%** | **-$10,518.47** | **-3.67** | **-37.8%** | **-$8.07** | **0.72** |

Fees: BTC $3,863.53, ETH $3,386.41, HYPE $1,910.63 (total $9,160.56).
Exits: 749 signal / 554 stop / 0 max-hold. Combined Sharpe / MaxDD
are computed on the summed $30k three-coin equity curve.

## Verdict: loser on every coin

-$10,518 across 1303 trades on $30k starting capital over ~7.5 months
before funding, with a 20.3% win rate and a 0.72 profit factor, is a
loser on all three coins with no green coin to argue from. Crosses
fire often (~430 per coin) and most fail: the adaptive smoothing
neither tracks fast trends tightly enough nor freezes usefully in
chop on 1h bars. Do not trade this configuration.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.
- Paper only, no live execution.
