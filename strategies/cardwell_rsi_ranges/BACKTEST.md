# Cardwell RSI Ranges — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793714400000] (2026-03-14 22:00 UTC →
2026-11-03 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP = 40 bars.

**Bar counts used:** BTC 5609, ETH 5609, HYPE 5607.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 138 | 32.6% | -67.51 | 0.06 | -10.9% | -0.49 | 0.99 |
| ETH | 135 | 31.1% | -1610.70 | -1.30 | -25.9% | -11.93 | 0.76 |
| HYPE | 120 | 35.0% | -194.17 | -0.09 | -18.1% | -1.62 | 0.97 |
| **Combined** | **393** | **32.8%** | **-1872.38** | **-0.68** | **-13.3%** | **-4.76** | **0.90** |

Fees: total $3212.65.
Exits: 23 signal, 370 stop.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Near-flat loser

Closest to flat of the RSI family (-$1,872 combined, BTC essentially breakeven at -$67.51) but still negative on all three coins. Range rules filter noise without creating edge — not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
