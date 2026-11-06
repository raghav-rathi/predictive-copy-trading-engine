# Wolfe Wave — Backtest

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
| BTC | 57 | 43.9% | 295.87 | 0.45 | -8.1% | 5.19 | 1.12 |
| ETH | 55 | 29.1% | -1590.75 | -2.52 | -21.5% | -28.92 | 0.48 |
| HYPE | 51 | 37.3% | -780.33 | -1.30 | -12.2% | -15.30 | 0.68 |
| **Combined** | **163** | **36.8%** | **-2075.21** | **-1.56** | **-12.4%** | **-12.73** | **0.74** |

Fees: total $1284.23.
Exits: {'stop': 121, 'signal': 42}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser combined, 163 trades, -$2,075.21, PF 0.74. BTC's +$295.87 (PF 1.12) is the only green coin and is small against ETH's -$1,590.75 (PF 0.48, Sharpe -2.52). 74% of exits are stops — the trendline-reclaim entry does not survive 1h crypto chop.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
