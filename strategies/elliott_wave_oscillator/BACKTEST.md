# Elliott Wave Oscillator — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793800800000] (2026-03-14 22:00 UTC →
2026-11-04 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5633, ETH 5633, HYPE 5631.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 117 | 26.5% | -1293.02 | -1.11 | -17.5% | -11.05 | 0.74 |
| ETH | 132 | 28.8% | -912.46 | -0.72 | -22.1% | -6.91 | 0.83 |
| HYPE | 127 | 33.1% | 132.60 | 0.20 | -16.0% | 1.04 | 1.02 |
| **Combined** | **376** | **29.5%** | **-2072.88** | **-0.86** | **-13.0%** | **-5.51** | — |

Fees: total $3134.04.
Exits: {'stop': 285, 'signal': 91}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser on BTC/ETH, barely green on HYPE. The SMA(50)-filtered zero-cross system trades into chop and wins under 30% of the time on BTC/ETH.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
