# Harmonic Butterfly — Backtest

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
| BTC | 6 | 50.0% | -100.05 | -0.37 | -3.8% | -16.68 | 0.66 |
| ETH | 4 | 50.0% | 5.66 | 0.04 | -1.7% | 1.42 | 1.04 |
| HYPE | 3 | 66.7% | -68.72 | -0.46 | -2.1% | -22.91 | 0.34 |
| **Combined** | **13** | **53.8%** | **-163.11** | **-0.43** | **-1.8%** | **-12.55** | — |

Fees: total $126.21.
Exits: {'stop': 13}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser, but thin: 13 trades in ~7.5 months. The 0.786/1.272-ratio filter fires rarely and the few completions do not pay.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
