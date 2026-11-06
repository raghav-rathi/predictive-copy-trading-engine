# Belt Hold Pattern — Backtest

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
| BTC | 188 | 35.6% | -2315.55 | -1.88 | -29.0% | -12.32 | 0.75 |
| ETH | 161 | 37.9% | 1297.25 | 1.37 | -16.5% | 8.06 | 1.18 |
| HYPE | 207 | 34.3% | -166.53 | 0.02 | -21.3% | -0.80 | 0.98 |
| **Combined** | **556** | **35.8%** | **-1184.82** | **-0.16** | **-17.5%** | **-2.13** | **0.95** |

Fees: total $4528.15.
Exits: {'stop': 436, 'signal': 120}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). The summed curve
ends at -$651.50 (vs -$1,184.82 closed-trade PnL) — the $533.32 gap
is unrealised MTM on positions still open at the final bar.

## Verdict: Loser combined, 556 trades, -$1,184.82, PF 0.95 — effectively breakeven-to-slightly-negative. ETH wins (+$1,297.25, PF 1.18) but BTC loses (-$2,315.55) and HYPE is flat (-$166.53); the single-coin win does not survive aggregation. 78% of exits are stops — the belt-hold reversal rarely runs far enough to beat the 2xATR stop.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
