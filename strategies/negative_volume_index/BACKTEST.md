# Negative Volume Index — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793538000000] (2026-03-14 22:00 UTC → 2026-11-01
13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP = 300 bars.

**Bar counts used:** BTC 5560, ETH 5560, HYPE 5558.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 170 | 28.8% | -2,969.25 | -3.57 | -30.3% | -17.47 | 0.52 |
| ETH | 177 | 31.1% | -2,438.86 | -2.76 | -29.4% | -13.78 | 0.61 |
| HYPE | 205 | 28.3% | -2,293.62 | -2.47 | -25.0% | -11.19 | 0.66 |
| **Combined** | **552** | **29.3%** | **-7,701.74** | **+0.52** | **-26.2%** | **-13.95** | **0.60** |

Fees: BTC $1,590.72, ETH $1,257.69, HYPE $963.89 (total $3,812.30).
Exits: 296 signal / 256 stop.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: Loser

-7,701.74 across 552 trades on $30k starting capital, loses on all three coins.
Negative Volume Index is not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
