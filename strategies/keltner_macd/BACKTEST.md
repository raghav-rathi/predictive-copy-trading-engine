# Keltner + MACD — Backtest

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
| BTC | 238 | 30.3% | -3434.54 | -2.45 | -37.2% | -14.43 | 0.68 |
| ETH | 241 | 28.6% | -3604.63 | -2.58 | -38.3% | -14.96 | 0.67 |
| HYPE | 227 | 32.6% | -1186.86 | -0.67 | -15.7% | -5.23 | 0.89 |
| **Combined** | **706** | **30.5%** | **-8226.03** | **-2.83** | **-28.8%** | **-11.65** | — |

Fees: total $4948.94.
Exits: {'stop': 571, 'signal': 135}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser on all three coins, 706 trades, PF 0.67-0.89. Keltner-band breakouts with MACD confirmation repeat the batch's band-breakout failure mode.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
