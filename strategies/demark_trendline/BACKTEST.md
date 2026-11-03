# DeMark Trendline Breakout — Backtest

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
| BTC | 567 | 30.3% | -5875.20 | -4.34 | -58.8% | -10.36 | 0.67 |
| ETH | 552 | 29.5% | -5558.85 | -4.04 | -58.7% | -10.07 | 0.67 |
| HYPE | 482 | 34.6% | -1683.47 | -0.80 | -36.1% | -3.49 | 0.91 |
| **Combined** | **1601** | **31.4%** | **-13117.52** | **-4.04** | **-46.0%** | **-8.19** | **0.76** |

Fees: total $10316.77.
Exits: 765 signal, 836 stop.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Heavy loser, overtrades

TD trendline breakouts fire 1,601 times and lose badly on BTC/ETH (MaxDD ~-59%). Confirmed-pivot trendlines lag too much at 1h — not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
