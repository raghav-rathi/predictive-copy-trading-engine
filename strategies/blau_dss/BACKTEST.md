# Blau Double Smoothed Stochastic — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793714400000] (2026-03-14 22:00 UTC →
2026-11-03 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP = 40 bars.

**Bar counts used:** BTC 5609, ETH 5609, HYPE 5607.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 897 | 26.8% | -7629.50 | -6.65 | -77.5% | -8.51 | 0.62 |
| ETH | 861 | 28.6% | -5573.53 | -3.59 | -58.2% | -6.47 | 0.74 |
| HYPE | 918 | 30.5% | -5941.72 | -4.43 | -63.7% | -6.47 | 0.71 |
| **Combined** | **2676** | **28.6%** | **-19144.75** | **-6.31** | **-65.0%** | **-7.15** | **0.69** |

Fees: total $13316.16.
Exits: 1826 signal, 850 stop.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Heavy loser, overtrades

Double smoothing did not tame the stochastic: 2,676 trades, negative on every coin, combined MaxDD -65%. Not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
