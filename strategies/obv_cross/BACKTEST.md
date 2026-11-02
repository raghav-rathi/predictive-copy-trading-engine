# OBV Cross — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793628000000] (2026-03-14 22:00 UTC → 2026-11-02
14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP = 34 bars.

**Bar counts used:** BTC 5585, ETH 5585, HYPE 5583.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 773 | 19.4% | -8,185.30 | -9.05 | -82.2% | -10.59 | 0.43 |
| ETH | 659 | 23.4% | -5,133.69 | -3.77 | -52.2% | -7.79 | 0.68 |
| HYPE | 670 | 25.1% | -2,879.06 | -1.69 | -32.7% | -4.30 | 0.84 |
| **Combined** | **2102** | **22.5%** | **-16,198.05** | **-5.79** | **-55.1%** | **-7.71** | **0.67** |

Fees: BTC $3,968.12, ETH $4,044.35, HYPE $3,028.32 (total $11,040.80).
Exits: 1362 signal / 740 stop.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: Loser — heavy overtrading

-16,198.05 across 2102 trades on $30k starting capital, negative on all three coins with drawdowns past 55% on the combined curve. A fast state/turn/flow line on 1h bars is a fee machine. OBV Cross is not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
