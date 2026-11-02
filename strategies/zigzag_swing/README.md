# ZigZag Swing Breakout

The ZigZag filter strips a chart down to its swings: only moves that retrace 5% from an extreme count as a pivot. This system trades breakouts of those confirmed swings — a close above the last swing high is a long, below the last swing low a short — and, crucially, it never trades the live extreme, only pivots already confirmed by a 5% reversal, so the levels never repaint.

## Mechanism

- Deviation 5%: a swing high confirms when price falls 5% from the running high; a swing low when it rises 5% from the running low.
- Traded levels are the last confirmed swing high/low, held until replaced.
- No level exists before the first confirmed pivot.

## Entry / exit

- **Long entry:** close crosses above the last confirmed swing high.
- **Short entry:** close crosses below the last confirmed swing low.
- **Exit:** the opposite swing level. The risk layer adds a 2xATR stop, a 2.5xATR trail, and a 120-bar max hold.

## Source

- ZigZag swing indicator (classic charting):
  https://school.stockcharts.com/doku.php?id=technical_indicators:zigzag

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, longs and shorts allowed. WARMUP = 30 bars
(5% pivot confirmation + ATR/margin (pivot timing varies).).

## Honest limitation

Confirmation is the cost: by the time a swing high confirms, price has already given back 5%, and the breakout entry then needs a further move past that high — in a 5%-noise crypto market that stack of lags means most breakouts are entered near the local extreme (see BACKTEST.md).

Paper only, no live execution.
