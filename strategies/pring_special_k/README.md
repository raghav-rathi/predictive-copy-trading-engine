# Pring Special K

Martin Pring Special K: weighted sum of 10/15/20/30-bar ROCs (weights 1/2/3/4), smoothed with a 10-bar MA, traded against its own 10-bar signal line. Long on K cross above signal, short on cross below; exits on the opposite cross.

Source: Pring Special K (Martin Pring) — https://school.stockcharts.com/doku.php?id=technical_indicators:special_k

Layout (same subpackage convention as every strategy in this library):

- `indicators.py` — indicator computation (pure pandas/numpy, causal only)
- `signals.py` — entry/exit signal logic
- `risk.py` — batch-standard risk layer (2xATR stop, 2.5xATR trail, 120-bar max hold, 1% risk/trade, 3x leverage cap)
- `test_pring_special_k.py` — unit tests (green)
- `BACKTEST.md` — empirical validation on Hyperliquid 1h candles
- `CALIBRATION.md` — parameter notes

Paper only. No live execution is wired anywhere in this package by design.
