# Volume Price Trend — Backtest

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
| BTC | 451 | 26.6% | -4,281.46 | -2.90 | -46.3% | -9.49 | 0.69 |
| ETH | 474 | 25.5% | -4,341.99 | -3.07 | -48.1% | -9.16 | 0.70 |
| HYPE | 407 | 30.7% | -95.05 | +0.08 | -15.9% | -0.23 | 0.99 |
| **Combined** | **1332** | **27.5%** | **-8,718.50** | **+0.41** | **-30.7%** | **-6.55** | **0.80** |

Fees: BTC $3,667.51, ETH $3,064.87, HYPE $2,021.79 (total $8,754.17).
Exits: 708 stop / 624 signal.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: Loser

-8,718.50 across 1332 trades on $30k starting capital, loses on all three coins.
Volume Price Trend is not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
