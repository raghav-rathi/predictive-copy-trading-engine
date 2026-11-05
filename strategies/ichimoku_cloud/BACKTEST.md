# Ichimoku Cloud — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) extended with the public
candleSnapshot tail to the last completed hour bar. Window t in
[1773525600000, 1793887200000] (2026-03-14 22:00 UTC →
2026-11-05 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5656, ETH 5656, HYPE 5654.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 63 | 30.0% | -914.24 | -1.06 | -16.2% | -14.51 | 0.67 |
| ETH | 60 | 23.0% | -706.51 | -0.77 | -9.1% | -11.78 | 0.77 |
| HYPE | 64 | 36.0% | -33.19 | 0.03 | -9.9% | -0.52 | 0.99 |
| **Combined** | **187** | **29.9%** | **-1653.95** | **-0.91** | **-7.7%** | **-8.84** | — |

Fees: total $1515.25.
Exits: {'stop': 143, 'signal': 44}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser on all three coins, 187 trades, -$1,653.95, PF 0.81. The strictest filter set in the batch (fewest trades by far) still loses, with the worst combined win rate (29.9%) — the Tenkan/Kijun cross + cloud + Chikou stack filters out most trades without filtering out the losers.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
