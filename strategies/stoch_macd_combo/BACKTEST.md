# Stochastic + MACD Combo — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793800800000] (2026-03-14 22:00 UTC →
2026-11-04 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5633, ETH 5633, HYPE 5631.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 22 | 45.5% | -117.64 | -0.57 | -3.1% | -5.35 | 0.81 |
| ETH | 23 | 30.4% | -460.93 | -1.93 | -6.7% | -20.04 | 0.33 |
| HYPE | 22 | 27.3% | -493.84 | -2.01 | -6.3% | -22.45 | 0.39 |
| **Combined** | **67** | **34.3%** | **-1072.41** | **-2.60** | **-4.6%** | **-16.01** | — |

Fees: total $560.87.
Exits: {'signal': 54, 'stop': 13}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser on all three coins (67 trades, PF 0.33-0.81). The oversold %K cross + MACD filter still buys into falling knives on 1h crypto.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
