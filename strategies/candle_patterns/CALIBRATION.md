# Nison candlestick pattern reversal — Calibration

Shipped config: Bullish/bearish engulfing + pin bars (wick >= 2x body, body in favorable third, range >= 0.5 ATR); enter the pattern, exit on the opposite pattern; 1.5xATR stop, 2xATR target, 24-bar max hold

## What was verified

Pattern detectors verified on constructed bars: engulfing requires body engulfment, pin bars require the wick/body geometry, centered doji bars are rejected. Exit wiring is exactly the opposite-pattern flag. Indicator correct; the timeframe is wrong for the idea.

## Sensitivity

See BACKTEST.md verdict section for the parameter sweep (where run).
The shipped config is the documented classic parameter set, not the
sweep optimum -- sweeps that merely move the edge across coins or coins
across parameters are reported as instability, not improvements.

## Standing caveats

- Backtest is one 7-month window on 1h bars; walk-forward validation not run.
- Costs are Hyperliquid base taker fees; real tiered fees differ slightly.
- No live execution is wired anywhere in this package by design.
