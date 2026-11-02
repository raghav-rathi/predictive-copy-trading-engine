# Gann Fan — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793628000000] (2026-03-14 22:00 UTC → 2026-11-02
14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP = 44 bars.

**Bar counts used:** BTC 5585, ETH 5585, HYPE 5583.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 365 | 32.3% | -4,102.22 | -2.77 | -46.7% | -11.24 | 0.75 |
| ETH | 343 | 36.2% | -3,898.73 | -2.68 | -42.8% | -11.37 | 0.76 |
| HYPE | 359 | 36.2% | -1,656.48 | -0.92 | -27.9% | -4.61 | 0.89 |
| **Combined** | **1067** | **34.9%** | **-9,657.43** | **-2.99** | **-35.0%** | **-9.05** | **0.79** |

Fees: BTC $3,349.53, ETH $2,489.11, HYPE $1,505.98 (total $7,344.62).
Exits: 812 stop / 255 signal.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: Loser

-9,657.43 across 1067 trades on $30k starting capital, negative on all three coins. Gann Fan is not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
