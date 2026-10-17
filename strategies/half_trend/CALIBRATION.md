# HalfTrend ATR-channel trend — Calibration

Shipped config: Amplitude-50 extremes, ATR(100)/2 x2 channel; stateful line trails below price in uptrends, above in downtrends; flip = entry; 2xATR stop, 3xATR trail, 240-bar max hold

## What was verified

State machine verified on synthetic trends: line trails the correct side, flips mark entries, no bar is ever both entries. Truncation test proves the line at bar i is independent of later data.

## Sensitivity

See BACKTEST.md verdict section for the parameter sweep (where run).
The shipped config is the documented classic parameter set, not the
sweep optimum -- sweeps that merely move the edge across coins or coins
across parameters are reported as instability, not improvements.

## Standing caveats

- Backtest is one 7-month window on 1h bars; walk-forward validation not run.
- Costs are Hyperliquid base taker fees; real tiered fees differ slightly.
- No live execution is wired anywhere in this package by design.
