# Relative Volatility Index

Donald Dorsey Relative Volatility Index (10/10): volatility-weighted RSI — standard deviation of closes split into up/down buckets. Long on cross above 50, short on cross below 50; exits on the opposite cross.

Source: Relative Volatility Index (Donald Dorsey) — https://school.stockcharts.com/doku.php?id=technical_indicators:relative_volatility_index

Layout (same subpackage convention as every strategy in this library):

- `indicators.py` — indicator computation (pure pandas/numpy, causal only)
- `signals.py` — entry/exit signal logic
- `risk.py` — batch-standard risk layer (2xATR stop, 2.5xATR trail, 120-bar max hold, 1% risk/trade, 3x leverage cap)
- `test_relative_volatility_index.py` — unit tests (green)
- `BACKTEST.md` — empirical validation on Hyperliquid 1h candles
- `CALIBRATION.md` — parameter notes

Paper only. No live execution is wired anywhere in this package by design.
