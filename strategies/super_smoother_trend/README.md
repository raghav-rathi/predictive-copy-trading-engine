# SuperSmoother Trend

John F. Ehlers' SuperSmoother trend crossover. The SuperSmoother
is a 2-pole Butterworth low-pass filter on price — near-zero lag at
low frequencies and a maximally flat passband, so a fast/slow pair
tracks trend turns with less whipsaw than a moving-average
crossover of the same periods.

- **Long:** SuperSmoother(10) crosses above SuperSmoother(30)
- **Short:** SuperSmoother(10) crosses below SuperSmoother(30)
- **Exit:** the opposite cross (the premise is gone)
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 60-bar max hold,
  1% risk/trade, 3x leverage

Parameters: fast SS(10), slow SS(30), ATR(14) for stop/trail.
The filter is an explicit recursion (seeded with the price itself,
so no NaN head):

    a1 = exp(-1.414*pi/n); b1 = 2*a1*cos(1.414*pi/n)
    c2 = b1; c3 = -a1*a1; c1 = 1 - c2 - c3
    filt[i] = c1*(P[i] + P[i-1])/2 + c2*filt[i-1] + c3*filt[i-2]

Usage:

```python
from strategies.data import fetch_candles
from strategies.super_smoother_trend import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=240)
sig = signals.add_signals(indicators.add_indicators(df))  # SS(10)/SS(30) default
```

See BACKTEST.md for the 2026-03-14 → 2026-11-24 Hyperliquid 1h
(BTC/ETH/HYPE) results — honest verdict: loser on BTC and ETH,
winner on HYPE only, combined -$3,825.60 — and CALIBRATION.md for
the (5,20)/(10,30)/(20,50) fast/slow sensitivity check.
