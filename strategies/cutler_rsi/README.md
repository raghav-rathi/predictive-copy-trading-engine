# Cutler RSI

Cutler's RSI (14): Wilder's RSI with simple moving averages of gains/losses instead of Wilder smoothing. Long on cross above 30 from oversold, short on cross below 70 from overbought; exits at the opposite extreme.

Source: Cutler's RSI — https://www.investopedia.com/terms/r/rsi.asp

Layout (same subpackage convention as every strategy in this library):

- `indicators.py` — indicator computation (pure pandas/numpy, causal only)
- `signals.py` — entry/exit signal logic
- `risk.py` — batch-standard risk layer (2xATR stop, 2.5xATR trail, 120-bar max hold, 1% risk/trade, 3x leverage cap)
- `test_cutler_rsi.py` — unit tests (green)
- `BACKTEST.md` — empirical validation on Hyperliquid 1h candles
- `CALIBRATION.md` — parameter notes

Paper only. No live execution is wired anywhere in this package by design.
