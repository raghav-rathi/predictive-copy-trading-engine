# Smoothed Heikin-Ashi

## Mechanism

1. Build standard Heikin-Ashi candles: ha_close = (o+h+l+c)/4,
   ha_open recursively averaged from the prior HA open/close,
   ha_high/low as the extremes of price and HA open/close.
2. Smooth ha_open and ha_close each with EMA(5). This is the
   variant under test: smoothing is supposed to strip the
   single-bar noise that makes raw Heikin-Ashi flip on doji-like
   bars.
3. Trade the smoothed candles' direction: long when smoothed HA
   close crosses above smoothed HA open, short on the cross below.

## Entry / exit rules

- **Long entry:** smoothed HA close crosses above smoothed HA open.
- **Short entry:** smoothed HA close crosses below smoothed HA open.
- **Long exit:** smoothed HA close crosses below smoothed HA open
  (the opposite cross — the position lives exactly as long as the
  smoothed trend agrees with it).
- **Short exit:** the opposite cross.
- Risk layer: 2xATR hard stop, 2.5xATR chandelier trail, no fixed
  target, 168-bar (~7-day) max hold, 1% equity risk per trade,
  3x leverage cap.

## Source

Heikin-Ashi candlestick construction (standard) plus EMA(5)
smoothing of the HA open/close — the commonly published
"smoothed Heikin-Ashi" variant, no proprietary claim.

## Honest caveats

- Smoothing does NOT fix Heikin-Ashi whipsaw at 1h: the strategy
  fires 2,235 trades across three coins in seven months and loses
  on all three (see BACKTEST.md). EMA(5) delays flips by a few
  bars but does not reduce their count in chop — it just makes
  each flip arrive later, closer to the reversal that kills it.
- Because exits are the opposite cross, every flip is a trade:
  there is no "flat" state, so chop is traded continuously and
  fees compound (total fees $11,984.73 across the three coins).
- This is the batch's worst strategy by total loss and should not
  be mistaken for a trend filter: at 1h it is a chop amplifier.
