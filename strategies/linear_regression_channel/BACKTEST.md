# Linear Regression Channel — Backtest

**Data:** Hyperliquid 1h candles read directly from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) — `fetch_candles` was NOT called,
so the cache was not rewritten. Window t in [1773525600000,
1793318400000] (2026-03-14 22:00 UTC → 2026-10-30 00:00 UTC), duplicates
dropped (keep first). $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off. WARMUP = 55 bars.

**Bar counts used:** BTC 5499, ETH 5499, HYPE 5497. Before dedup the
window held 5504 / 5504 / 5502 rows, i.e. 5 exact-duplicate bars per
coin were dropped. First bar BTC/ETH 1773525600000 (2026-03-14
22:00 UTC), HYPE 1773532800000 (2026-03-15 00:00 UTC); last bar all
coins 1793318400000 (2026-10-30 00:00 UTC).

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 170 | 44.7% | -$1,182.71 | -1.04 | -17.8% | -$6.96 | 0.84 |
| ETH | 155 | 45.8% | -$885.13 | -0.83 | -13.5% | -$5.71 | 0.87 |
| HYPE | 167 | 44.3% | -$1,445.14 | -1.55 | -17.7% | -$8.65 | 0.79 |
| **Combined** | **492** | **44.9%** | **-$3,512.98** | **-1.81** | **-14.3%** | **-$7.14** | **0.83** |

Fees: BTC $1,799.95, ETH $1,230.52, HYPE $796.05 (total $3,826.52).
Exits: 273 stop / 219 signal / 0 max-hold. Combined Sharpe / MaxDD
are computed on the summed $30k three-coin equity curve.

## Verdict: loser on all three coins

-$3,513 across 492 trades, negative on every coin, combined Sharpe
-1.81 — the worst of this batch despite the highest win rate
(44.9%). That combination is the tell: the midline exit banks
small reversion wins while the stop absorbs full trend-continuation
losses, so a good hit rate still loses money. Fading 2-sigma
extensions in a trending ~7.5-month crypto window is structurally
against the trade. Not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- No trend filter: fades are taken with equal size in trends and
  ranges alike.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
