# Pring Special K — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793714400000] (2026-03-14 22:00 UTC →
2026-11-03 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP = 50 bars.

**Bar counts used:** BTC 5609, ETH 5609, HYPE 5607.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 320 | 33.8% | -2576.91 | -1.68 | -31.8% | -8.05 | 0.80 |
| ETH | 317 | 35.0% | -686.36 | -0.25 | -20.7% | -2.17 | 0.95 |
| HYPE | 297 | 37.0% | 3805.21 | 2.04 | -16.4% | 12.81 | 1.24 |
| **Combined** | **934** | **35.2%** | **541.93** | **0.29** | **-14.9%** | **0.58** | **1.01** |

Fees: total $8382.87.
Exits: 285 signal, 649 stop.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Mixed: HYPE win, BTC/ETH losses

Combined +$541.93 is carried entirely by HYPE (+$3,805, Sharpe 2.04) while BTC (-$2,577) and ETH (-$686) lose. A coin-dependent print, not a consistent edge — not a live gate.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
