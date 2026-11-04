# Percentage Volume Oscillator — Backtest

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
| BTC | 410 | 37.8% | -3742.29 | -3.10 | -41.2% | -9.13 | 0.67 |
| ETH | 422 | 41.7% | -1508.29 | -0.96 | -21.1% | -3.57 | 0.88 |
| HYPE | 393 | 44.5% | -988.87 | -0.70 | -31.1% | -2.52 | 0.93 |
| **Combined** | **1225** | **41.3%** | **-6239.45** | **-2.38** | **-25.7%** | **-5.09** | — |

Fees: total $9384.55.
Exits: {'signal': 825, 'stop': 400}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser on all three coins. Volume-momentum crosses do not transfer to price direction on 1h crypto; PF 0.67-0.93 everywhere.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
