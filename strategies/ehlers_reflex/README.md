# Reflex Zero-Lag

Zero-lag trend entries on John Ehlers' **Reflex** oscillator
(TASC, February 2020).

- **Smooth:** close → Ehlers 2-pole SuperSmoother(20)
  (`a1 = exp(-1.414·π/20)`, `b1 = 2·a1·cos(1.414·180°/20)`)
- **Detrend:** `Slope = (filt − filt.shift(20)) / 20`;
  `Sum = Σ_{k=1..20} ((filt + k·Slope) − filt.shift(k))`
- **Normalize:** `MS = 0.04·Sum² + 0.96·MS.shift(1)`;
  `Reflex = Sum / √MS` (0/0 guarded)
- **Long:** Reflex crosses above zero
- **Short:** Reflex crosses below zero
- **Exit:** the opposite zero cross (Reflex changing sign means the
  leg failed)
- **Risk:** 2xATR hard stop, 2.5xATR chandelier trail, 150-bar max
  hold, 1% risk/trade, 3x leverage

Parameters: length=20, MS alpha=0.04, ATR(14) for stop/trail.
WARMUP=100 (SuperSmoother(20) transient + the length-20 shift
lookback, with margin). **The length=20 was fixed a priori** —
adopted before any backtest ran, not from the sweep in
CALIBRATION.md.

Usage:

```python
import pandas as pd
from strategies.ehlers_reflex import indicators, signals, risk
from strategies.backtest import run_backtest

df = pd.read_csv("data/candles/BTC_1h.csv")
sig = signals.add_signals(indicators.add_indicators(df))  # length=20 default
res = run_backtest(sig, risk.RISK, coin="BTC", warmup=risk.WARMUP,
                   use_funding=False)
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the 10/20/40 sensitivity check.

Source: Reflex (John Ehlers, TASC Feb 2020) —
https://forex-station.com/download/file.php?id=3357914&sid=f0c366b7fa15f05758951129dc3ccff7
