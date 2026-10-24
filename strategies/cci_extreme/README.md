# CCI Extreme

Donald Lambert's Commodity Channel Index, traded the classic
way: not the touch of an extreme level, but the *return*
through it. CCI measures how far the typical price has strayed
from its own average, in units of mean deviation:

- **tp** = (h + l + c) / 3
- **sma** = SMA(tp, 20)
- **md** = mean(|tp − sma|) over the same 20 bars (the current
  window's mean applied to every bar in the window, the
  canonical TA-Lib definition)
- **cci** = (tp − sma) / (0.015 × md)

The 0.015 constant scales CCI so that ~70–80% of readings fall
inside ±100 in Lambert's original design. A zero mean
deviation (dead-flat window) maps to CCI = 0, the neutral
midpoint.

## Entries (the return through the level, not the touch)

- **Long:** CCI crosses *above* −100 from below. The washout
  is ending, not deepening — buying while CCI is still falling
  through −100 would catch the falling knife; the cross is
  what confirms the stretch is releasing.
- **Short:** exact mirror — CCI crosses *below* +100 from
  above.

## Exits

Zero-line crosses in the adverse direction — a long that has
mean-reverted all the way back to CCI = 0 has done its job,
and if it then crosses below zero the reversion has overshot
into the other side's territory:

- **long_exit:** CCI crosses below 0
- **short_exit:** CCI crosses above 0

Exits deliberately carry no level filter — once the trade is
on, the zero cross is trigger-happy.

## Risk

2.0xATR hard stop, 2.5xATR chandelier trail, no fixed target
(the zero-line cross is the exit), 96-bar (~4-day) max hold —
a stretch that hasn't snapped back in four days is a new
regime, not a stretch. 1% risk/trade, 3x leverage cap,
long/short symmetric.

Parameters: CCI 20, levels ±100, zero-line exit. All fixed a
priori; no optimization. WARMUP=50.

Usage:

```python
from strategies.cci_extreme import indicators, signals, risk

sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results
and CALIBRATION.md for the a-priori calibration rationale.

Sources:

- Commodity Channel Index mechanics —
  https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:commodity_channel_index
