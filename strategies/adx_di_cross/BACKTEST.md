# ADX / DI Crossover — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1792328400000) (2026-03-14 22:00 UTC →
2026-10-18 13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5223, ETH 5223, HYPE 5221.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 3 | 0.0% | -117.32 | -0.77 | -2.2% | -39.11 | 0.00 |
| ETH | 1 | 0.0% | -104.81 | -2.11 | -1.0% | -104.81 | 0.00 |
| HYPE | 4 | 75.0% | 698.18 | 2.58 | -2.1% | 174.55 | 7.00 |
| **Combined** | **8** | **37.5%** | **476.05** | **1.51** | **-1.1%** | **59.51** | **2.41** |

Fees: total $58.73.
Exits: {'stop': 8}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Winner combined on paper (+$476.05, PF 2.41) — but on only
8 trades, so this is not a meaningful edge. The ADX > 25 + rising +
spread ≥ 5 filter is extremely restrictive on 1h crypto: BTC fired 3
times (all losses), ETH once (a loss), and the entire combined profit
comes from 3 winning HYPE trades. Every exit hit the ATR stop/trail —
no trade ever reached a DI-cross or ADX < 20 signal exit. Treat as
unproven / sample-size noise, not a tradeable signal.

## Limitations

- Single ~7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
