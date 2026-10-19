# Fractal Breakout (Bill Williams)

Trade the break of confirmed structure, not the wiggle: 5-bar Bill
Williams fractals (strict local highs/lows with 2 bars each side) mark
resistance/support; a fractal is only tradeable once confirmed 2 bars
late, so levels are shifted forward and forward-filled — no lookahead.

**Signals** — long when the close crosses above the last confirmed
up-fractal level with the close above SMA200 (the Alligator trend gate
is replaced by SMA200, documented in `indicators.py`); short is the
mirror. Exits on a cross back across the fractal level or an opposing
fractal break (which also lets the position flip). 2xATR hard stop,
80-bar max hold.

Source: https://arongroups.co/technical-analyze/bill-williams-indicators/

See `BACKTEST.md` for empirical results and `CALIBRATION.md` for the
fractal-size sensitivity sweep.
