# Volume-weighted MACD — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1793973600000] (2026-03-14 22:00 UTC →
2026-11-06 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5681, ETH 5681, HYPE 5679.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 68 | 19.1% | -1659.54 | -2.35 | -17.8% | -24.41 | 0.51 |
| ETH | 67 | 29.9% | 148.19 | 0.22 | -11.8% | 2.21 | 1.05 |
| HYPE | 66 | 39.4% | 342.36 | 0.44 | -11.2% | 5.19 | 1.12 |
| **Combined** | **201** | **29.4%** | **-1168.99** | **-0.61** | **-10.2%** | **-5.82** | — |

Fees: total $1765.99.
Exits: {'stop': 151, 'signal': 50}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser combined, 201 trades, -$1,168.99, PF 0.88. BTC drives the loss (19.1% win rate, PF 0.51); ETH and HYPE are small greens that do not cover it. The volume-weighted MACD cross fires late into moves — 75% of exits are stops.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
