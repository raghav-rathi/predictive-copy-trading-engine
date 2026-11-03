# Cutler RSI — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793714400000] (2026-03-14 22:00 UTC →
2026-11-03 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP = 20 bars.

**Bar counts used:** BTC 5609, ETH 5609, HYPE 5607.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 263 | 39.9% | -2598.23 | -1.94 | -31.5% | -9.88 | 0.79 |
| ETH | 269 | 42.8% | -1754.58 | -1.18 | -27.7% | -6.52 | 0.85 |
| HYPE | 248 | 38.7% | -2360.56 | -1.85 | -26.0% | -9.52 | 0.78 |
| **Combined** | **780** | **40.5%** | **-6713.38** | **-2.34** | **-24.8%** | **-8.61** | **0.81** |

Fees: total $5737.44.
Exits: 249 signal, 531 stop.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser on all three coins

Simple-average RSI performs like Wilder RSI here: negative everywhere, ~40% win rate, PF 0.78-0.85. The smoothing choice is not the edge — not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
