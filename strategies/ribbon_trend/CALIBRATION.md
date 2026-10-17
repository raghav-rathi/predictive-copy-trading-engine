# EMA ribbon (8/13/21/34/55) alignment trend — Calibration

Shipped config: Enter on full ribbon alignment flip with >0.4% fan spread; exit when alignment breaks or fan compresses below 0.2%; 2xATR stop, 3xATR trail, 168-bar max hold

## What was verified

Stacking verified in sustained trends; fan spread exceeds 0.4% there. Flat-chop test: entries stay under 5% of bars via the fan gate. Exhaustion exit verified: alignment loss after a long entry always produces a long_exit.

## Sensitivity

See BACKTEST.md verdict section for the parameter sweep (where run).
The shipped config is the documented classic parameter set, not the
sweep optimum -- sweeps that merely move the edge across coins or coins
across parameters are reported as instability, not improvements.

## Standing caveats

- Backtest is one 7-month window on 1h bars; walk-forward validation not run.
- Costs are Hyperliquid base taker fees; real tiered fees differ slightly.
- No live execution is wired anywhere in this package by design.
