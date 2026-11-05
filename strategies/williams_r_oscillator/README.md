# Williams %R Oscillator

Williams %R(14) (Larry Williams, 1973) oversold/overbought exits with an SMA(50) trend filter: long when %R crosses back above -80 after being below -80 while close is above SMA(50); short when %R crosses back below -20 after being above -20 while close is below SMA(50); exit long when %R crosses above -20, exit short when %R crosses below -80. %R(14) = (HighestHigh14 - Close) / (HighestHigh14 - LowestLow14) * -100.

## Rules

- Long: %R crosses back above -80 and close > SMA(50).
- Short: %R crosses back below -20 and close < SMA(50).
- Exit long: %R crosses above -20.
- Exit short: %R crosses below -80.
- Plus ATR stop / trail from the batch-standard risk layer.

## Source

- Williams %R indicator: https://blog.ueex.com/williams-r-indicator/

Paper only, no live execution.
