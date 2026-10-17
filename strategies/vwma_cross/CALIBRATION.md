# VWMA(20/50) volume-conviction cross — Calibration

Shipped config: Typical-price VWMA(20) vs VWMA(50) cross gated on volume above its 20-bar average; exit on the cross back; 2xATR stop, 3xATR trail, 120-bar max hold

## What was verified

VWMA verified against a manual rolling computation to 1e-9. Heavy-volume bar test: the fast line jumps above the slow one as designed. Volume gate verified: crosses without volume confirmation do not enter.

## Sensitivity

See BACKTEST.md verdict section for the parameter sweep (where run).
The shipped config is the documented classic parameter set, not the
sweep optimum -- sweeps that merely move the edge across coins or coins
across parameters are reported as instability, not improvements.

## Standing caveats

- Backtest is one 7-month window on 1h bars; walk-forward validation not run.
- Costs are Hyperliquid base taker fees; real tiered fees differ slightly.
- No live execution is wired anywhere in this package by design.
