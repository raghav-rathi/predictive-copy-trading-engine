# Blau Double Smoothed Stochastic

William Blau Double Smoothed Stochastic (21, 3, 3): stochastic %K double-smoothed with EMAs and traded against its 3-bar EMA trigger. Long on DSS cross above trigger, short on cross below; exits on the opposite cross.

Source: Double Smoothed Stochastic (William Blau) — https://school.stockcharts.com/doku.php?id=technical_indicators:double_smoothed_stochastic

Layout (same subpackage convention as every strategy in this library):

- `indicators.py` — indicator computation (pure pandas/numpy, causal only)
- `signals.py` — entry/exit signal logic
- `risk.py` — batch-standard risk layer (2xATR stop, 2.5xATR trail, 120-bar max hold, 1% risk/trade, 3x leverage cap)
- `test_blau_dss.py` — unit tests (green)
- `BACKTEST.md` — empirical validation on Hyperliquid 1h candles
- `CALIBRATION.md` — parameter notes

Paper only. No live execution is wired anywhere in this package by design.
