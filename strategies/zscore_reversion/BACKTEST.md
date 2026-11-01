# Z-Score Reversion — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793538000000] (2026-03-14 22:00 UTC → 2026-11-01
13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP = 30 bars.

**Bar counts used:** BTC 5560, ETH 5560, HYPE 5558.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 282 | 42.6% | -4,749.24 | -5.03 | -48.6% | -16.84 | 0.53 |
| ETH | 258 | 40.7% | -4,819.04 | -4.91 | -48.2% | -18.68 | 0.53 |
| HYPE | 289 | 47.1% | -1,947.03 | -1.64 | -26.4% | -6.74 | 0.83 |
| **Combined** | **829** | **43.5%** | **-11,515.30** | **+0.05** | **-39.3%** | **-13.89** | **0.64** |

Fees: BTC $2,220.68, ETH $1,543.30, HYPE $1,391.01 (total $5,154.99).
Exits: 463 stop / 366 signal.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: Loser

-11,515.30 across 829 trades on $30k starting capital, loses on all three coins.
Z-Score Reversion is not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
