# Trend Intensity Index

M.H. Pee Trend Intensity Index (30): 100 x sum of up-moves / sum of absolute moves. Long on cross above 80 (strong uptrend), short on cross below 20 (strong downtrend); exits on cross back through 50.

Source: Trend Intensity Index (M.H. Pee) — https://www.incrediblecharts.com/indicators/trend_intensity_index.php

Layout (same subpackage convention as every strategy in this library):

- `indicators.py` — indicator computation (pure pandas/numpy, causal only)
- `signals.py` — entry/exit signal logic
- `risk.py` — batch-standard risk layer (2xATR stop, 2.5xATR trail, 120-bar max hold, 1% risk/trade, 3x leverage cap)
- `test_trend_intensity_index.py` — unit tests (green)
- `BACKTEST.md` — empirical validation on Hyperliquid 1h candles
- `CALIBRATION.md` — parameter notes

Paper only. No live execution is wired anywhere in this package by design.
