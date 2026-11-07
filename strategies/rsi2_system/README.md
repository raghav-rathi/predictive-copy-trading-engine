# RSI(2) System

Larry Connors' RSI(2) mean reversion (Short Term Trading Strategies That Work, 2008). The idea: in an established trend, a violent 2-bar overstretch against the trend is usually a snap-back setup. The 2-period RSI is extremely sensitive — it only reaches the extremes after sharp, consecutive moves in one direction.

## Rules

- Long: close > SMA(200) AND RSI(2) <= 5.
- Short: close < SMA(200) AND RSI(2) >= 95.
- Exit long: close > SMA(5). Exit short: close < SMA(5). Plus ATR stop / trail. Signals use only data through bar i's close — no lookahead.

## Source

- Larry Connors RSI(2), Short Term Trading Strategies That Work (2008): https://cleartape.ai/strategies/rsi-2-strategy

Paper only, no live execution.
