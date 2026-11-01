# DPO Cross — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793538000000] (2026-03-14 22:00 UTC → 2026-11-01
13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP = 40 bars.

**Bar counts used:** BTC 5560, ETH 5560, HYPE 5558.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 409 | 22.5% | -4,738.86 | -3.61 | -48.4% | -11.59 | 0.63 |
| ETH | 449 | 23.4% | -3,164.32 | -2.08 | -38.7% | -7.05 | 0.79 |
| HYPE | 409 | 25.4% | -1,073.83 | -0.56 | -26.1% | -2.63 | 0.92 |
| **Combined** | **1267** | **23.8%** | **-8,977.01** | **+0.38** | **-31.9%** | **-7.09** | **0.79** |

Fees: BTC $3,528.66, ETH $3,571.99, HYPE $2,057.49 (total $9,158.14).
Exits: 651 signal / 616 stop.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: Loser

-8,977.01 across 1267 trades on $30k starting capital, loses on all three coins.
DPO Cross is not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
