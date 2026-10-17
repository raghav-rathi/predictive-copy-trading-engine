# ICT liquidity-sweep (stop-hunt) reversal — Calibration

Shipped config: Wick >0.25 ATR through the 20-bar swing extreme with a close back inside: short the buy-side sweep, long the sell-side sweep; exit on opposite sweep or a closing break; 2.5xATR stop, 2xATR target, 48-bar max hold

## What was verified

Sweep detector verified on constructed bars: wick-through + close-inside fires, close-beyond does not (breakout, not a sweep), sub-0.25-ATR pokes are rejected. Breakout-close invalidation exits the faded position as designed.

## Sensitivity

See BACKTEST.md verdict section for the parameter sweep (where run).
The shipped config is the documented classic parameter set, not the
sweep optimum -- sweeps that merely move the edge across coins or coins
across parameters are reported as instability, not improvements.

## Standing caveats

- Backtest is one 7-month window on 1h bars; walk-forward validation not run.
- Costs are Hyperliquid base taker fees; real tiered fees differ slightly.
- No live execution is wired anywhere in this package by design.
