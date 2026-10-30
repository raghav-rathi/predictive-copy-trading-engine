# Structure Break (BOS)

## Mechanism

Market structure is the sequence of swing highs and lows: an
uptrend prints higher highs and higher lows, a downtrend the
mirror. A Break of Structure (BOS) is a candle *close* beyond
the most recent swing level in the direction of the trend —
confirmation the trend is continuing. A break against the
trend (a Change of Character, CHoCH) is the early warning
the trend may be ending, and is used here as the exit.

- **Swing pivots:** a 5-bar pivot high is the maximum of the
  5 bars centred on it; a pivot low is the mirror minimum.
  Pivots are only confirmed after the 2 bars to their right
  have closed, so no unconfirmed pivot can ever trigger a
  signal.
- **Long entry:** a close above the prior confirmed swing
  high, while the last structure break was also upward — a
  BOS continuation, i.e. a second consecutive upward break
  printing a higher high. The first break in a new direction
  only sets the trend state; it does not enter.
- **Short entry:** mirror (close below the prior swing low,
  last break also downward).
- **Exit:** the opposite structure break — a close below the
  most recent swing low while long, or above the most recent
  swing high while short. Wicks do not count: only closes
  break structure.

## Entry / exit rules

- Long entry: BOS-continuation up while flat.
- Short entry: BOS-continuation down while flat.
- Long exit: a downward structure break while long. Short
  exit mirrors.
- Risk layer: 2xATR stop, 2.5xATR trailing stop, 120-bar max
  hold, 1% risk per trade, 3x leverage cap.

## Source

Break of Structure (BOS) vs CHoCH Explained (Velotrade)
https://velotrade.com/blog/break-of-structure

## Honest caveats

- The backtest (see BACKTEST.md) is essentially flat (+$283
  over 433 trades, combined Sharpe 0.18) — noise on $30k of
  starting capital, carried entirely by HYPE while BTC and
  ETH both lose. Not a demonstrated edge.
- 351 of 433 exits are stops, not signal exits: the stop,
  not the structure exit, manages most trades.
- Paper/backtest only. Nothing here touches live execution.
