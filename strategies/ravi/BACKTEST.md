# RAVI — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793628000000] (2026-03-14 22:00 UTC → 2026-11-02
14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP = 80 bars.

**Bar counts used:** BTC 5585, ETH 5585, HYPE 5583.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 125 | 36.0% | -719.17 | -0.57 | -15.8% | -5.75 | 0.87 |
| ETH | 144 | 36.1% | -239.69 | -0.09 | -14.4% | -1.66 | 0.97 |
| HYPE | 140 | 37.1% | -722.31 | -0.45 | -13.6% | -5.16 | 0.90 |
| **Combined** | **409** | **36.4%** | **-1,681.17** | **-0.58** | **-13.3%** | **-4.11** | **0.92** |

Fees: BTC $1,386.04, ETH $1,302.17, HYPE $712.82 (total $3,401.02).
Exits: 391 stop / 18 signal.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: Loser, second-smallest loss of the batch

-1,681.17 across 409 trades on $30k starting capital, negative on all three coins with shallow drawdowns. The 0.3% reference lines fire on noise at 1h scale. RAVI is not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
