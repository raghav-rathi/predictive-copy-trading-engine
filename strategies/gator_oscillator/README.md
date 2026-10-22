# Gator Oscillator States

Bill Williams' Gator Oscillator — the convergence/divergence degree of
the Alligator's three balance lines.

- **Balance lines** on median price (h+l)/2, all Wilder-smoothed
  (SMMA) and forward-displaced (past data only, no lookahead):
  - Jaw = SMMA(median, 13), displaced 8 bars
  - Teeth = SMMA(median, 8), displaced 5 bars
  - Lips = SMMA(median, 5), displaced 3 bars
- **Gator histograms** around zero:
  - Upper = |jaw − teeth| (plotted above zero)
  - Lower = −|teeth − lips| (plotted below zero)
  - A bar is **green** when its |value| is rising vs the prior bar
    (the Alligator opens its mouth); **red** otherwise
- **Williams' four states:** awakes (one bar flips green), eats (both
  green — mouth expanding), fills out (one flips red), sleeps (both
  red — mouth closed)
- **Fan order = direction:** lips > teeth > jaw (bull) or
  lips < teeth < jaw (bear)

Rules:

- **Long:** both histograms flip to green (awakes → eats) AND the fan
  is bull (lips > teeth > jaw)
- **Short:** both flip green AND the fan is bear (lips < teeth < jaw)
- **Exit:** the Gator sleeps (both red) OR the fan order flips against
  the position
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 150-bar max hold,
  1% risk/trade, 3x leverage

Parameters: 13/8/5 SMMA lengths, 8/5/3 displacements, ATR(14) for
stop/trail. WARMUP=40.

Usage:

```python
from strategies.gator_oscillator import indicators, signals, risk

sig = signals.add_signals(indicators.add_indicators(df))  # df with t,o,h,l,c,v
res = run_backtest(sig, risk.RISK, warmup=risk.WARMUP, use_funding=False)
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the jaw-length sensitivity check.

Sources: Gator Oscillator (Bill Williams) —
https://www.ifcmfa.com/en/ntx-indicators/gator-oscillator; Alligator
indicator — https://www.luxalgo.com/blog/alligator-indicator/
