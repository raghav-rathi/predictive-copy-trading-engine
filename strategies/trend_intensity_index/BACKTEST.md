# Trend Intensity Index — Backtest

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
| BTC | 11 | 45.5% | 488.13 | 1.24 | -3.0% | 44.38 | 2.08 |
| ETH | 8 | 50.0% | 538.25 | 1.41 | -2.3% | 67.28 | 2.81 |
| HYPE | 8 | 50.0% | 441.84 | 1.22 | -2.4% | 55.23 | 2.36 |
| **Combined** | **27** | **48.1%** | **1468.21** | **1.88** | **-2.1%** | **54.38** | **2.37** |

Fees: total $194.01.
Exits: 27 stop.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Winner on all three coins — but thin

Green on BTC, ETH and HYPE with the batch's best Sharpe (1.88 combined) and shallowest drawdown (-2.1%), but on only 27 trades in ~7.5 months: the 80/20 TII thresholds fire rarely. Promising as a low-frequency regime filter, not a standalone tradeable system on this evidence alone; it does NOT clear a live gate on trade count.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
