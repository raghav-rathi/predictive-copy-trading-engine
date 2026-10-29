# Counterattack Lines

## Mechanism

Counterattack lines are Steve Nison's two-candle stalemate
reversal (Japanese Candlestick Charting Techniques, ch. 6):
after a trend, a long candle is followed by an opposite-color
candle that gaps against the trend at the open and then
fights all the way back to (nearly) the prior candle's close.
The trend is bridled, not yet reversed — Nison ranks this
below the piercing pattern precisely because the second
candle does NOT push well into the first candle's body, it
merely returns to the prior close.

- **Bullish:** 5-bar downtrend into bar 1, bar 1 long black,
  bar 2 white gapping down at the open (o2 < c1), closing
  within 0.2xATR of bar 1's close, with a body of similar
  size (body ratio within 2/3–3/2).
- **Bearish:** mirror — 5-bar uptrend, long white, black
  candle gapping up at the open and closing nearly at the
  prior close.
- The "nearly the same close" test is in ATR units so it
  scales across BTC/ETH/HYPE price levels.

## Entry / exit rules

- Long entry: bullish counterattack bar while flat.
- Short entry: bearish counterattack bar while flat.
- Long exit: a bearish counterattack bar while long. Short
  exit mirrors.
- Risk layer: 2xATR stop, 2.5xATR trailing stop, 72-bar max
  hold, 1% risk per trade, 3x leverage cap.

## Source

Counterattack lines (Steve Nison, Japanese Candlestick
Charting Techniques, ch. 6)
https://archive.org/stream/JapaneseCandlestickChartingTechniques2ndEditionSteveNison/Japanese%20Candlestick%20Charting%20Techniques%2C%202nd%20Edition%2C%20Steve%20Nison_djvu.txt

## Honest caveats

- The backtest (see BACKTEST.md) loses (-$940 over 27
  trades, PF 0.41): BTC wins 0 of 8 trades with Sharpe -3.24.
  A stalemate candle is not a reversal — on 1h crypto it
  reads more like a pause inside the trend than a turn.
- Nison's own ranking warns about this pattern: it is weaker
  than piercing / dark-cloud cover, and the backtest agrees.
- Paper/backtest only. Nothing here touches live execution.
