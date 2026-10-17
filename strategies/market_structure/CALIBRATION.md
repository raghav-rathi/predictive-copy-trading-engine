# SMC market-structure (BOS/CHoCH) trend — Calibration

Shipped config: Fractal (2,2) swing pivots; bullish/bearish BOS continues the leg, CHoCH reverses; exit when structure breaks the other way; 2xATR stop, 3xATR trail, 168-bar max hold

## What was verified

Pivot/BOS/CHoCH mechanics verified on synthetic legs: continuation BOS entries during the up leg, CHoCH short at the reversal, direction persists through shallow pullbacks. Pivot confirmation lag (RIGHT=2) verified causal. (3,3) sweep: HYPE stable, BTC/ETH still negative -- the failure mode is the market, not the parameter.

## Sensitivity

See BACKTEST.md verdict section for the parameter sweep (where run).
The shipped config is the documented classic parameter set, not the
sweep optimum -- sweeps that merely move the edge across coins or coins
across parameters are reported as instability, not improvements.

## Standing caveats

- Backtest is one 7-month window on 1h bars; walk-forward validation not run.
- Costs are Hyperliquid base taker fees; real tiered fees differ slightly.
- No live execution is wired anywhere in this package by design.
