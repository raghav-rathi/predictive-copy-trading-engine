# Rainbow Moving Average — Backtest

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
| BTC | 612 | 21.9% | -6270.30 | -5.24 | -64.2% | -10.25 | 0.59 |
| ETH | 635 | 23.0% | -4842.34 | -3.26 | -50.8% | -7.63 | 0.71 |
| HYPE | 613 | 26.4% | -2887.66 | -1.72 | -29.5% | -4.71 | 0.82 |
| **Combined** | **1860** | **23.8%** | **-14000.30** | **-4.85** | **-46.7%** | **-7.53** | — |

Fees: total $11490.93.
Exits: {'signal': 1254, 'stop': 606}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Worst of the batch: -$14,000 across 1,860 trades, MaxDD -46.7%. Breaking out of the whole 22-EMA ribbon on 1h bars is a whipsaw machine; the ribbon lags and re-entries stack losses.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
