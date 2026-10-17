# Dreiss Choppiness-regime Donchian — Calibration

Shipped config: CHOP(14) regime filter (trend < 38.2, chop > 61.8); Donchian(20) breakouts only in trending regimes; exit on regime flip to chop or midline cross; 2xATR stop, 3xATR trail, 120-bar max hold

## What was verified

CHOP bounds verified [0,100]; straight trends score < 38.2, space-filling chop scores > 61.8. Breakout entries verified to never fire during choppy bars. Notable: on 1h crypto CHOP rarely exceeds 61.8, so the chop-exit seldom triggers -- exits come from the midline cross.

## Sensitivity

See BACKTEST.md verdict section for the parameter sweep (where run).
The shipped config is the documented classic parameter set, not the
sweep optimum -- sweeps that merely move the edge across coins or coins
across parameters are reported as instability, not improvements.

## Standing caveats

- Backtest is one 7-month window on 1h bars; walk-forward validation not run.
- Costs are Hyperliquid base taker fees; real tiered fees differ slightly.
- No live execution is wired anywhere in this package by design.
