# Keltner Breakout — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793628000000] (2026-03-14 22:00 UTC → 2026-11-02
14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP = 30 bars.

**Bar counts used:** BTC 5585, ETH 5585, HYPE 5583.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 146 | 29.5% | -1,674.21 | -1.34 | -21.4% | -11.47 | 0.77 |
| ETH | 135 | 34.1% | -844.27 | -0.59 | -20.3% | -6.25 | 0.86 |
| HYPE | 136 | 33.8% | -373.37 | -0.23 | -14.4% | -2.75 | 0.94 |
| **Combined** | **417** | **32.4%** | **-2,891.85** | **-1.04** | **-12.5%** | **-6.93** | **0.85** |

Fees: BTC $1,492.36, ETH $1,039.29, HYPE $694.17 (total $3,225.81).
Exits: 361 stop / 56 signal.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: Loser

-2,891.85 across 417 trades on $30k starting capital, negative on all three coins. Buying 2xATR excursions mostly buys mean reversion. Keltner Breakout is not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
