# Chikou Span Cross — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794232800000) (2026-03-14 22:00 UTC →
2026-11-09 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5752, ETH 5752, HYPE 5750.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 527 | 24.7% | -5691.09 | -4.63 | -59.5% | -10.80 | 0.55 |
| ETH | 549 | 28.2% | -3810.71 | -2.42 | -46.8% | -6.94 | 0.75 |
| HYPE | 466 | 33.7% | -1340.01 | -0.72 | -25.4% | -2.88 | 0.91 |
| **Combined** | **1542** | **28.7%** | **-10841.82** | **-3.32** | **-39.5%** | **-7.03** | **0.74** |

Fees: total $10249.27.
Exits: {'signal': 877, 'stop': 665}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser (-$10,841.82, PF 0.74) on 1,542 trades — a clear NO-GO

A 26-period momentum cross on 1h crypto whipsaws relentlessly: 1,542
trades in ~8 months, a 28.7% win rate, negative on all three coins,
and a combined -39.5% drawdown. Fees alone were $10,249 — nearly the
size of the loss. The signal exit fired 877 times, so the rule works
as coded; the edge simply is not there. Do not trade this standalone.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
