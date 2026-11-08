# Narrow-Range Breakout (NR7) — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1792328400000] (2026-03-14 22:00 UTC →
2026-10-18 13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5223, ETH 5223, HYPE 5221.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 500 | 20.4% | -7917.45 | -8.17 | -79.2% | -15.83 | 0.40 |
| ETH | 454 | 23.1% | -6058.16 | -4.91 | -62.9% | -13.34 | 0.60 |
| HYPE | 413 | 27.1% | -4491.58 | -3.45 | -47.0% | -10.88 | 0.66 |
| **Combined** | **1367** | **23.3%** | **-18467.19** | **-7.14** | **-61.9%** | **-13.51** | **0.56** |

Fees: total $7129.04.
Exits: {'signal': 756, 'stop': 611}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser, 1367 trades, -$18467.19, PF 0.56 — heavily red
on all three coins (BTC -$7917.45, Sharpe -8.17, MaxDD -79.2%).
NR7 setups recur every few bars and the 24-bar window keeps levels
armed most of the time, so the strategy trades nearly every close
past a recent narrow bar's high/low — pure whipsaw in chop, with a
20-27% win rate against 2xATR stops. No edge on this window in
either direction; do not trade as specified.

## Limitations

- Single ~7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
