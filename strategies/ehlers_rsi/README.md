# Ehlers RSI

John Ehlers' RSI on SuperSmoother-filtered closes (*Cycle Analytics
for Traders*, 2013): run the classic Wilder RSI on a
SuperSmoother-filtered close series instead of raw closes, so the
oscillator reacts to the cycle rather than to bar-to-bar noise.

## Rules

- **Smoother:** SuperSmoother(10) of closes (2-pole recursion,
  seeded with the price for the first two bars).
- **Oscillator:** Wilder RSI(14) on the smoothed series.
- **Long entry:** RSI crosses above 30 (oversold bounce).
- **Short entry:** RSI crosses below 70 (overbought fade).
- **Long exit:** RSI crosses above 70 (overbought — take the win).
- **Short exit:** RSI crosses below 30 (oversold — cover).
- ATR stop / trail from the risk layer also applies; max hold 120 bars.

All computation is causal, so signals on bar i use only data through
bar i's close. Distinct from `adaptive_rsi`, which is Kaufman-AMA
based.

## Source

- John F. Ehlers, *Cycle Analytics for Traders* (2013)
- Investopedia, "Relative Strength Index (RSI)": https://www.investopedia.com/terms/r/rsi.asp

Paper only, no live execution.
