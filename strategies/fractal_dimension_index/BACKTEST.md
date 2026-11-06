# Fractal Dimension Index — Backtest

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
| BTC | 274 | 23.4% | -4029.20 | -4.60 | -43.2% | -14.71 | 0.47 |
| ETH | 317 | 26.8% | -2591.84 | -2.13 | -31.8% | -8.18 | 0.72 |
| HYPE | 210 | 26.2% | -2219.47 | -2.98 | -24.1% | -10.57 | 0.62 |
| **Combined** | **801** | **25.5%** | **-8840.51** | **-4.52** | **-32.3%** | **-11.04** | — |

Fees: total $5670.12.
Exits: {'signal': 558, 'stop': 243}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). The summed curve's
final net is -$8,797.33 rather than -$8,840.51 because positions were
still open at the window end, carrying +$43.19 of unrealised MTM.

## Verdict: Loser combined, 801 trades, -$8,840.51, PF 0.61. All three coins lose with win rates of 23–27% and a combined Sharpe of -4.52 — the worst batch-28 result by dollars and drawdown (-32.3%). The FDI < 1.4 regime filter does not keep the system out of losing SMA(20) crosses; 70% of exits are signal exits, so trades are churned out quickly at a loss.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
