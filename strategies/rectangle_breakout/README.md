# Rectangle Breakout

## Mechanism

A rectangle is a sideways consolidation bounded by a horizontal
support and resistance. This engine watches the trailing 20-bar
range (prior bars only — never the current bar, so the range is
known before the breakout bar closes):

- **Range:** high = max high of the prior 20 bars, low = min low
  of the prior 20 bars.
- **Tight:** range width < 4% of the range midpoint.
- **Held:** the trailing 20-bar window was itself tight on at
  least 15 consecutive prior bars (the consolidation is
  established, not a one-bar fluke).
- **Breakout:** close above the range high (long) or below the
  range low (short), with volume above 1.2x the 20-bar average
  volume.

## Entry / exit rules

- Long entry: tight + held ≥ 15 bars + close > range high +
  volume > 1.2x average.
- Short entry: mirror below the range low.
- Long exit: close back below the range low, or a short breakout
  on the same bar. Short exit mirrors.
- Risk layer (not signal logic): 2xATR stop, 2.5xATR trailing
  stop, 168-bar max hold, 1% risk per trade, 3x leverage cap.

## Source

Classic rectangle consolidation breakout — Edwards & Magee,
*Technical Analysis of Stock Trends*; summary at
https://www.investopedia.com/terms/r/rectangle.asp

## Honest caveats

- The backtest (see BACKTEST.md) loses money overall: breakouts
  on 1h crypto candles fail more often than they follow through,
  and the stop absorbs almost every trade (only 6 of 229 trades
  exited on signal).
- The 4% width and 15-bar hold thresholds are fixed a priori
  from the textbook description, not fitted to this window — but
  they are also arbitrary round numbers, and a different width
  would give a different trade count.
- Range boundaries drift every bar (trailing window), so the
  "opposite boundary" exit is tighter than the textbook's fixed
  rectangle edges; that is a deliberate simplification, and it
  costs trades that would have survived a fixed rectangle.
- Paper/backtest only. Nothing here touches live execution.
