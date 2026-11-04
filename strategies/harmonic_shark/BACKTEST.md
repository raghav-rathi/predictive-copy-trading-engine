# Harmonic Shark — Backtest

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
| BTC | 9 | 55.6% | 332.92 | 0.93 | -2.9% | 36.99 | 2.16 |
| ETH | 7 | 57.1% | -37.71 | -0.11 | -1.9% | -5.39 | 0.86 |
| HYPE | 10 | 40.0% | -26.48 | -0.07 | -3.2% | -2.65 | 0.93 |
| **Combined** | **26** | **50.0%** | **268.73** | **0.48** | **-1.9%** | **10.34** | — |

Fees: total $211.25.
Exits: {'stop': 26}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Only combined-green strategy of the batch (+$269), but thin: 26 trades, green only on BTC, red on ETH/HYPE. Does NOT clear a live gate.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
