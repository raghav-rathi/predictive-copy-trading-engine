# Golden Cross / Death Cross

The textbook long-term trend signal, run on 1h bars: the cross
of a 50-bar average over a 200-bar average is a ~2-day vs ~8-day
trend filter. The cross itself is slow by design — it confirms
a regime change rather than predicting one.

- **Golden Cross:** SMA(50) crosses above SMA(200) → long.
- **Death Cross:** SMA(50) crosses below SMA(200) → short.

No filters: the cross of a 50-bar average over a 200-bar
average is itself the filter — it cannot fire in chop, because
neither average moves fast enough to cross and re-cross on
noise. Adding a confirmation filter would only delay an
already-lagging signal.

## Entries

- **Long:** SMA50 crosses above SMA200.
- **Short:** SMA50 crosses below SMA200.

## Exits

- **long_exit:** SMA50 crosses below SMA200 (the Death Cross).
- **short_exit:** SMA50 crosses above SMA200 (the Golden Cross).

## Risk

2.0xATR hard stop, 3.0xATR chandelier trail, no fixed target
(the opposite cross is the exit), 240-bar (~10-day) max hold
— a cross that hasn't paid within ten days on 1h bars is a
failed regime call, not a slow winner. 1% risk/trade, 3x
leverage cap, long/short symmetric.

Parameters: SMA(50)/SMA(200). All fixed a priori; no
optimization. WARMUP=250.

Usage:

```python
from strategies.golden_cross import indicators, signals, risk

sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the a-priori calibration rationale.

Sources:

- Golden Cross / Death Cross (classic SMA cross) —
  https://www.investopedia.com/terms/g/goldencross.asp
