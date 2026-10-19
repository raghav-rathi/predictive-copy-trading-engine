# Twiggs Money Flow

Money-flow oscillator with a true-range denominator: `mf_i =
v_i*(2*c_i-h_i-l_i)/trange_i`, smoothed as `TMF =
WilderEMA(mf,21)/WilderEMA(v,21)`. Trades zero-line crosses: long above
0, short below 0, exit on cross back. 2xATR hard stop, 60-bar max hold.

Source: https://www.mql5.com/en/market/product/451

Files: `indicators.py`, `signals.py`, `risk.py`, `test_twiggs_money_flow.py`,
`BACKTEST.md`, `CALIBRATION.md`.
