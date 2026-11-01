# RSI Bollinger Bands — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793538000000] (2026-03-14 22:00 UTC → 2026-11-01
13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP = 50 bars.

**Bar counts used:** BTC 5560, ETH 5560, HYPE 5558.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 268 | 49.3% | -3,741.84 | -4.06 | -39.9% | -13.96 | 0.58 |
| ETH | 249 | 51.0% | -3,221.03 | -3.62 | -34.9% | -12.94 | 0.61 |
| HYPE | 272 | 49.6% | -3,781.14 | -4.08 | -39.5% | -13.90 | 0.60 |
| **Combined** | **789** | **49.9%** | **-10,744.01** | **+0.15** | **-37.5%** | **-13.62** | **0.59** |

Fees: BTC $2,439.40, ETH $1,763.96, HYPE $1,108.94 (total $5,312.31).
Exits: 462 signal / 327 stop.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: Loser

-10,744.01 across 789 trades on $30k starting capital, loses on all three coins.
RSI Bollinger Bands is not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
