# Aroon Oscillator

Chande's Aroon oscillator compresses the two Aroon lines into one: Aroon-Up minus Aroon-Down over 25 bars. A fresh high pushes it toward +100, a fresh low toward -100, and a market making neither pushes it toward 0. Trading the zero cross trades the trend change itself, not the level.

## Mechanism

- Aroon-Up(25) = 100 x (25 - bars since the 25-bar high) / 25; Aroon-Down is the mirror on lows.
- Oscillator = Aroon-Up - Aroon-Down, in [-100, +100].
- Zero is the regime line: above it the recent high is fresher than the recent low.

## Entry / exit

- **Long entry:** oscillator crosses above 0.
- **Short entry:** oscillator crosses below 0.
- **Exit:** the opposite zero cross. The risk layer adds a 2xATR stop, a 2.5xATR trail, and a 120-bar max hold.

## Source

- Aroon Oscillator (Tushar Chande):
  https://school.stockcharts.com/doku.php?id=technical_indicators:aroon_oscillator

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, longs and shorts allowed. WARMUP = 39 bars
(25 bars for Aroon + ATR/margin.).

## Honest limitation

The zero cross fires on any fresh extreme, so a choppy tape that alternates fresh highs and lows whipsaws it constantly. The oscillator also says nothing about how far a trend runs — the trail and max hold do that work, and on 1h bars they often give back most of the move (see BACKTEST.md).

Paper only, no live execution.
