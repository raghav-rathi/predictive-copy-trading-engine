# Ehlers MAMA/FAMA Cross

John Ehlers' MESA Adaptive Moving Average, implemented from his
original code. A Hilbert-transform discriminator measures the market's
dominant cycle period each bar — median price → weighted smoother →
detrender → quadrature pair (I1/Q1) → 90°-shifted pair (jI/jQ) →
smoothed phasor (I2/Q2) → phase-advance (Re/Im) → 360/atan(Im/Re) —
and the smoothing alpha adapts to it: fastLimit when the cycle
shortens, down to slowLimit when it lengthens. MAMA tracks with that
alpha; FAMA is a half-alpha smoothing of MAMA.

- **Long:** MAMA crosses above FAMA *and* close > MAMA
- **Short:** MAMA crosses below FAMA *and* close < MAMA
- **Exit:** the opposite cross
- **Risk:** 2xATR hard stop, 200-bar max hold, 1% risk/trade, 3x leverage

Parameters: fastLimit=0.5, slowLimit=0.05, period clamp [6, 50] bars
(0.67x–1.5x walk from the prior bar), stop 2xATR(14), max hold 200.

Usage mirrors the other engines:

```python
from strategies.mama_fama import SPEC
sig = SPEC.add_signals(SPEC.add_indicators(df, fast_limit=0.5))
```

See BACKTEST.md for the 2026-03-14 → 2026-10-20 Hyperliquid 1h
(BTC/ETH/HYPE) results (honest loser: combined -$11,909) and
CALIBRATION.md for the 0.4/0.5/0.6 fastLimit sweep.
