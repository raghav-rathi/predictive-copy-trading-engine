# Funding-Rate Carry — Calibration

Threshold sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, pinned batch-48 window
2026-03-14 22:00 UTC → 2026-11-27 14:00 UTC, 6,184 bars
BTC/ETH, 6,182 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 168-bar max hold; funding PnL from the local cache,
TOTAL = price + funding). The sweep re-runs
`add_signals(df, thresh=X)` -- the threshold is the
strategy's natural knob: 0.0000100 is a looser (more
frequent) trigger, 0.0000125 the shipped setting (90th
percentile of positive fund_avg_24h, pooled -- see
README.md), 0.0000200 a stricter (rarer) one. The exit
level stays at thresh/2 throughout.

| THRESH | Coin | Trades (L/S) | Win% (total) | Price $ | Funding $ | TOTAL $ | PF (total) | Expectancy (total) |
|---|---|---|---|---|---|---|---|---|
| 0.0000100 | BTC | 47 (8/39) | 36.2% | -$594 | +$71 | -$523 | 0.80 | -$11.13 |
| 0.0000100 | ETH | 44 (8/36) | 34.1% | -$431 | +$43 | -$388 | 0.83 | -$8.82 |
| 0.0000100 | HYPE | 53 (0/53) | 37.7% | -$760 | +$48 | -$712 | 0.73 | -$13.43 |
| 0.0000125 (shipped) | BTC | 8 (4/4) | 25.0% | -$282 | +$14 | -$268 | 0.33 | -$33.45 |
| 0.0000125 (shipped) | ETH | 11 (6/5) | 27.3% | -$399 | +$9 | -$390 | 0.38 | -$35.47 |
| 0.0000125 (shipped) | HYPE | 24 (0/24) | 33.3% | -$299 | +$26 | -$273 | 0.76 | -$11.37 |
| 0.0000200 | BTC | 3 (0/3) | 0.0% | -$260 | +$1 | -$259 | 0.00 | -$86.23 |
| 0.0000200 | ETH | 2 (2/0) | 0.0% | -$215 | +$1 | -$214 | 0.00 | -$107.19 |
| 0.0000200 | HYPE | 10 (0/10) | 40.0% | +$505 | +$16 | +$521 | 1.89 | +$52.11 |

## One-line verdict

- **0.0000100:** combined -$1,623 on 144 trades -- the
  looser trigger trades far more often and loses more in
  total, though per-trade expectancy improves (more, smaller
  losses).
- **0.0000125:** the shipped setting -- combined -$931 on
  43 trades.
- **0.0000200:** combined +$48 on 15 trades -- nominally
  positive, carried entirely by HYPE (+$521 on 10 trades,
  PF 1.89) while BTC and ETH lose every trade they take
  (0% win rate on 5 trades combined). Fifteen trades is not
  evidence, and a threshold that is positive only because
  one coin's 10 short trades happened to work is exactly the
  kind of cell that must not be shipped.
- **Shipped decision:** keep THRESH = 0.0000125 as the
  registry config regardless. It was fixed from the funding
  distribution (90th percentile of positive fund_avg_24h)
  BEFORE any backtest was run; the sweep is diagnostic only.
  Funding PnL is positive at every threshold (+$162 / +$49 /
  +$18 combined), which confirms the carry leg is real, but
  it is small at every setting and never covers the price
  leg's losses except in the 15-trade noise cell. Do not ship
  a different threshold on the strength of this sweep.

## Audit

- **Lookahead audit:** no lookahead found. The funding merge
  is a same-bar join on t; fund_avg_24h is a trailing rolling
  mean (bars <= i); ATR(14) is Wilder smoothing; signals use
  only bar-i values. The truncation test
  (`test_no_lookahead_truncation`) confirms indicator and
  signal values at bar j are identical whether computed on
  the full frame or on the frame truncated at j. Funding PnL
  uses only rates with t in [entry_t, exit_t), i.e. hours the
  trade was actually held.
- **Source check:** the funding mechanics (positive rate =
  longs pay shorts; negative rate = shorts pay longs) match
  Hyperliquid's documented funding and the SwoleCharts
  tracker. No deviations from the brief: thresholds are the
  pooled 90th-percentile rule stated in README.md, set before
  PnL was seen.
- **Tests:** 21/21 pass (`python3 -m unittest
  strategies.funding_rate_carry.test_funding_rate_carry`),
  including hand-computed funding-PnL signs and the
  equity-with-funding adjustment.
- **No parameter was tuned to PnL.** THRESH stays 0.0000125.
