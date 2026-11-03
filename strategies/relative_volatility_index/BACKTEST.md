# Relative Volatility Index — Backtest

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
| BTC | 1102 | 25.0% | -8436.80 | -9.27 | -84.5% | -7.66 | 0.51 |
| ETH | 1055 | 28.7% | -6045.52 | -4.38 | -61.1% | -5.73 | 0.71 |
| HYPE | 997 | 30.7% | -5790.57 | -4.23 | -60.5% | -5.81 | 0.74 |
| **Combined** | **3154** | **28.1%** | **-20272.90** | **-7.91** | **-68.0%** | **-6.43** | **0.66** |

Fees: total $15525.63.
Exits: 2313 signal, 841 stop.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Heavy loser, overtrades

Dorsey RVI crossed 50 over 3,100 times and bled on every coin (combined MaxDD -68%). Volatility-weighted RSI crosses are noise at 1h in crypto — not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
