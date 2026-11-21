# Accumulation/Distribution Line — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795269600000) (2026-03-14 22:00 UTC →
2026-11-21 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 6040, ETH 6040, HYPE 6038.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 801 | 25.5% | -7279.66 | -6.15 | -74.9% | -9.09 | 0.59 |
| ETH | 801 | 28.6% | -6099.34 | -4.27 | -61.9% | -7.61 | 0.67 |
| HYPE | 702 | 29.2% | -3597.84 | -2.15 | -38.5% | -5.13 | 0.80 |
| **Combined** | **2304** | **27.7%** | **-16976.83** | **-5.56** | **-57.3%** | **-7.37** | **0.68** |

Fees: total $12242.78.
Exits: BTC {'signal': 503, 'stop': 298}; ETH {'signal': 531, 'stop': 270}; HYPE {'signal': 459, 'stop': 243}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$13,095.66.

## Verdict: LOSER (worst of the batch) — -$16,976.83 on 2,304 trades, combined Sharpe -5.56, MaxDD -57.3%.

All three coins lose heavily. The A/D line is a cumulative sum of
signed volume, so on 1h bars it whipsaws across its SMA(20)
constantly: 2,304 trades in 6,040 bars (~1 trade per 2.6 bars per
coin), 1,493 of them closed by the next opposite cross. Win rates
are 25–29% with profit factors 0.59–0.80, and fees alone ($12,242.78)
are 72% of the total loss — the system churns itself to death. BTC
loses 75% of its $10k start. No parameter was tuned; the spec shipped
as written, and both calibration alternates also lost money (see
CALIBRATION.md).

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 2,304 trades is a large sample and all three coins agree in sign —
  this is a robust loser, not noise.
- The A/D line has no normalization: its level drifts with cumulative
  volume, so an SMA cross is mostly a noise trade on 1h bars.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
