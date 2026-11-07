# Floor-Trader Pivots — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1794060000000] (2026-03-14 22:00 UTC →
2026-11-07 13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5704, ETH 5704, HYPE 5702.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 102 | 33.3% | -1091.03 | -1.09 | -16.1% | -10.70 | 0.75 |
| ETH | 99 | 36.4% | 557.55 | 0.59 | -7.8% | 5.63 | 1.12 |
| HYPE | 72 | 41.7% | 1667.04 | 1.64 | -9.6% | 23.15 | 1.48 |
| **Combined** | **273** | **36.6%** | **1133.56** | **0.56** | **-6.4%** | **4.15** | **1.09** |

Fees: total $2379.62.
Exits: {'stop': 201, 'signal': 72}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Winner combined, 273 trades, +$1133.56, PF 1.09 — but
lopsided: HYPE (+$1667.04, Sharpe 1.64) carries the batch while BTC
(-$1091.03, Sharpe -1.09, MaxDD -16.1%) is firmly red and ETH
(+$557.55) is middling. The exit mix is stop-heavy (201 of 273 exits
hit the ATR stop/trail, only 72 reached the R2/S2 target or the
back-below/above-PP signal exit), so positions rarely run to target.
A genuine small edge on HYPE/ETH, not on BTC — treat as
coin-dependent, not a universal pivot edge.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
