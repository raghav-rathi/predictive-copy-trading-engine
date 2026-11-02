# Gann HiLo Activator — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793628000000] (2026-03-14 22:00 UTC → 2026-11-02
14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP = 20 bars.

**Bar counts used:** BTC 5585, ETH 5585, HYPE 5583.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 823 | 25.9% | -8,068.98 | -7.62 | -81.1% | -9.80 | 0.53 |
| ETH | 814 | 28.9% | -6,222.97 | -4.32 | -64.8% | -7.64 | 0.68 |
| HYPE | 754 | 32.1% | -3,842.86 | -2.33 | -46.3% | -5.10 | 0.81 |
| **Combined** | **2391** | **28.9%** | **-18,134.81** | **-5.85** | **-62.3%** | **-7.58** | **0.68** |

Fees: BTC $4,568.53, ETH $4,259.66, HYPE $2,731.20 (total $11,559.39).
Exits: 1498 signal / 893 stop.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: Loser — heavy overtrading

-18,134.81 across 2391 trades on $30k starting capital, negative on all three coins with drawdowns past 55% on the combined curve. A fast state/turn/flow line on 1h bars is a fee machine. Gann HiLo Activator is not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
