# Fast Stochastic Crossover — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1792328400000] (2026-03-14 22:00 UTC →
2026-10-18 13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5223, ETH 5223, HYPE 5221.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 85 | 24.7% | -1158.54 | -2.25 | -12.1% | -13.63 | 0.52 |
| ETH | 76 | 39.5% | -32.06 | -0.02 | -6.1% | -0.42 | 0.98 |
| HYPE | 112 | 32.1% | -864.14 | -1.98 | -12.5% | -7.72 | 0.65 |
| **Combined** | **273** | **31.9%** | **-2054.74** | **-1.99** | **-7.9%** | **-7.53** | **0.69** |

Fees: total $2313.27.
Exits: {'signal': 238, 'stop': 35}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser combined, 273 trades, -$2054.74, PF 0.69, Sharpe
-1.99 — all three coins red or flat (BTC -$1158.54, HYPE -$864.14,
ETH -$32.06). The exit mix is signal-dominated (238 of 273 exits
via the %K cross / extreme-zone exit, only 35 on the ATR stop):
oversold/overbought crosses on 1h crypto reverse too fast, so
positions are cut before any trend develops, and the 31.9% win
rate cannot cover fees. No fast-stochastic edge on this window.

## Limitations

- Single ~7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
