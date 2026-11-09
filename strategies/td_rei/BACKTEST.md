# DeMark Range Expansion Index — Backtest

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
| BTC | 570 | 37.0% | -6448.63 | -5.61 | -66.6% | -11.31 | 0.59 |
| ETH | 556 | 40.5% | -5305.92 | -3.99 | -58.9% | -9.54 | 0.67 |
| HYPE | 580 | 42.8% | -2719.04 | -1.62 | -38.3% | -4.69 | 0.85 |
| **Combined** | **1706** | **40.1%** | **-14473.59** | **-5.03** | **-53.2%** | **-8.48** | **0.71** |

Fees: total $9169.73.
Exits: {'signal': 882, 'stop': 824}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser — heavy loser on all three coins (−$14,473.59 combined, PF 0.71, Sharpe −5.03, MaxDD −53.2%).

REI whipsaws across the ±60 extremes constantly on 1h crypto: 1,706
trades in ~8 months (~7 per day across the three coins), and nearly
half the exits hit the ATR stop. The ±60 snap-back idea — built for
daily bars, where DeMark's gate and 5-bar window filter out noise —
fires far too often on hourly bars; the oscillator re-crosses the
extremes before any move develops, and fees alone ($9,169.73) eat
more than half the gross loss. No coin is close to breakeven. Do not
trade as shipped; the signal needs a trend filter or a much wider
extreme band before it is worth revisiting.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
