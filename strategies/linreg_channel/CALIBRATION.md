# Raff linear-regression channel mean-reversion — Calibration

Shipped config: LSMA(50) +/- 2 sigma of residuals; long the lower-band tag that closes back inside, short the upper-band tag; exit at midline or opposite band; 1.5xATR stop, 2xATR target, 48-bar max hold

## What was verified

LSMA verified against numpy polyfit to 1e-9; on a perfect line the band width collapses as it should. Tag logic verified on a constructed dip: wick through + close back inside fires, and only then. Truncation test proves lookahead-freedom.

## Sensitivity

See BACKTEST.md verdict section for the parameter sweep (where run).
The shipped config is the documented classic parameter set, not the
sweep optimum -- sweeps that merely move the edge across coins or coins
across parameters are reported as instability, not improvements.

## Standing caveats

- Backtest is one 7-month window on 1h bars; walk-forward validation not run.
- Costs are Hyperliquid base taker fees; real tiered fees differ slightly.
- No live execution is wired anywhere in this package by design.
