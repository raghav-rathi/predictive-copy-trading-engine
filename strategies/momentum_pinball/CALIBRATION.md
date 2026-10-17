# Raschke Momentum Pinball (LBR/RSI) — Calibration

Shipped config: LBR/RSI = 3-period Wilder RSI of the 1-period ROC of close; long on the flip up out of <30, short on the flip down out of >70; exit at the opposite extreme; 1.5xATR stop, 24-bar max hold

## What was verified

Indicator verified: independent loop recomputation of Wilder RSI(3) of diff(1) matches to 1e-6, including the pandas ewm seeding and min_periods masking. Truncation test proves lookahead-freedom. Flip frequency measured: 1 trade per ~7 bars on BTC -- the failure is structural (costs), not a bug.

## Sensitivity

See BACKTEST.md verdict section for the parameter sweep (where run).
The shipped config is the documented classic parameter set, not the
sweep optimum -- sweeps that merely move the edge across coins or coins
across parameters are reported as instability, not improvements.

## Standing caveats

- Backtest is one 7-month window on 1h bars; walk-forward validation not run.
- Costs are Hyperliquid base taker fees; real tiered fees differ slightly.
- No live execution is wired anywhere in this package by design.
