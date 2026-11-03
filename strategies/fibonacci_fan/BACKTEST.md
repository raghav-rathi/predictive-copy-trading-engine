# Fibonacci Fan — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793714400000] (2026-03-14 22:00 UTC →
2026-11-03 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP = 60 bars.

**Bar counts used:** BTC 5609, ETH 5609, HYPE 5607.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 158 | 31.0% | -1845.53 | -1.44 | -25.3% | -11.68 | 0.75 |
| ETH | 147 | 34.0% | -1026.15 | -0.75 | -20.9% | -6.98 | 0.86 |
| HYPE | 135 | 37.0% | 768.68 | 0.84 | -14.2% | 5.69 | 1.12 |
| **Combined** | **440** | **33.9%** | **-2103.00** | **-0.69** | **-13.1%** | **-4.78** | **0.90** |

Fees: total $3432.58.
Exits: 29 signal, 411 stop.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser overall, HYPE green

Negative on BTC/ETH, green on HYPE (+$769, PF 1.12). One-coin green does not make a system — not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
