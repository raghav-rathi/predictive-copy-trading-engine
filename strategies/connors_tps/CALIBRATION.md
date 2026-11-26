# Connors TPS — Calibration

Entry-threshold sensitivity on the same Hyperliquid 1h data
as BACKTEST.md (BTC/ETH/HYPE, pinned batch-47 window
2026-03-14 22:00 UTC → 2026-11-26 14:00 UTC, 6,160 bars
BTC/ETH, 6,158 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 10-bar max hold). The RSI(2) entry threshold is the
strategy's natural knob: 20/80 is the stricter (deeper
pullback) setting, 25/75 the book's published 25/75, 30/70
the looser one. The sweep re-runs `add_signals(df,
entry_low=X, entry_high=Y)` — the 70/30 exits, the SMA(200)
filter and the 10-bar time exit stay fixed throughout.

| Entry thresholds | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 20/80 | BTC | 258 | 60.5% | -$1,941 | -2.02 | 0.71 | -$7.52 |
| 20/80 | ETH | 252 | 58.3% | -$1,994 | -2.26 | 0.69 | -$7.91 |
| 20/80 | HYPE | 267 | 58.4% | -$2,057 | -2.44 | 0.67 | -$7.71 |
| 25/75 (shipped) | BTC | 329 | 61.1% | -$1,930 | -1.81 | 0.77 | -$5.87 |
| 25/75 (shipped) | ETH | 315 | 55.6% | -$2,412 | -2.49 | 0.70 | -$7.66 |
| 25/75 (shipped) | HYPE | 330 | 57.3% | -$3,013 | -3.46 | 0.61 | -$9.13 |
| 30/70 | BTC | 381 | 58.5% | -$2,817 | -2.66 | 0.69 | -$7.39 |
| 30/70 | ETH | 386 | 57.5% | -$2,503 | -2.37 | 0.73 | -$6.48 |
| 30/70 | HYPE | 383 | 56.1% | -$3,774 | -4.21 | 0.58 | -$9.85 |

## One-line verdict

- **20/80:** combined -$5,993 on 777 trades — the least-bad
  read (fewest trades, lowest fees at $5,959, most even
  across coins), but still negative on every coin.
- **25/75:** the shipped setting — combined -$7,355 on 974
  trades; the best BTC read in the sweep (-$1,930) and the
  worst HYPE read (-$3,013).
- **30/70:** combined -$9,094 on 1,150 trades — the worst
  combined read; the looser threshold trades the most and
  pays the most fees ($8,336).
- **Shipped decision:** keep the specified entry thresholds
  = 25/75 as the registry config regardless. They were
  fixed before any backtest was run (the book's published
  levels); the sweep is diagnostic only. The 20/80 read
  being "least bad" is in-sample information about a
  still-losing setting, not evidence to ship it — all three
  settings lose on all three coins. Do not ship different
  thresholds on the strength of this sweep.

## Audit

- **Lookahead audit:** no lookahead found. SMA(200) and
  Wilder RSI(2) are causal; the two-consecutive-bar setup
  reads bar i and bar i-1 only; exits are level conditions
  on bar i's RSI(2); no `ichimoku` chikou column is used
  anywhere. The truncation test
  (`test_no_lookahead_truncation`) confirms indicator and
  signal values at bar j are identical whether computed on
  the full frame or on the frame truncated at j.
- **Source check:** the TPS structure (trend filter, RSI(2)
  pullback setup, RSI exit, day-11 time exit) is Connors &
  Alvarez as cited in the README. Two documented deviations:
  the 200-bar trend filter is scaled from daily bars to 200
  1h bars (~8.3 days), stated as an adaptation, not the
  book's daily rule; and the house 2xATR stop / 3xATR trail
  is added where the original system has no stop, required
  by house risk rules. The 10-bar max hold enforces the
  time exit.
- **Tests:** 16/16 pass (`python3 -m unittest
  strategies.connors_tps.test_connors_tps`).
- **No parameter was tuned to PnL.** Entry thresholds stay 25/75.
