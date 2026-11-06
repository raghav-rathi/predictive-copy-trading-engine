# Shooting Star Pattern — Backtest

**Data:** Hyperliquid 1h candles: local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1793973600000] (2026-03-14 22:00 UTC →
2026-11-06 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5681, ETH 5681, HYPE 5679.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 28 | 35.7% | -175.88 | -0.31 | -6.7% | -6.28 | 0.89 |
| ETH | 34 | 41.2% | -285.04 | -0.49 | -9.5% | -8.38 | 0.84 |
| HYPE | 58 | 51.7% | 473.38 | 0.75 | -9.0% | 8.16 | 1.23 |
| **Combined** | **120** | **45.0%** | **12.45** | **0.02** | **-3.9%** | **0.10** | — |

Fees: total $730.04.
Exits: {'stop': 80, 'signal': 40}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). The summed curve's
final net is -$4.28 rather than +$12.45 because an ETH short was still
open at the window end, carrying -$16.73 of unrealised MTM.

## Verdict: Breakeven scratch combined, 120 trades, +$12.45, PF 1.00. HYPE's +$473.38 (PF 1.23) is the only green coin and is offset by BTC and ETH losses; the combined result is noise around zero, not a win. Two-thirds of exits are stops.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
