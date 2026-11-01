# NR7 Breakout — Backtest

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
| BTC | 759 | 25.0% | -8,015.55 | -7.49 | -80.6% | -10.56 | 0.52 |
| ETH | 713 | 29.2% | -5,422.89 | -3.52 | -57.1% | -7.61 | 0.72 |
| HYPE | 705 | 30.9% | -4,813.88 | -3.08 | -49.9% | -6.83 | 0.75 |
| **Combined** | **2177** | **28.3%** | **-18,252.32** | **-0.99** | **-61.4%** | **-8.38** | **0.67** |

Fees: BTC $4,104.97, ETH $4,206.17, HYPE $2,381.85 (total $10,692.99).
Exits: 1264 signal / 913 stop.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: Loser

-18,252.32 across 2177 trades on $30k starting capital, loses on all three coins.
NR7 Breakout is not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
