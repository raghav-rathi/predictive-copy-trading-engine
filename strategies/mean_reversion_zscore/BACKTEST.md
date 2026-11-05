# Mean Reversion Z-Score — Backtest

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
| BTC | 106 | 49.0% | -1269.61 | -1.71 | -13.7% | -11.98 | 0.72 |
| ETH | 105 | 52.0% | -1076.59 | -1.43 | -12.3% | -10.25 | 0.75 |
| HYPE | 112 | 57.0% | -543.46 | -0.69 | -14.2% | -4.85 | 0.87 |
| **Combined** | **323** | **52.9%** | **-2889.65** | **-1.99** | **-12.1%** | **-8.95** | — |

Fees: total $2604.67.
Exits: {'signal': 183, 'stop': 140}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser on all three coins, 323 trades, -$2,889.65, PF 0.78. Wins the coin flip at 52.9% win rate but loses the money; z=0 exits cut winners short while stops let losers run.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
