# Laguerre RSI (John Ehlers)

Time-warped RSI: Ehlers' Laguerre filter (gamma=0.5) smooths price before
the RSI-style ratio, so the oscillator reaches 0/1 faster than a standard
RSI and hugs the extremes during real moves.

**Signals** — long when `lrsi` crosses up through 0.2 (oversold reversal),
short when it crosses down through 0.8, exits on the 0.5 centerline.
2xATR hard stop, 50-bar max hold, no trailing/target.

Source: https://doc.stocksharp.com/en/topics/api/indicators/list_of_indicators/laguerre_rsi

See `BACKTEST.md` for empirical results and `CALIBRATION.md` for the
gamma sensitivity sweep.
