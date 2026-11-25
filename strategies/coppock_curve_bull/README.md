# Coppock Curve Bull

Edwin Coppock's Coppock Curve (Barron's, October 15, 1962) — a
long-term momentum oscillator built for monthly bars, translated
to 1h crypto bars. The canonical monthly formula is
WMA(ROC(14) + ROC(11), 10); the monthly original cannot fire on
~8 months of 1h data, so the lookbacks are translated to hours
at 24h/day and the adaptation is documented, not hidden:

- **ROC lookbacks:** 336h (14 days) and 264h (11 days)
- **WMA window:** 240h (10 days), front-weighted (newest bar
  weight 240, oldest weight 1)
- **Long (canonical):** the curve turns up while below zero —
  the below-zero hook Coppock himself traded
- **Short (non-canonical extension):** the curve turns down
  while above zero; documented as an extension, not Coppock's
  original (his system was long-only)
- **Exit:** the opposite turn, or the curve crossing zero
  against the position
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 240-bar max
  hold (slow indicator, long holds), 1% risk/trade, 3x leverage

Parameters: ROC_n = 100 × (C_t − C_{t−n}) / C_{t−n}; Coppock =
WMA(240) of ROC(336) + ROC(264). ATR(14) in the harness for the
stop/trail.

Usage:

```python
from strategies.coppock_curve_bull import indicators, signals, risk

df = indicators.add_indicators(df)  # wma_window=240 default
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 → 2026-11-25 Hyperliquid 1h
(BTC/ETH/HYPE, batch-46 pinned window) results — honest verdict:
loser combined (-$1,712 on 262 trades), HYPE the only positive
coin — and CALIBRATION.md for the WMA-window 120/240/480
sensitivity check and the lookahead audit.
