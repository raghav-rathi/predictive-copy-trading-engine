# Consecutive Days Fade (Connors) — Calibration

Streak-threshold and exit-SMA sensitivity on the same
Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE, pinned
batch-49 window 2026-03-14 22:00 UTC → 2026-11-28 14:00 UTC,
6,185 bars BTC/ETH, 6,183 HYPE; same costs/sizing, 2xATR
stop, 3xATR trail, 24-bar max hold). The sweeps re-run
`add_signals(df, streak_n=X)` / `add_indicators(df,
sma_n=X)` -- everything else stays fixed.

## Streak threshold (exit SMA fixed at 10)

| Streak | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 3 | BTC | 662 | 57.3% | -$5,105 | -4.33 | 0.65 | -$7.71 |
| 3 | ETH | 659 | 58.3% | -$4,630 | -3.78 | 0.71 | -$7.03 |
| 3 | HYPE | 683 | 61.5% | -$3,217 | -2.38 | 0.82 | -$4.71 |
| 3 | **Combined** | **2,004** | **59.0%** | **-$12,952** | — | — | — |
| 4 (shipped) | BTC | 309 | 58.9% | -$3,657 | -3.86 | 0.62 | -$11.84 |
| 4 (shipped) | ETH | 318 | 56.9% | -$3,224 | -3.31 | 0.67 | -$10.14 |
| 4 (shipped) | HYPE | 359 | 64.1% | -$518 | -0.39 | 0.95 | -$1.44 |
| 4 (shipped) | **Combined** | **986** | **60.1%** | **-$7,399** | **-3.51** | **0.76** | **-$7.50** |
| 5 | BTC | 141 | 55.3% | -$2,270 | -3.13 | 0.57 | -$16.10 |
| 5 | ETH | 153 | 55.6% | -$856 | -1.03 | 0.83 | -$5.59 |
| 5 | HYPE | 165 | 55.8% | -$1,880 | -2.14 | 0.69 | -$11.39 |
| 5 | **Combined** | **459** | **55.6%** | **-$5,006** | — | — | — |

## Exit SMA (streak fixed at 4)

| Exit SMA | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 5 | BTC | 317 | 56.2% | -$3,562 | -4.45 | 0.56 | -$11.24 |
| 5 | ETH | 326 | 58.3% | -$2,724 | -3.16 | 0.64 | -$8.36 |
| 5 | HYPE | 364 | 64.8% | -$696 | -0.71 | 0.92 | -$1.91 |
| 5 | **Combined** | **1,007** | **60.0%** | **-$6,981** | — | — | — |
| 10 (shipped) | **Combined** | **986** | **60.1%** | **-$7,399** | **-3.51** | **0.76** | **-$7.50** |
| 20 | BTC | 299 | 50.5% | -$3,945 | -3.66 | 0.64 | -$13.19 |
| 20 | ETH | 311 | 53.1% | -$3,516 | -3.30 | 0.68 | -$11.31 |
| 20 | HYPE | 352 | 60.5% | +$844 | +0.69 | 1.06 | +$2.40 |
| 20 | **Combined** | **962** | **55.0%** | **-$6,617** | — | — | — |

## One-line verdict

- **Streak 3:** combined -$12,952 on 2,004 trades -- fading
  earlier just doubles the churn; same failure mode, more
  of it.
- **Streak 4:** the shipped setting -- combined -$7,399
  on 986 trades, 60.1% win rate, PF 0.76.
- **Streak 5:** combined -$5,006 on 459 trades -- the
  least-bad variant, still a clear loser; fewer, larger
  losses (expectancy -$16.10 on BTC). Waiting longer does
  not fix the payoff asymmetry.
- **Exit SMA 5:** combined -$6,981 -- a faster exit banks
  the small reversion sooner and loses slightly less.
- **Exit SMA 10:** the shipped setting -- combined -$7,399.
- **Exit SMA 20:** combined -$6,617 -- HYPE alone turns
  positive (+$844, PF 1.06) but BTC/ETH still lose
  -$3,945/-$3,516; one coin's green cell is not an edge.
- **Shipped decision:** keep streak = 4 and exit SMA = 10
  as the registry config regardless. Both were fixed from
  the source before any backtest was run; the sweeps are
  diagnostic only. No swept variant is profitable combined,
  so there is nothing to tune toward -- the edge is absent,
  not mis-parameterized. Do not ship streak 5 or SMA 20 on
  the strength of this sweep.

## Audit

- **Lookahead audit:** no lookahead found. Streaks count
  only closes through the current bar; SMA(10) is a causal
  rolling mean; entries are crossed_above on the streak
  count. The truncation test
  (`test_no_lookahead_truncation`) confirms indicator and
  signal values at bar j are identical whether computed on
  the full frame or on the frame truncated at j.
- **Source check:** the streak construction (fade 3+
  consecutive up/down closes, effect growing with the
  streak) matches the cited Connors reference. Two
  documented choices: threshold fixed at 4 (the source
  studies 3+; 4 is the shipped reading, swept at 3/5) and
  the exit on a close crossing SMA(10) (the source does
  not fix an exit; the mean-reversion exit is the
  strategy's own rule).
- **Tests:** 15/15 pass (`python3 -m unittest
  strategies.streak_fade.test_streak_fade`).
- **No parameter was tuned to PnL.** Streak stays 4, exit
  SMA stays 10.
