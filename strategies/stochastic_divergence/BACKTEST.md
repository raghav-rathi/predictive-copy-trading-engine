# Stochastic Divergence — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793973600000] (2026-03-14 22:00 UTC →
2026-11-06 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5681, ETH 5681, HYPE 5679.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 267 | 44.6% | -2913.50 | -2.66 | -30.6% | -10.91 | 0.71 |
| ETH | 240 | 45.8% | -1494.66 | -1.28 | -19.1% | -6.23 | 0.85 |
| HYPE | 240 | 51.2% | 247.72 | 0.30 | -8.8% | 1.03 | 1.03 |
| **Combined** | **747** | **47.1%** | **-4160.44** | **-1.93** | **-14.8%** | **-5.57** | — |

Fees: total $5530.74.
Exits: {'stop': 403, 'signal': 344}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser combined, 747 trades, -$4,160.44, PF 0.86. Best win rate of the batch (47.1%) but losers outweigh winners; only HYPE is green (+$247.72, PF 1.03 — breakeven noise).

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
