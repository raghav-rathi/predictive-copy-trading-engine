# Fibonacci Fan

Fibonacci fan (rolling 50-bar leg): fan lines radiate from the window low through the 38.2% and 61.8% retracement points of the low-to-high leg, extended forward at the leg's slope. Long on close cross above the 38.2% fan line, short on cross below the 61.8% fan line; exits on the opposite cross. Redrawn each bar from data through that bar only — no repainting of past signals.

Source: Fibonacci fan (classic charting) — https://school.stockcharts.com/doku.php?id=technical_indicators:fibonacci_fan

Layout (same subpackage convention as every strategy in this library):

- `indicators.py` — indicator computation (pure pandas/numpy, causal only)
- `signals.py` — entry/exit signal logic
- `risk.py` — batch-standard risk layer (2xATR stop, 2.5xATR trail, 120-bar max hold, 1% risk/trade, 3x leverage cap)
- `test_fibonacci_fan.py` — unit tests (green)
- `BACKTEST.md` — empirical validation on Hyperliquid 1h candles
- `CALIBRATION.md` — parameter notes

Paper only. No live execution is wired anywhere in this package by design.
