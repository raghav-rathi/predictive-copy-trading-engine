# Percentage Price Oscillator — Calibration

Signal-period sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, pinned batch-46 window
2026-03-14 22:00 UTC → 2026-11-25 14:00 UTC, 6,136 bars
BTC/ETH, 6,134 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 60-bar max hold). The signal period is the strategy's
natural knob: how much the PPO signal line is smoothed — 5
reacts fast (more crosses), 14 reacts slow (fewer, later
crosses). The sweep re-runs `add_indicators(df, signal=X)`
only — signals and risk are unchanged.

| Signal | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 5 | BTC | 235 | 27.2% | -$2,685 | -2.07 | 0.67 | -$11.43 |
| 5 | ETH | 220 | 27.3% | -$1,103 | -0.58 | 0.86 | -$5.01 |
| 5 | HYPE | 207 | 28.0% | -$1,490 | -1.31 | 0.77 | -$7.20 |
| 9 (shipped) | BTC | 167 | 31.7% | -$1,137 | -0.73 | 0.83 | -$6.81 |
| 9 (shipped) | ETH | 167 | 28.1% | -$863 | -0.46 | 0.87 | -$5.17 |
| 9 (shipped) | HYPE | 163 | 27.6% | -$1,545 | -1.49 | 0.74 | -$9.48 |
| 14 | BTC | 135 | 28.9% | -$1,177 | -0.93 | 0.79 | -$8.72 |
| 14 | ETH | 142 | 33.1% | +$113 | +0.18 | 1.02 | +$0.80 |
| 14 | HYPE | 126 | 30.2% | -$823 | -0.78 | 0.82 | -$6.53 |

## One-line verdict

- **5:** the worst combined read (-$5,279, 662 trades) —
  a faster signal line just means more crosses, more chop,
  more fees ($4,672).
- **9:** the shipped setting — combined -$3,545, 497 trades,
  PF 0.82. Loser on all three coins.
- **14:** the least bad combined read (-$1,887, 403 trades)
  and the only positive single-coin cell in the whole sweep
  (ETH +$113, PF 1.02) — but BTC (-$1,177) and HYPE (-$823)
  are still losers, and the "improvement" is just fewer,
  later trades, not better entries.
- **Shipped decision:** keep the specified signal period 9
  as the registry config regardless. It was fixed before any
  backtest was run; adopting 14 *because* it loses less
  in-sample would be in-sample selection on a knob whose
  effect is monotone only in trade count, not in edge (all
  three values are combined losers with PF 0.77–0.88). The
  honest read: no signal smoothing rescues a lagging
  cross on 1h crypto. Do not ship 14 on the strength of
  this sweep.

## Batch-46 audit (2026-11-25)

- **Lookahead audit:** no lookahead found. PPO, signal and
  histogram are causal EMAs of closes through bar j; signals
  use `crossed_above`/`crossed_below` on bars i and i−1 only,
  plus the current bar's PPO sign. The truncation test
  (`test_no_lookahead_truncation`) confirms indicator and
  signal values at bar j are identical whether computed on
  the full frame or on the frame truncated at j.
- **Source check:** the StockCharts ChartSchool PPO article
  (verified via search 2026-11-25) defines PPO as
  100 × (12-day EMA − 26-day EMA) / 26-day EMA, the signal
  line as a 9-day EMA of PPO, and the histogram as PPO minus
  its signal line — exactly as implemented. No bug found.
- **Tests:** 13/13 pass (`python3 -m unittest
  strategies.ppo_oscillator.test_ppo_oscillator`).
- **No parameter was tuned to PnL.** Signal period stays 9.
