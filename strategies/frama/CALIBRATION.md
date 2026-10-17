# Ehlers FRAMA fractal-adaptive trend — Calibration

Shipped config: Fractal-dimension alpha (N=16) adaptive average of (h+l)/2; long on close crossing above FRAMA with slope>0 and FRAMA above its 100-bar SMA; exit on cross back; 2xATR stop, 3xATR trail, 168-bar max hold

## What was verified

Alpha verified in [0.01,1], dimension in [1,2] on all bars. Straight-line test: FRAMA == price to 2%. Chop test: FRAMA moves less than price. Truncation test proves lookahead-freedom. Indicator correct; signal loses.

## Sensitivity

See BACKTEST.md verdict section for the parameter sweep (where run).
The shipped config is the documented classic parameter set, not the
sweep optimum -- sweeps that merely move the edge across coins or coins
across parameters are reported as instability, not improvements.

## Standing caveats

- Backtest is one 7-month window on 1h bars; walk-forward validation not run.
- Costs are Hyperliquid base taker fees; real tiered fees differ slightly.
- No live execution is wired anywhere in this package by design.
