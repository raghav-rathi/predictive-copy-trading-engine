# Harmonic Crab — Backtest

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
| BTC | 2 | 0.0% | -146.23 | -1.21 | -1.7% | -73.12 | 0.00 |
| ETH | 0 | 0.0% | 0.00 | 0.00 | 0.0% | 0.00 | 0.00 |
| HYPE | 0 | 0.0% | 0.00 | 0.00 | 0.0% | 0.00 | 0.00 |
| **Combined** | **2** | **0.0%** | **-146.23** | **-1.21** | **-0.6%** | **-73.12** | — |

Fees: total $21.21.
Exits: {'stop': 2}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Near-no-signal: 2 trades on BTC, none on ETH/HYPE. The 1.618-extension Crab band is too strict for 1h crypto swings; no verdict beyond 'does not fire'.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
