# Slow Stochastic

George Lane's Slow Stochastic: the classic range oscillator,
smoothed the way Lane himself traded it. %K measures where the
close sits inside the last 14 bars' range; %D is its 3-bar
simple average and is the signal line:

- **%K** = 100 × (close − lowest low 14) / (highest high 14 −
  lowest low 14). 0 = at the 14-bar low, 100 = at the 14-bar high.
- **%D** = SMA(3) of %K.
- A zero 14-bar range (dead-flat window) maps to %K = 50, the
  neutral midpoint.

## Entries (the cross is the trigger, the zone is the filter)

- **Long:** %K crosses *above* %D AND %K < 20 (still
  oversold). The turn is happening off a washed-out low, not
  mid-range noise — a cross at %K = 50 is just the oscillator
  wandering through the middle of its range and is blocked.
- **Short:** exact mirror — %K crosses *below* %D while
  %K > 80 (still overbought).

## Exits

Pure opposite crosses, no zone filter — once the trade is on,
the exit should be trigger-happy, not gated:

- **long_exit:** %K crosses below %D
- **short_exit:** %K crosses above %D

## Risk

1.5xATR hard stop, 2xATR chandelier trail, no fixed target (the
opposite cross is the exit), 72-bar (~3-day) max hold — a
stochastic turn that hasn't resolved in three days was noise,
not a turn. 1% risk/trade, 3x leverage cap, long/short
symmetric.

Parameters: %K 14, %D SMA 3, zones 20/80. All fixed a priori;
no optimization. WARMUP=40.

Usage:

```python
from strategies.slow_stochastic import indicators, signals, risk

sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results
and CALIBRATION.md for the a-priori calibration rationale.

Sources:

- Stochastic Oscillator mechanics —
  https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:stochastic_oscillator
