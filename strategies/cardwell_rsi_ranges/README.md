# Cardwell RSI Ranges

Andrew Cardwell range rules on Wilder RSI (14): a bull range holds RSI between 40-80 (20-bar min >= 40), a bear range between 20-60 (20-bar max <= 60). Long on RSI cross above 50 inside a bull range, short on cross below 50 inside a bear range; exits at the range edges (40 / 60).

Source: Cardwell RSI range rules (Andrew Cardwell) — https://school.stockcharts.com/doku.php?id=technical_indicators:relative_strength_index

Layout (same subpackage convention as every strategy in this library):

- `indicators.py` — indicator computation (pure pandas/numpy, causal only)
- `signals.py` — entry/exit signal logic
- `risk.py` — batch-standard risk layer (2xATR stop, 2.5xATR trail, 120-bar max hold, 1% risk/trade, 3x leverage cap)
- `test_cardwell_rsi_ranges.py` — unit tests (green)
- `BACKTEST.md` — empirical validation on Hyperliquid 1h candles
- `CALIBRATION.md` — parameter notes

Paper only. No live execution is wired anywhere in this package by design.
