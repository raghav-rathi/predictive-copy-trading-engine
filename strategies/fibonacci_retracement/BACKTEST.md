# Fibonacci Retracement — Backtest

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
| BTC | 177 | 46.9% | -1143.92 | -1.09 | -18.3% | -6.46 | 0.84 |
| ETH | 148 | 39.9% | -2666.73 | -3.41 | -29.3% | -18.02 | 0.61 |
| HYPE | 205 | 43.4% | -3012.49 | -3.42 | -33.6% | -14.70 | 0.64 |
| **Combined** | **530** | **43.6%** | **-6823.14** | **-3.88** | **-25.0%** | **-12.87** | **0.70** |

Fees: total $3569.40.
Exits: {'stop': 294, 'signal': 236}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Clear loser combined, 530 trades, -$6,823.14, PF 0.70 —
the worst batch-29 strategy by Sharpe (-3.88). All three coins lose
(BTC -$1,143.92, ETH -$2,666.73, HYPE -$3,012.49). The golden-zone
bounce does not hold on 1h crypto: 294 of 530 trades end on the ATR
stop, and even the 236 signal exits (old-high targets and A
invalidations) cannot carry the book — expectancy -$12.87/trade.
The first-touch-only rule keeps trade count lower than the other two
batch-29 strategies, but the edge is still negative on every coin.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
