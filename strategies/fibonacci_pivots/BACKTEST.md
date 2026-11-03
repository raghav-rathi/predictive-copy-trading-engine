# Fibonacci Pivots — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793714400000] (2026-03-14 22:00 UTC →
2026-11-03 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP = 48 bars.

**Bar counts used:** BTC 5609, ETH 5609, HYPE 5607.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 203 | 32.0% | -1133.32 | -0.70 | -15.5% | -5.58 | 0.87 |
| ETH | 211 | 35.1% | -1491.29 | -0.99 | -20.0% | -7.07 | 0.84 |
| HYPE | 218 | 28.9% | -1321.23 | -0.83 | -20.5% | -6.06 | 0.86 |
| **Combined** | **632** | **32.0%** | **-3945.84** | **-1.20** | **-15.0%** | **-6.24** | **0.86** |

Fees: total $4958.09.
Exits: 92 signal, 540 stop.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser on all three coins

Daily Fibonacci pivots lose on every coin with PF 0.84-0.87. Prior-day levels do not hold at 1h in crypto — not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
