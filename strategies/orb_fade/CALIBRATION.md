# Opening Range Breakout Failure Fade — Calibration

OR-window and failure-window sensitivity on the same
Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE, pinned
batch-49 window 2026-03-14 22:00 UTC → 2026-11-28 14:00 UTC,
6,185 bars BTC/ETH, 6,183 HYPE; same costs/sizing, 2xATR
stop, 3xATR trail, 24-bar max hold). The sweeps re-run
`add_indicators(df, or_n=X)` / `add_signals(df,
failure_bars=X)` -- everything else stays fixed.

## OR window (failure window fixed at 6 bars)

| OR window | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 4 bars (shipped) | BTC | 264 | 29.2% | -$2,463 | -1.84 | 0.74 | -$9.33 |
| 4 bars (shipped) | ETH | 248 | 25.4% | -$1,950 | -1.53 | 0.79 | -$7.86 |
| 4 bars (shipped) | HYPE | 271 | 29.2% | -$1,867 | -1.61 | 0.80 | -$6.89 |
| 4 bars (shipped) | **Combined** | **783** | **28.0%** | **-$6,279** | **-2.58** | **0.77** | **-$8.02** |
| 8 bars | BTC | 201 | 26.9% | -$2,393 | -2.17 | 0.68 | -$11.90 |
| 8 bars | ETH | 161 | 26.1% | -$1,655 | -1.44 | 0.74 | -$10.28 |
| 8 bars | HYPE | 202 | 28.2% | -$837 | -0.74 | 0.88 | -$4.14 |
| 8 bars | **Combined** | **564** | **27.1%** | **-$4,885** | — | **0.77** | — |

## Failure window (OR window fixed at 4 bars)

| Failure window | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 6 bars (shipped) | **Combined** | **783** | **28.0%** | **-$6,279** | **-2.58** | **0.77** | **-$8.02** |
| 12 bars | BTC | 297 | 27.9% | -$3,372 | -2.62 | 0.67 | -$11.35 |
| 12 bars | ETH | 290 | 23.8% | -$3,026 | -2.46 | 0.70 | -$10.44 |
| 12 bars | HYPE | 307 | 29.0% | -$1,984 | -1.63 | 0.81 | -$6.46 |
| 12 bars | **Combined** | **894** | **27.0%** | **-$8,382** | — | **0.73** | — |

## One-line verdict

- **OR 4 / fail 6:** the shipped setting -- combined -$6,279
  on 783 trades.
- **OR 8 / fail 6:** combined -$4,885 on 564 trades -- a
  wider (8-bar) opening range is broken less often, so the
  strategy fades less and churns less; still a large loser.
- **OR 4 / fail 12:** combined -$8,382 on 894 trades -- a
  longer failure window admits more late, stale fades and
  loses more.
- **Shipped decision:** keep OR window = 4 bars and failure
  window = 6 bars as the registry config regardless. Both
  were fixed before any backtest was run; the sweeps are
  diagnostic only. The OR-8 variant being less bad is a
  churn reduction, not an edge appearing -- it still loses
  $4,885. Do not ship a different window on the strength of
  this sweep.

## Audit

- **Lookahead audit:** no lookahead found. The opening
  range is computed only from the day's 00:00-03:00 bars
  and exposed from 04:00 on; breaks and failures are
  crossed_above / crossed_below on levels known at the bar's
  close; the pending-setup state machine only reads bars up
  to the current one; exit levels are frozen at the entry
  bar. The truncation test
  (`test_no_lookahead_truncation`) confirms indicator and
  signal values at bar j are identical whether computed on
  the full frame or on the frame truncated at j.
- **Source check:** the construction (UTC-day opening range
  from the first 4 bars, trade the breakout failure back
  inside the range) matches the cited ORB-failure reference.
  Documented choices: the level series starts at 04:00 (so
  the first detectable break is 05:00); the frozen break
  level is carried on the break bar itself for cross
  detection; pending setups cancel at the day boundary;
  exit levels freeze at entry.
- **Tests:** 19/19 pass (`python3 -m unittest
  strategies.orb_fade.test_orb_fade`).
- **No parameter was tuned to PnL.** OR window stays 4 bars,
  failure window stays 6 bars.
