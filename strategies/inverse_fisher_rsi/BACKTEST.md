# Inverse Fisher RSI — Backtest

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
| BTC | 335 | 29.9% | -4,444.83 | -3.30 | -44.4% | -13.27 | 0.63 |
| ETH | 340 | 34.7% | -2,042.64 | -1.26 | -33.8% | -6.01 | 0.85 |
| HYPE | 330 | 38.8% | +2,897.92 | +1.58 | -18.3% | +8.78 | 1.18 |
| **Combined** | **1005** | **34.4%** | **-3,589.55** | **+0.92** | **-18.0%** | **-3.57** | **0.92** |

Fees: BTC $2,706.14, ETH $2,728.03, HYPE $2,040.41 (total $7,474.58).
Exits: 648 stop / 357 signal.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: Loser

-3,589.55 across 1005 trades on $30k starting capital, green only on HYPE.
Inverse Fisher RSI is not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
