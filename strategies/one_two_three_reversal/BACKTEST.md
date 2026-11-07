# 1-2-3 Reversal — Backtest

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
| BTC | 233 | 32.6% | -1765.36 | -1.06 | -22.4% | -7.58 | 0.83 |
| ETH | 225 | 33.8% | -1197.63 | -0.69 | -22.5% | -5.32 | 0.88 |
| HYPE | 207 | 35.7% | 284.71 | 0.28 | -19.2% | 1.38 | 1.03 |
| **Combined** | **665** | **34.0%** | **-2678.29** | **-0.76** | **-13.5%** | **-4.03** | **0.91** |

Fees: total $5033.52.
Exits: {'stop': 591, 'signal': 74}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser combined, 665 trades, -$2,678.29, PF 0.91 — the
1-2-3 fires constantly on 1h fractal pivots (665 trades in 7.5 months)
and the 2xATR stop / 2.5xATR trail does almost all of the exiting
(591 of 665 exits are stops); the point-3 invalidation exit fires only
74 times. Win rate 34.0% with expectancy -$4.03/trade: breakout
entries above point 2 on noisy 1h pivots get faded more often than
they run. HYPE alone is slightly green (+$284.71) but that is thin
noise on 207 trades, not an edge.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
