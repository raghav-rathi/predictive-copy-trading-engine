# Time Segmented Volume — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794232800000) (2026-03-14 22:00 UTC →
2026-11-09 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5752, ETH 5752, HYPE 5750.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 505 | 26.9% | -5011.44 | -3.60 | -55.0% | -9.92 | 0.63 |
| ETH | 505 | 29.3% | -528.34 | -0.13 | -28.3% | -1.05 | 0.97 |
| HYPE | 459 | 37.0% | 143.62 | 0.21 | -14.3% | 0.31 | 1.01 |
| **Combined** | **1469** | **30.9%** | **-5396.15** | **-1.33** | **-24.3%** | **-3.67** | **0.88** |

Fees: total $10439.31.
Exits: {'stop': 724, 'signal': 745}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser combined (−$5,396.15, PF 0.88) on 1,469 trades.

The zero-line cross fires about every 11 bars and the win rate sits
near 30% on every coin — TSV flips sign on noise as readily as on
real accumulation, and half the exits (724 of 1,469) hit the ATR
stop rather than the signal exit, so positions are usually stopped
out before any follow-through. HYPE's +$143.62 (PF 1.01, 459 trades)
is a nominal breakeven, not a winner: $0.31 expectancy per trade
against ~$5 of fees per trade. No edge here on 1h crypto.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
