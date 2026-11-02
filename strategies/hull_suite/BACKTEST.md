# Hull Suite — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793628000000] (2026-03-14 22:00 UTC → 2026-11-02
14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP = 32 bars.

**Bar counts used:** BTC 5585, ETH 5585, HYPE 5583.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 738 | 27.0% | -7,459.33 | -6.46 | -75.3% | -10.11 | 0.57 |
| ETH | 724 | 30.2% | -5,329.63 | -3.44 | -56.8% | -7.36 | 0.71 |
| HYPE | 698 | 31.9% | -4,260.69 | -2.74 | -47.2% | -6.10 | 0.79 |
| **Combined** | **2160** | **29.7%** | **-17,049.65** | **-5.39** | **-58.4%** | **-7.89** | **0.70** |

Fees: BTC $4,423.87, ETH $4,131.62, HYPE $2,610.11 (total $11,165.60).
Exits: 1281 signal / 879 stop.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: Loser — heavy overtrading

-17,049.65 across 2160 trades on $30k starting capital, negative on all three coins with drawdowns past 55% on the combined curve. A fast state/turn/flow line on 1h bars is a fee machine. Hull Suite is not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
