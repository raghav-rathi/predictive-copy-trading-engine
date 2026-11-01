# Central Pivot Range — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793538000000] (2026-03-14 22:00 UTC → 2026-11-01
13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP = 48 bars.

**Bar counts used:** BTC 5560, ETH 5560, HYPE 5558.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 368 | 27.4% | -3,345.57 | -2.18 | -36.6% | -9.09 | 0.73 |
| ETH | 376 | 26.9% | -2,949.15 | -1.98 | -34.7% | -7.84 | 0.78 |
| HYPE | 359 | 32.0% | +321.69 | +0.32 | -21.9% | +0.90 | 1.02 |
| **Combined** | **1103** | **28.7%** | **-5,973.03** | **+0.70** | **-25.0%** | **-5.42** | **0.85** |

Fees: BTC $3,360.38, ETH $2,944.30, HYPE $1,939.76 (total $8,244.44).
Exits: 603 stop / 500 signal.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: Loser

-5,973.03 across 1103 trades on $30k starting capital, green only on HYPE.
Central Pivot Range is not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
