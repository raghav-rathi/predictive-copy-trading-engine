# Adaptive RSI — Backtest

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
| BTC | 27 | 22.2% | -688.82 | -1.32 | -12.3% | -25.51 | 0.52 |
| ETH | 34 | 41.2% | -134.34 | -0.17 | -8.9% | -3.95 | 0.91 |
| HYPE | 30 | 26.7% | -905.10 | -1.52 | -11.8% | -30.17 | 0.42 |
| **Combined** | **91** | **30.8%** | **-1,728.26** | **-1.38** | **-8.5%** | **-18.99** | **0.62** |

Fees: BTC $246.42, ETH $238.76, HYPE $142.48 (total $627.66).
Exits: 91 stop.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: Loser on very few trades

-1,728.26 across only 91 trades on $30k starting capital, negative on all three coins. Adaptive smoothing did not rescue RSI's trend-pinning problem. Adaptive RSI is not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
