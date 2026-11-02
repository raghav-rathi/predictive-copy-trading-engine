# Adaptive RSI

Kaufman's insight was that a moving average should go fast in a trend and slow in chop, with the efficiency ratio deciding the speed. This system applies that idea to RSI itself: RSI(14) is smoothed by a Kaufman AMA driven by ER(10), so the oscillator snaps back quickly from oversold in a real trend but barely moves in sideways noise. Entries are the classic 30/70 recoveries, exits at the 50 midline.

## Mechanism

- ER(10) = |close - close[10]| / sum of |close changes| over 10 bars.
- SC = (ER x (2/3 - 2/31) + 2/31)^2; AMA[i] = AMA[i-1] + SC x (RSI[i] - AMA[i-1]).
- Traded line: the adaptive RSI, not raw RSI(14).

## Entry / exit

- **Long entry:** adaptive RSI crosses above 30.
- **Short entry:** adaptive RSI crosses below 70.
- **Exit:** adaptive RSI crosses 50 against the position. The risk layer adds a 2xATR stop, a 2.5xATR trail, and a 120-bar max hold.

## Source

- Kaufman Adaptive Moving Average (Perry Kaufman):
  https://school.stockcharts.com/doku.php?id=technical_indicators:kaufman_adaptive_moving_average

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, longs and shorts allowed. WARMUP = 30 bars
(14 bars for RSI + 10-bar efficiency ratio + margin.).

## Honest limitation

Adapting the smoothing does not fix RSI's core flaw on trending crypto: in a strong trend the adaptive RSI still pins at the extreme and the 30/70 entries fire against the trend's continuation. The 50 exit also cuts winners early whenever momentum merely pauses (see BACKTEST.md).

Paper only, no live execution.
