# Fast Stochastic Crossover

Fast stochastic %K(14)/%D(3) crossover with an SMA(200) trend filter on 1h candles.

## Rules

- %K(14) = 100 × (close − LL14) / (HH14 − LL14); %D = SMA(3) of %K. A zero 14-bar range (HH14 == LL14) maps to %K = 50.
- Long: %K crosses above %D while %K < 20 (oversold cross) and close is above SMA(200) → enter. Exit when %K crosses below %D or %K > 80.
- Short: %K crosses below %D while %K > 80 and close is below SMA(200) → enter. Exit when %K crosses above %D or %K < 20.
- ATR stop / trail from the risk layer also applies.

## Source

- MarketInOut — Stochastic Oscillator: Fast, Slow and Full Explained: https://www.marketinout.com/technical-analysis/stochastic-oscillator

Paper only, no live execution.
