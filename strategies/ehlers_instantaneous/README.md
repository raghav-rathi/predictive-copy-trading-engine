# Ehlers Instantaneous Trendline

Trade John Ehlers' Instantaneous Trendline (IT) as a
trend-birth signal. The IT is a second-order recursive filter
with alpha = 0.07 that smooths price with far less lag than an
SMA/EMA of comparable smoothness — it tracks price closely in
trends, so a close crossing it marks a genuine trend turn
rather than a lagging-average event.

With alpha = 0.07:

    IT[i] = (alpha − alpha²/4)·P[i] + 0.5·alpha²·P[i−1]
          − (alpha − 0.75·alpha²)·P[i−2]
          + 2·(1−alpha)·IT[i−1] − (1−alpha)²·IT[i−2]

where P is close (the assigned spec uses close; some Ehlers
presentations use the (h+l)/2 median price instead — the
difference is a smoothing-input choice, not a different filter).
The coefficients sum to 1, so a flat price series reproduces
itself exactly (unit-tested). Seeded with price: IT[0] = P[0],
IT[1] = P[1]. Strictly causal — no lookahead.

## Entries (the cross is the whole thesis)

- **Long:** close crosses *above* the IT — price has just broken
  above its own low-lag smoothed trend.
- **Short:** close crosses *below* the IT.

Deliberately no extra filter: the filter's low lag IS the edge
claimed for it, and adding an ADX or slope gate would turn it
into a different strategy. In chop price ping-pongs across any
smoother, which is the known cost of the setup; the ATR
stop/trail and 72-bar max hold are the only defences, by design.

## Exits

Pure opposite crosses:

- **long_exit:** close crosses below the IT
- **short_exit:** close crosses above the IT

## Risk

1.5xATR hard stop, 2xATR chandelier trail, no fixed target (the
opposite cross is the exit), 72-bar (~3-day) max hold, 1% risk
per trade, 3x leverage cap, long/short symmetric.

Parameters: alpha 0.07, ATR 14. All fixed a priori; no
optimization. WARMUP=60.

Usage:

```python
from strategies.ehlers_instantaneous import indicators, signals, risk

sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the a-priori calibration rationale.

Sources:

- Instantaneous Trendline (John Ehlers, Cycle Analytics for
  Traders) — https://www.fmz.com/lang/en/strategy/436000
