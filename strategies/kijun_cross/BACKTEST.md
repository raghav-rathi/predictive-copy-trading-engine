# Kijun Cross — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793628000000] (2026-03-14 22:00 UTC → 2026-11-02
14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP = 40 bars.

**Bar counts used:** BTC 5585, ETH 5585, HYPE 5583.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 498 | 25.5% | -4,154.60 | -2.74 | -48.5% | -8.34 | 0.73 |
| ETH | 550 | 22.5% | -3,608.78 | -2.33 | -42.4% | -6.56 | 0.80 |
| HYPE | 504 | 25.2% | -2,611.37 | -1.52 | -27.5% | -5.18 | 0.83 |
| **Combined** | **1552** | **24.4%** | **-10,374.74** | **-2.98** | **-35.8%** | **-6.68** | **0.79** |

Fees: BTC $4,275.62, ETH $4,331.84, HYPE $2,280.37 (total $10,887.82).
Exits: 854 signal / 698 stop.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: Loser

-10,374.74 across 1552 trades on $30k starting capital, negative on all three coins. Kijun Cross is not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
