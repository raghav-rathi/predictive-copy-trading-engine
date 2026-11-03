# Kairi Relative Index

Kairi Relative Index (25): (close - SMA25) / SMA25 x 100. Mean reversion: long on recovery cross above -5 after an oversold dip, short on breakdown cross below +5 after an overbought peak; exits at the mean (0).

Source: Kairi Relative Index — https://www.investopedia.com/terms/k/kairi-relative-index-kri.asp

Layout (same subpackage convention as every strategy in this library):

- `indicators.py` — indicator computation (pure pandas/numpy, causal only)
- `signals.py` — entry/exit signal logic
- `risk.py` — batch-standard risk layer (2xATR stop, 2.5xATR trail, 120-bar max hold, 1% risk/trade, 3x leverage cap)
- `test_kairi_index.py` — unit tests (green)
- `BACKTEST.md` — empirical validation on Hyperliquid 1h candles
- `CALIBRATION.md` — parameter notes

Paper only. No live execution is wired anywhere in this package by design.
