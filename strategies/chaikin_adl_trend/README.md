# Chaikin ADL Trend

Trade Marc Chaikin's Accumulation/Distribution Line as a trend
signal: the ADL accumulates money flow volume — where the close
sits inside each bar's range, weighted by volume — so it rises
when buyers consistently lift closes toward the highs on volume
(accumulation) and falls when sellers press closes toward the
lows on volume (distribution).

- **MFM** = ((c − l) − (h − c)) / (h − l), in [−1, 1]; a zero-range
  bar (h == l) maps to 0 instead of dividing by zero.
- **MFV** = MFM × v.
- **ADL** = cumulative sum of MFV.
- **Signal line** = SMA(ADL, 10).
- **Trend filter** = SMA(close, 50).

## Entries (the cross must agree with the trend)

- **Long:** ADL crosses *above* its SMA(10) AND close > SMA(50).
- **Short:** ADL crosses *below* its SMA(10) AND close < SMA(50).

The SMA(50) filter is the whole discipline: a bare ADL cross
whipsaws in chop, so the cross only fires when it agrees with
the medium-term trend.

## Exits

Pure opposite ADL crosses, no trend filter — once the trade is
on, the exit should be trigger-happy, not gated:

- **long_exit:** ADL crosses below its SMA(10)
- **short_exit:** ADL crosses above its SMA(10)

## Risk

1.5xATR hard stop, 2xATR chandelier trail, no fixed target (the
opposite cross is the exit), 72-bar (~3-day) max hold, 1% risk
per trade, 3x leverage cap, long/short symmetric.

Parameters: ADL SMA 10, SMA filter 50, ATR 14. All fixed a
priori; no optimization. WARMUP=70.

Usage:

```python
from strategies.chaikin_adl_trend import indicators, signals, risk

sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the a-priori calibration rationale.

Sources:

- Accumulation/Distribution Line (Marc Chaikin) —
  https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:accumulation_distribution_line
