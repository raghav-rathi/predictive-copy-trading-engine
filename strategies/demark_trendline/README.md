# DeMark Trendline Breakout

Tom DeMark TD trendlines: trendlines through the last two confirmed pivot highs (downtrend line) and last two confirmed pivot lows (uptrend line); pivots confirm with a 2-bar lag, so no lookahead. Long on close cross above the downtrend line, short on cross below the uptrend line; exits on the opposite cross.

Source: DeMark TD trendlines (Tom DeMark) — https://www.investopedia.com/terms/d/demark.asp

Layout (same subpackage convention as every strategy in this library):

- `indicators.py` — indicator computation (pure pandas/numpy, causal only)
- `signals.py` — entry/exit signal logic
- `risk.py` — batch-standard risk layer (2xATR stop, 2.5xATR trail, 120-bar max hold, 1% risk/trade, 3x leverage cap)
- `test_demark_trendline.py` — unit tests (green)
- `BACKTEST.md` — empirical validation on Hyperliquid 1h candles
- `CALIBRATION.md` — parameter notes

Paper only. No live execution is wired anywhere in this package by design.
