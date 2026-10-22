# SuperSmoother Trend

Trend-cross entries on John Ehlers' SuperSmoother — a 2-pole recursive
IIR low-pass filter whose coefficients come from a DSP analog-filter
prototype (Cybernetic Analysis for Stocks and Futures).

## Mechanism

Ordinary moving averages trade lag for smoothness one-for-one. Ehlers
designed the SuperSmoother from a digital low-pass filter instead, so
it delivers the smoothness of a ~20-bar average with roughly half the
lag of an equivalent SMA (step-response test: the filter reaches 50%
of a unit step in 4 bars vs 9 for SMA(20)).

Coefficients (period=20):

- **a1** = exp(-1.414 × π / 20) ≈ 0.80083
- **b1** = 2 × a1 × cos(1.414 × 180 / 20 degrees) ≈ 1.56231
- **c2** = b1, **c3** = -a1², **c1** = 1 - c2 - c3

Filter recursion on close:

    filt[i] = c1 × (price[i] + price[i-1]) / 2
              + c2 × filt[i-1] + c3 × filt[i-2]

Unity DC gain (c1 / (1 - c2 - c3) = 1), so the filter tracks the price
level itself — a cross of close against the filter is a genuine trend
turn, not an artifact.

## Rules

- **Long:** close crosses above the filter AND the filter is rising
- **Short:** close crosses below the filter AND the filter is falling
- The slope gate keeps entries on the side of the developing trend —
  a cross against a falling filter is usually a pullback pop, not a turn
- **Exit:** the opposite cross of close vs the filter (ungated)
- **Risk:** 2xATR hard stop, 2xATR chandelier trail, 150-bar max hold,
  1% risk/trade, 3x leverage. No fixed target — exits are cross-driven.

Parameters: period=20, ATR(14) for stop/trail. WARMUP=80 (the filter
settles within ~60 bars, with margin).

Usage:

```python
from strategies.data import fetch_candles
from strategies.ehlers_supersmoother import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=260)
sig = signals.add_signals(indicators.add_indicators(df))  # period=20 default
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the period=10/20/40 sensitivity check.

Source: SuperSmoother (John Ehlers) —
https://forex-station.com/post1295578265.html
