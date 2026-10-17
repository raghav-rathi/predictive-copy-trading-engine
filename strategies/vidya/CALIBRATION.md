# Chande VIDYA adaptive trend — Calibration

Shipped config: CMO(9)-weighted adaptive average of close; long on cross above VIDYA with rising VIDYA above its 50-bar SMA; exit on cross back; 2xATR stop, 3xATR trail, 168-bar max hold

## What was verified

Recursion verified against an independent loop to 1e-9. Adaptivity verified: in a straight trend VIDYA sits within 2% of price; in chop it lags materially. The failure is the signal, not the indicator.

## Sensitivity

See BACKTEST.md verdict section for the parameter sweep (where run).
The shipped config is the documented classic parameter set, not the
sweep optimum -- sweeps that merely move the edge across coins or coins
across parameters are reported as instability, not improvements.

## Standing caveats

- Backtest is one 7-month window on 1h bars; walk-forward validation not run.
- Costs are Hyperliquid base taker fees; real tiered fees differ slightly.
- No live execution is wired anywhere in this package by design.
