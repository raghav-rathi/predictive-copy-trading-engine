# Dynamic Momentum Index

Chande & Kroll's Dynamic Momentum Index (DMI): a variable-
lookback RSI. Volatility sets the window — sd5 = stdev(close,
5), sd_avg = SMA(sd5, 10), Vi = sd5 / sd_avg, TD =
clamp(int(14 / Vi), 5, 30) — so the RSI window shortens
toward 5 bars in volatile stretches and lengthens toward 30
in calm ones. The DMI itself is the RSI over the last TD
price changes, with RS from the simple means of gains and
losses over those TD changes (the definitional form — NOT
Wilder smoothing; see below).

- **Long:** DMI crosses up through 30
- **Short:** DMI crosses down through 70
- **Exit:** DMI crosses back through 50 (long exits on a
  cross below 50, short on a cross above 50)
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 120-bar
  max hold, 1% risk/trade, 3x leverage (the harness stops
  sit behind the 50-cross exit as a safety net for
  gap-through moves)

Parameters: sd window 5, sd-average window 10, base period
14, TD clamped to [5, 30], entry levels 30 / 70, exit level
50. Crosses are transition-only (base.crossed_above /
crossed_below), judged on bar i's close and executed at bar
i+1's open by the harness.

Definitional choice, stated explicitly: Chande's DMI uses a
simple average of gains/losses over the variable TD window.
Wilder smoothing over a changing window has no canonical
definition, so base.rsi (Wilder) is deliberately NOT used
here. Where the TD window has only gains DMI is 100, only
losses 0, and neither (all changes zero) 50. Where sd5 and
sd_avg are both 0 (a perfectly flat stretch) Vi is undefined
and DMI is NaN — no volatility, no momentum reading — and
no signal fires. DMI is NaN until sd_avg is defined (bar
13); WARMUP = 40 covers the spin-up.

Sources: Tushar Chande & Stanley Kroll — "The New Technical
Trader" (1994); Stocks & Commodities V.11:5 "Stochastic RSI
and Dynamic Momentum Index" —
https://www.luxalgo.com/library/concept/dynamic-momentum-index/
and https://docs.wickra.org/Indicators/Indicator-DynamicMomentumIndex

Usage:

```python
from strategies.dynamic_momentum_index import indicators, signals, risk

df = indicators.add_indicators(df)  # base_period=14 defaults
sig = signals.add_signals(df)  # long_level=30.0, short_level=70.0, exit_level=50.0 defaults
```

See BACKTEST.md for the 2026-03-14 → 2026-11-26 Hyperliquid 1h
(BTC/ETH/HYPE, batch-47 pinned window) results and
CALIBRATION.md for the base-period 10/14/21 sensitivity
check.
