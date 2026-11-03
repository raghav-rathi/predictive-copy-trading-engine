# Wyckoff Sign of Strength

Wyckoff sign of strength / weakness: a close above the prior 40-bar high on volume over 1.5x its 20-bar average is a sign of strength (long); a close below the prior 40-bar low on the same volume condition is a sign of weakness (short). Exits on close back inside the range.

Source: Wyckoff sign of strength (Richard Wyckoff) — https://school.stockcharts.com/doku.php?id=chart_school:market_analysis:wyckoff_method

Layout (same subpackage convention as every strategy in this library):

- `indicators.py` — indicator computation (pure pandas/numpy, causal only)
- `signals.py` — entry/exit signal logic
- `risk.py` — batch-standard risk layer (2xATR stop, 2.5xATR trail, 120-bar max hold, 1% risk/trade, 3x leverage cap)
- `test_wyckoff_sos.py` — unit tests (green)
- `BACKTEST.md` — empirical validation on Hyperliquid 1h candles
- `CALIBRATION.md` — parameter notes

Paper only. No live execution is wired anywhere in this package by design.
