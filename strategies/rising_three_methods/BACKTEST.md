# Rising Three Methods — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1792328400000] (2026-03-14 22:00 UTC →
2026-10-18 13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5223, ETH 5223, HYPE 5221.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 0 | 0.0% | 0.00 | 0.00 | 0.0% | 0.00 | 0.00 |
| ETH | 1 | 100.0% | 39.99 | 0.40 | -0.8% | 39.99 | inf |
| HYPE | 0 | 0.0% | 0.00 | 0.00 | 0.0% | 0.00 | 0.00 |
| **Combined** | **1** | **100.0%** | **39.99** | **0.39** | **-0.3%** | **39.99** | **inf** |

Fees: total $13.78.
Exits: {'stop': 1}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Untestable as specified — 1 trade in the whole window.
The pattern fires exactly once post-warmup across ~15,600 bars
(1 long entry on ETH, 0 on BTC and HYPE): a 5-bar structure
requiring a ≥1.0×ATR bar-1 body plus three consecutive
inside-range counter-trend candles plus a breakout close
essentially never completes on 1h crypto. The single trade
(+$39.99, exited on the ATR stop) carries no information about
the pattern's edge. This is a pattern-frequency failure, not a
code bug — the logic fires correctly on synthetic data (see the
unit tests). Do not read the +$39.99 / PF inf as a win.

## Limitations

- Single ~7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
