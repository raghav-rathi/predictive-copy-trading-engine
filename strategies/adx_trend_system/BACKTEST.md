# ADX Trend System — Backtest

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
| BTC | 86 | 28.0% | -396.13 | -0.35 | -13.7% | -4.61 | 0.88 |
| ETH | 82 | 33.0% | -895.15 | -1.24 | -15.4% | -10.92 | 0.69 |
| HYPE | 93 | 24.0% | -1373.92 | -2.20 | -13.7% | -14.77 | 0.57 |
| **Combined** | **261** | **28.0%** | **-2665.21** | **-1.83** | **-9.0%** | **-10.21** | — |

Fees: total $2072.09.
Exits: {'signal': 133, 'stop': 128}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser on all three coins, 261 trades, -$2,665.21, PF 0.72. The ADX > 25 filter keeps count low but DI crosses arrive late; 28.0% win rate, worst on HYPE -$1,373.92.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
