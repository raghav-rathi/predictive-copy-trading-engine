# Kumo Breakout — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793628000000] (2026-03-14 22:00 UTC → 2026-11-02
14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP = 90 bars.

**Bar counts used:** BTC 5585, ETH 5585, HYPE 5583.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 291 | 24.7% | -3,526.38 | -3.08 | -35.5% | -12.12 | 0.63 |
| ETH | 311 | 26.7% | -3,778.15 | -3.31 | -43.5% | -12.15 | 0.64 |
| HYPE | 294 | 21.4% | -1,813.75 | -1.23 | -19.7% | -6.17 | 0.81 |
| **Combined** | **896** | **24.3%** | **-9,118.28** | **-3.57** | **-30.6%** | **-10.18** | **0.69** |

Fees: BTC $2,791.88, ETH $2,463.34, HYPE $1,358.90 (total $6,614.12).
Exits: 455 stop / 441 signal.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: Loser

-9,118.28 across 896 trades on $30k starting capital, negative on all three coins. Kumo Breakout is not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
