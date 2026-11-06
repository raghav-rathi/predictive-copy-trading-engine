# Belt Hold Pattern

Steve Nison belt hold: a tall white candle opening on its low after a
downtrend (bullish belt hold, long) or a long black candle opening on its
high after an uptrend (bearish belt hold, short). Body >= 60% of the range,
open within 10% of the range of the extreme, little or no shadow on the far
side. Both directions fired in the backtest (339 long signals, 341 short
signals across the three coins).

## Rules

- Long: downtrend context (close below EMA(20) on at least 3 of the last 5
  prior bars, or 5-bar return below -1%) + bullish belt hold candle: opens
  within 10% of its range of the low, body >= 60% of range, white, upper
  shadow <= 15% of range.
- Short: uptrend context (mirror) + bearish belt hold candle: opens within
  10% of its range of the high, body >= 60% of range, black, lower shadow
  <= 15% of range.
- Exit long: a bearish belt hold appears. Exit short: a bullish belt hold
  appears.
- Trend context uses prior bars only (shifted by 1); the candle shape is the
  signal bar's own OHLC. Zero-range bars can never qualify.

## Source

- Steve Nison — Belt Hold (Japanese Candlestick Charting Techniques, 1991).
  No verified URL.

Paper only, no live execution.
