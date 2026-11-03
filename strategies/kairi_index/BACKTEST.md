# Kairi Relative Index — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793714400000] (2026-03-14 22:00 UTC →
2026-11-03 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP = 30 bars.

**Bar counts used:** BTC 5609, ETH 5609, HYPE 5607.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 5 | 0.0% | -410.82 | -2.78 | -4.7% | -82.16 | 0.00 |
| ETH | 20 | 35.0% | -327.22 | -1.03 | -6.0% | -16.36 | 0.68 |
| HYPE | 53 | 43.4% | -1174.65 | -2.25 | -13.6% | -22.16 | 0.51 |
| **Combined** | **78** | **38.5%** | **-1912.69** | **-2.85** | **-7.0%** | **-24.52** | **0.50** |

Fees: total $258.86.
Exits: 33 signal, 45 stop.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser on all three coins

Mean-reversion entries at +/-5% KRI lose everywhere, worst on HYPE (-13.6% MaxDD). The 25-bar mean is too slow for 1h crypto ranges — not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
