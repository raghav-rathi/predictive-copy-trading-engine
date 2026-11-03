# Weinstein Stage Analysis — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793714400000] (2026-03-14 22:00 UTC →
2026-11-03 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP = 220 bars.

**Bar counts used:** BTC 5609, ETH 5609, HYPE 5607.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 152 | 25.7% | -2344.62 | -2.25 | -25.3% | -15.43 | 0.65 |
| ETH | 170 | 27.1% | 376.45 | 0.41 | -12.5% | 2.21 | 1.06 |
| HYPE | 154 | 24.0% | 799.20 | 0.76 | -10.4% | 5.19 | 1.14 |
| **Combined** | **476** | **25.6%** | **-1168.98** | **-0.44** | **-11.6%** | **-2.46** | **0.94** |

Fees: total $3817.46.
Exits: 171 signal, 305 stop.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser overall, ETH/HYPE green

Green on ETH (+$376) and HYPE (+$799) but BTC (-$2,345) drags the combined to -$1,169. Stage transitions on 1h bars are too slow/late — not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
