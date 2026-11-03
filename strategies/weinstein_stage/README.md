# Weinstein Stage Analysis

Stan Weinstein stage analysis on 1h bars (adapted): Stage 2 long when close is above both EMA150 and EMA200 with EMA200 rising over 10 bars; Stage 4 short when close is below both with EMA200 falling. Entries on the first bar of each stage; exits on close crossing back through EMA150.

Source: Weinstein stage analysis (Stan Weinstein) — https://www.investopedia.com/terms/s/stage-analysis.asp

Layout (same subpackage convention as every strategy in this library):

- `indicators.py` — indicator computation (pure pandas/numpy, causal only)
- `signals.py` — entry/exit signal logic
- `risk.py` — batch-standard risk layer (2xATR stop, 2.5xATR trail, 120-bar max hold, 1% risk/trade, 3x leverage cap)
- `test_weinstein_stage.py` — unit tests (green)
- `BACKTEST.md` — empirical validation on Hyperliquid 1h candles
- `CALIBRATION.md` — parameter notes

Paper only. No live execution is wired anywhere in this package by design.
