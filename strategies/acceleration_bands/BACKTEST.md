# Acceleration Bands — Backtest

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
| BTC | 130 | 23.1% | -1957.85 | -2.58 | -22.3% | -15.06 | 0.54 |
| ETH | 128 | 22.7% | -2331.76 | -3.19 | -25.4% | -18.22 | 0.48 |
| HYPE | 121 | 20.7% | -725.44 | -0.82 | -8.7% | -6.00 | 0.81 |
| **Combined** | **379** | **22.2%** | **-5015.05** | **-3.49** | **-17.4%** | **-13.23** | — |

Fees: total $2697.40.
Exits: {'signal': 281, 'stop': 98}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser on all three coins, worst combined Sharpe of the batch's band systems (-3.49). Two-close breakout entries chase range expansion that mean-reverts on 1h crypto.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
