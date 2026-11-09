# Jurik MA Trend — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794232800000) (2026-03-14 22:00 UTC →
2026-11-09 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5752, ETH 5752, HYPE 5750.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 609 | 24.0% | -6601.21 | -7.13 | -68.9% | -10.84 | 0.49 |
| ETH | 590 | 25.3% | -3944.13 | -2.94 | -44.1% | -6.68 | 0.67 |
| HYPE | 616 | 30.0% | -3009.94 | -2.42 | -32.2% | -4.89 | 0.77 |
| **Combined** | **1815** | **26.4%** | **-13555.28** | **-5.50** | **-47.7%** | **-7.47** | **0.64** |

Fees: total $10795.92.
Exits: {'signal': 1489, 'stop': 326}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser (-$13,555.28, PF 0.64) on 1,815 trades — the worst batch-31 strategy, a clear NO-GO

A JMA(14) price cross on 1h crypto is a whipsaw machine: 1,815
trades, a 26.4% win rate, negative on all three coins, BTC down
-$6,601 with a -68.9% drawdown, combined Sharpe -5.50. The low-lag
smoothing does not help — the cross still flips on every minor
retracement, and fees ($10,796) compound the damage. The signal exit
fired 1,489 times, so the rule works as coded; the edge simply is
not there. Do not trade this standalone.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- The JMA used here is the public three-stage reconstruction, not
  Jurik's proprietary original — results are for this reconstruction.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
