# CVD Trend

Order-flow trend entries on Cumulative Volume Delta, built from 1h
candles via the standard close-location proxy (true CVD needs
tick-level bid/ask data, which 1h candles do not carry).

- **Close location** cl = (c − l) / (h − l) (0 at the low, 1 at the high)
- **buy_vol** = v × cl, **sell_vol** = v − buy_vol
- **delta** = buy_vol − sell_vol = v × (2·cl − 1)
- **CVD** = cumsum(delta)
- **Long:** EMA(CVD,20) slope turns positive (rising for 2 consecutive
  bars) with close above EMA(50)
- **Short:** EMA(CVD,20) slope turns negative (falling for 2 bars)
  with close below EMA(50)
- **Exit:** the CVD slope reverses
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 150-bar max hold,
  1% risk/trade, 3x leverage

Parameters: CVD EMA length 20, price EMA 50, ATR(14) for stop/trail.
WARMUP=80.

Usage:

```python
from strategies.data import fetch_candles
from strategies.cvd_trend import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=260)
sig = signals.add_signals(indicators.add_indicators(df))  # cvd_n=20, price_n=50 default
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the CVD-EMA 10/20/30 sensitivity check.

Source: Cumulative Volume Delta (CVD) —
https://www.quantvps.com/blog/cumulative-volume-delta

## Honest caveats

- **The close-location proxy is an approximation, not true CVD.**
  Real CVD classifies each trade at the bid or ask; this engine
  guesses the split from where the bar closed inside its range. On a
  bar that closes near its high after dipping low (or vice versa) the
  proxy can sign the whole bar's volume wrong, and on wide-range /
  doji bars it is close to a coin flip. Any venue with real tick data
  would measure a different CVD.
- **CVD is path-dependent and never resets here.** The cumulative sum
  runs from the first bar of the window, so its level is arbitrary;
  only the EMA slope is used — deliberately, so the anchor does not
  leak into the signal.
- The slope-reversal exit is fast: a single negative-slope bar exits
  a long, so positions often last only a few bars and the 2xATR stop
  is hit before the 3xATR trail can pay (win rates 29–32%, PF 0.71–0.87).
- Single 7-month crypto window; results are paper-only, funding
  unmodeled, next-bar-open execution.
