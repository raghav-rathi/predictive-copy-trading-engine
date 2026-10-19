# TEMA Trend (Patrick Mulloy)

`TEMA(n) = 3*EMA1 - 3*EMA2 + EMA3` lag-reduced trend line. TEMA20/TEMA50
cross with an SMA200 regime filter: long on cross-up above SMA200, short
on cross-down below SMA200, exit on the cross flipping back. 2.5xATR
stop, 3xATR chandelier trail, 120-bar max hold.

Sources:
- https://abovethegreenline.com/what-is-the-triple-exponential-moving-average-tema/
- https://www.definedgesecurities.com/library/tema/

Files: `indicators.py`, `signals.py`, `risk.py`, `test_tema_trend.py`,
`BACKTEST.md`, `CALIBRATION.md`.
