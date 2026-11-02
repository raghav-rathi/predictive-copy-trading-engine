# ZigZag Swing Breakout — Backtest

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
| BTC | 47 | 31.9% | -77.83 | -0.06 | -8.1% | -1.66 | 0.97 |
| ETH | 44 | 31.8% | -532.55 | -0.67 | -12.6% | -12.10 | 0.79 |
| HYPE | 84 | 36.9% | -437.42 | -0.33 | -12.7% | -5.21 | 0.89 |
| **Combined** | **175** | **34.3%** | **-1,047.80** | **-0.62** | **-8.6%** | **-5.99** | **0.88** |

Fees: BTC $446.75, ETH $318.77, HYPE $388.80 (total $1,154.33).
Exits: 175 stop.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: Near-flat loser, not an edge

-1,047.80 across 175 trades on $30k starting capital, the smallest loss of the batch — but still negative on all three coins and too few trades to call even a weak signal. ZigZag swing breakout is not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
