# Zero Lag EMA — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793887200000] (2026-03-14 22:00 UTC →
2026-11-05 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5656, ETH 5656, HYPE 5654.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 255 | 37.0% | -2033.41 | -1.29 | -27.6% | -7.97 | 0.82 |
| ETH | 293 | 32.0% | -1820.63 | -1.01 | -25.7% | -6.21 | 0.86 |
| HYPE | 283 | 37.0% | 1702.60 | 1.10 | -14.7% | 6.02 | 1.12 |
| **Combined** | **831** | **35.3%** | **-2151.44** | **-0.52** | **-19.0%** | **-2.59** | — |

Fees: total $6976.81.
Exits: {'stop': 642, 'signal': 189}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser, near breakeven, 831 trades, -$2,151.44, PF 0.94. HYPE alone green (+$1,702.60, PF 1.12) while BTC and ETH lose; the de-lagged cross is the closest to break-even in the batch but still nets negative.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
