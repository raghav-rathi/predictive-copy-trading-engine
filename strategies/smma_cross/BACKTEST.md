# SMMA Crossover — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794232800000) (2026-03-14 22:00 UTC →
2026-11-09 13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5752, ETH 5752, HYPE 5750.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 125 | 41.6% | 996.30 | 0.88 | -8.8% | 7.97 | 1.17 |
| ETH | 155 | 29.7% | -1759.07 | -1.51 | -25.0% | -11.35 | 0.76 |
| HYPE | 142 | 36.6% | 906.34 | 1.02 | -9.4% | 6.38 | 1.13 |
| **Combined** | **422** | **35.5%** | **143.57** | **0.28** | **-8.4%** | **0.34** | **1.01** |

Fees: total $3764.86.
Exits: BTC {'stop': 123, 'signal': 2}; ETH {'stop': 132, 'signal': 23}; HYPE {'stop': 131, 'signal': 11}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Breakeven on paper (+$143.57, PF 1.01, Sharpe 0.28) — no edge.

A nominally positive combined number that is really noise: expectancy $0.34/trade, profit factor 1.01, Sharpe 0.28. BTC and HYPE win modestly while ETH loses −$1,759.07 with a −25.0% drawdown — the coin split is inconsistent, which is what a no-edge system looks like. Almost every exit (386 of 422) hits the ATR stop rather than the opposite cross, so the signal exit rarely gets to do its job; the cross is too slow to exit a failing trade. Treat as unproven / breakeven, not a tradeable signal.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
