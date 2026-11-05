# Williams %R Oscillator — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793887200000] (2026-03-14 22:00 UTC →
2026-11-05 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5656, ETH 5656, HYPE 5654.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 139 | 41.0% | -3385.95 | -4.30 | -35.0% | -24.36 | 0.44 |
| ETH | 129 | 42.0% | -1239.75 | -1.36 | -13.8% | -9.61 | 0.78 |
| HYPE | 134 | 49.0% | -1867.66 | -2.47 | -26.1% | -13.94 | 0.67 |
| **Combined** | **402** | **44.0%** | **-6493.35** | **-4.22** | **-23.2%** | **-16.15** | — |

Fees: total $2984.34.
Exits: {'stop': 222, 'signal': 180}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser on all three coins, 402 trades, -$6,493.35, PF 0.62. The %R exit-the-extreme entries fire into moves that keep running; expectancy -$16.15 per trade is the worst per-trade bleed in the batch after the churners.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
