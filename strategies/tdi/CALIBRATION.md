# Dean Malone Traders Dynamic Index — Calibration

Shipped config: RSI(13) green vs SMA(2) red crosses gated by SMA(34) yellow at 50; exit on the reverse cross or RSI 68/32; 2xATR stop, 3xATR trail, 96-bar max hold

## What was verified

Lines verified: red/yellow are exact SMAs of the green RSI line; band width is exactly 2x1.6185x the 34-bar std. Entry gate verified: every long entry has yellow > 50. The failure is the signal frequency, not the indicator math.

## Sensitivity

See BACKTEST.md verdict section for the parameter sweep (where run).
The shipped config is the documented classic parameter set, not the
sweep optimum -- sweeps that merely move the edge across coins or coins
across parameters are reported as instability, not improvements.

## Standing caveats

- Backtest is one 7-month window on 1h bars; walk-forward validation not run.
- Costs are Hyperliquid base taker fees; real tiered fees differ slightly.
- No live execution is wired anywhere in this package by design.
