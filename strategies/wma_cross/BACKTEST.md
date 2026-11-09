# WMA Crossover — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794232800000) (2026-03-14 22:00 UTC →
2026-11-09 13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5752, ETH 5752, HYPE 5750.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 373 | 30.8% | -2456.64 | -1.34 | -36.5% | -6.59 | 0.84 |
| ETH | 391 | 30.2% | -1776.41 | -0.84 | -32.1% | -4.54 | 0.89 |
| HYPE | 367 | 33.5% | 2356.41 | 1.25 | -13.9% | 6.42 | 1.14 |
| **Combined** | **1131** | **31.5%** | **-1876.64** | **-0.33** | **-21.3%** | **-1.66** | **0.96** |

Fees: total $9346.36.
Exits: BTC {'stop': 251, 'signal': 122}; ETH {'stop': 259, 'signal': 132}; HYPE {'stop': 236, 'signal': 131}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser combined on paper (−$1,876.64, PF 0.96, Sharpe −0.33).

The fastest of the three crossovers is also the worst: 1,131 trades in ~8 months — the 9/21 WMA pair whipsaws constantly on 1h crypto, and the 31.5% win rate cannot carry the 2xATR stops. BTC (−$2,456.64, −36.5% drawdown) and ETH (−$1,776.41, −32.1% drawdown) both lose badly; only HYPE wins (+$2,356.41), which is not enough and not consistent across coins. Fees alone are $9,346.36 — the strategy pays the market to churn. Not a tradeable signal as shipped.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
