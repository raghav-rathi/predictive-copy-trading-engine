# 5-0 Pattern — Backtest

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
| BTC | 14 | 50.0% | -53.62 | -0.17 | -4.0% | -3.83 | 0.86 |
| ETH | 9 | 66.7% | 93.09 | 0.79 | -0.7% | 10.34 | 2.71 |
| HYPE | 15 | 80.0% | 22.10 | 0.14 | -2.3% | 1.47 | 1.09 |
| **Combined** | **38** | **65.8%** | **61.57** | **0.18** | **-0.8%** | **1.62** | **1.09** |

Fees: total $334.96.
Exits: {'signal': 32, 'stop': 6}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Winner combined, 38 trades, +$61.57, PF 1.09 — a thin, small
win: 65.8% win rate but tiny expectancy (+$1.62/trade); ETH (+$93.09)
and HYPE (+$22.10) green, BTC (-$53.62) slightly red. The exit
correction matters: the as-specified rule (38.2% of the C-to-D leg
measured from C) sat below the entry and printed -$214.27 with 37/38
immediate signal exits; the corrected BC-leg retracement target lets
positions run to a real target. Still thin-sample noise more than an
edge — 38 trades over 7.5 months.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
