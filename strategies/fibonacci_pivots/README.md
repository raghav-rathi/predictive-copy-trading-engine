# Fibonacci Pivots

Fibonacci pivot points on 1h bars: levels from the prior completed 24-bar block (pivot = (H+L+C)/3; R1 = P + 0.382*(H-L), S1 = P - 0.382*(H-L)). Long on close cross above R1, short on cross below S1; exits on cross back through the pivot. Levels are fixed within a block — no intraday repainting.

Source: Fibonacci pivot points — https://school.stockcharts.com/doku.php?id=technical_indicators:pivot_points

Layout (same subpackage convention as every strategy in this library):

- `indicators.py` — indicator computation (pure pandas/numpy, causal only)
- `signals.py` — entry/exit signal logic
- `risk.py` — batch-standard risk layer (2xATR stop, 2.5xATR trail, 120-bar max hold, 1% risk/trade, 3x leverage cap)
- `test_fibonacci_pivots.py` — unit tests (green)
- `BACKTEST.md` — empirical validation on Hyperliquid 1h candles
- `CALIBRATION.md` — parameter notes

Paper only. No live execution is wired anywhere in this package by design.
