# Three Drives Pattern — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793973600000] (2026-03-14 22:00 UTC →
2026-11-06 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5681, ETH 5681, HYPE 5679.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 0 | — | 0.00 | 0.00 | 0.0% | 0.00 | — |
| ETH | 0 | — | 0.00 | 0.00 | 0.0% | 0.00 | — |
| HYPE | 0 | — | 0.00 | 0.00 | 0.0% | 0.00 | — |
| **Combined** | **0** | **—** | **0.00** | **0.00** | **0.0%** | **0.00** | **—** |

Fees: total $0.00.
Exits: {}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: No trades — 0 trades on all three coins, $0.00. The pattern never completed on 1h crypto in this window: only 5 pivot windows across all three coins passed all four ratio checks, and every one of them failed the drive-length symmetry check (e.g. BTC lengths 3/8/4 and 4/3/10 bars). This is the honest result of the strict a-priori filters; no parameters were loosened to force trades.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
