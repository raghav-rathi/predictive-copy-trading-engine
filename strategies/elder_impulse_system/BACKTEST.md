# Elder Impulse System — Backtest

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
| BTC | 1222 | 25.0% | -8519.89 | -9.74 | -86.0% | -6.97 | 0.52 |
| ETH | 1233 | 24.0% | -7846.97 | -7.67 | -78.9% | -6.36 | 0.58 |
| HYPE | 1256 | 29.0% | -6776.25 | -6.45 | -68.3% | -5.40 | 0.61 |
| **Combined** | **3711** | **25.8%** | **-23143.12** | **-11.46** | **-77.5%** | **-6.24** | — |

Fees: total $15461.69.
Exits: {'signal': 3168, 'stop': 543}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser on all three coins, 3711 trades — the worst churn of batch 27. The impulse colour flips on nearly every MACD-histogram wiggle, so the system enters ~1,200 times per coin and exits on the next blue/red bar; $15,461.69 in fees alone exceeds half the combined loss. Elder designed the Impulse System as a filter, not a standalone entry trigger, and this window shows why.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
