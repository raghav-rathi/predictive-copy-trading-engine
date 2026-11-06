# EMA Pullback — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793973600000] (2026-03-14 22:00 UTC →
2026-11-06 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5681, ETH 5681, HYPE 5679.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 629 | 21.3% | -7469.95 | -6.21 | -76.0% | -11.88 | 0.53 |
| ETH | 701 | 21.1% | -6917.70 | -5.13 | -71.6% | -9.87 | 0.63 |
| HYPE | 621 | 23.8% | -4030.76 | -2.38 | -41.5% | -6.49 | 0.77 |
| **Combined** | **1951** | **22.0%** | **-18418.41** | **-5.85** | **-62.0%** | **-9.44** | — |

Fees: total $10051.96.
Exits: {'signal': 1083, 'stop': 868}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser combined, 1951 trades, -$18,418.41, PF 0.65. Worst batch-scale loss: 22.0% win rate on all three coins, BTC -76.0% drawdown; pullback entries fire constantly into chop and the EMA(20) exit comes too late to save them.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
