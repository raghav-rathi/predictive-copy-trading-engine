# CG Oscillator — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793538000000] (2026-03-14 22:00 UTC → 2026-11-01
13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP = 20 bars.

**Bar counts used:** BTC 5560, ETH 5560, HYPE 5558.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 1125 | 29.9% | -8,441.59 | -8.66 | -84.9% | -7.50 | 0.52 |
| ETH | 1143 | 32.8% | -6,535.10 | -4.64 | -68.0% | -5.72 | 0.68 |
| HYPE | 1094 | 36.1% | -5,652.34 | -4.13 | -61.7% | -5.17 | 0.75 |
| **Combined** | **3362** | **32.9%** | **-20,629.03** | **-1.50** | **-70.6%** | **-6.14** | **0.66** |

Fees: BTC $5,238.23, ETH $5,376.73, HYPE $3,495.72 (total $14,110.69).
Exits: 2459 signal / 903 stop.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: Loser

-20,629.03 across 3362 trades on $30k starting capital, loses on all three coins.
CG Oscillator is not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
