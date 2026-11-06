# Rounding Bottom — Backtest

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
| BTC | 188 | 21.8% | -4753.93 | -4.80 | -49.8% | -25.29 | 0.41 |
| ETH | 157 | 22.3% | -3623.43 | -3.83 | -38.9% | -23.08 | 0.50 |
| HYPE | 145 | 27.6% | -2052.27 | -2.09 | -22.8% | -14.15 | 0.62 |
| **Combined** | **490** | **23.7%** | **-10429.62** | **-4.96** | **-36.5%** | **-21.28** | **0.50** |

Fees: total $3564.61.
Exits: {'stop': 351, 'signal': 139}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). The summed curve
ends at -$10,402.78 (vs -$10,429.62 closed-trade PnL) — the $26.84
gap is unrealised MTM on positions still open at the final bar.

## Verdict: Loser combined, 490 trades, -$10,429.62, PF 0.50. All three coins lose with ~22–28% win rates; 72% of exits are stops. Neckline breakouts of 60-bar saucers on 1h crypto fail far more often than they follow through — the pattern fires often (714 long / 775 short signals) and loses steadily.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
