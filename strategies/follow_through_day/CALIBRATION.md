# Follow-Through Day (O'Neil) — Calibration

Gain-threshold and attempt-window sensitivity on the same
Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE, pinned
batch-49 window 2026-03-14 22:00 UTC → 2026-11-28 14:00 UTC,
6,185 bars BTC/ETH, 6,183 HYPE; same costs/sizing, 2xATR
stop, 3xATR trail, 240-bar max hold). The sweeps re-run
`add_indicators(df, gain_pct=X)` / `add_indicators(df,
attempt_hi=X)` -- everything else stays fixed.

## Gain threshold (attempt window fixed at 4-7)

| Gain | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 1.0% | BTC | 1 | 0.0% | -$107 | — | 0.00 | -$107.00 |
| 1.0% | ETH | 2 | 0.0% | -$166 | -1.44 | 0.00 | -$82.96 |
| 1.0% | HYPE | 5 | 20.0% | +$325 | 1.04 | 2.67 | +$65.00 |
| 1.0% | **Combined** | **8** | **12.5%** | **+$52** | — | — | **+$6.48** |
| 1.5% (shipped) | BTC | 0 | — | $0 | 0.00 | 0.00 | — |
| 1.5% (shipped) | ETH | 2 | 0.0% | -$166 | -1.44 | 0.00 | -$82.96 |
| 1.5% (shipped) | HYPE | 5 | 20.0% | +$325 | 1.04 | 2.67 | +$65.00 |
| 1.5% (shipped) | **Combined** | **7** | **14.3%** | **+$159** | **0.47** | **1.44** | **+$22.73** |
| 2.0% | BTC | 0 | — | $0 | 0.00 | 0.00 | — |
| 2.0% | ETH | 2 | 0.0% | -$166 | -1.44 | 0.00 | -$82.96 |
| 2.0% | HYPE | 4 | 25.0% | +$353 | — | 3.12 | +$88.25 |
| 2.0% | **Combined** | **6** | **16.7%** | **+$187** | — | — | **+$31.19** |

## Attempt window (gain fixed at 1.5%)

| Window | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 4-7 (shipped) | **Combined** | **7** | **14.3%** | **+$159** | **0.47** | **1.44** | **+$22.73** |
| 4-10 | BTC | 1 | 100.0% | +$50 | — | inf | +$50.00 |
| 4-10 | ETH | 3 | 33.3% | +$213 | — | 2.23 | +$71.00 |
| 4-10 | HYPE | 6 | 16.7% | +$224 | — | 1.76 | +$37.33 |
| 4-10 | **Combined** | **10** | **20.0%** | **+$487** | — | — | **+$48.74** |

## One-line verdict

- **Gain 1.0%:** combined +$52 on 8 trades -- one extra
  BTC loser vs shipped; noise.
- **Gain 1.5%:** the shipped setting -- combined +$159 on
  7 trades.
- **Gain 2.0%:** combined +$187 on 6 trades -- one fewer
  HYPE trade; noise.
- **Window 4-10:** combined +$487 on 10 trades -- the
  least-bad variant, still 10 trades; the extra three days
  admit three more FTDs and they happened to win. This is
  not evidence for 4-10 over 4-7.
- **Shipped decision:** keep gain = 1.5% and window = 4-7
  as the registry config regardless. Both were fixed before
  any backtest was run; the sweeps are diagnostic only.
  Every variant is within a few hundred dollars of zero on
  a single-digit trade count, so there is nothing to tune
  toward -- the signal is absent, not mis-parameterized.
  Do not ship a different gain or window on the strength
  of this sweep.

## Audit

- **Lookahead audit:** no lookahead found. Daily aggregates
  use only bars up to the current one; the state machine
  reads daily values in order; the FTD test is evaluated
  only on the completed (23:00) bar; entries are
  crossed_above on the ftd_day flag. The truncation test
  (`test_no_lookahead_truncation`) confirms indicator and
  signal values at bar j are identical whether computed on
  the full frame or on the frame truncated at j.
- **Source check:** the FTD construction (correction, new
  low, rally attempt, 4-7 day window, strong up day on
  rising volume confirms) matches O'Neil via the cited
  TraderLion reference. Documented choices: 20-day
  lookback, 8% correction, 1.5% gain, attempt_low = the
  prior (new-low) day's low, failure checked on later days
  only, expiry after day 7.
- **Tests:** 16/16 pass (`python3 -m unittest
  strategies.follow_through_day.test_follow_through_day`).
- **No parameter was tuned to PnL.** Gain stays 1.5%,
  window stays 4-7.
