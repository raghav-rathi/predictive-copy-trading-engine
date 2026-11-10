# Volume Zone Oscillator

Walid Khalil & David Steckler's Volume Zone Oscillator (TASC, June 2011):
a bounded volume oscillator. Each bar's volume is signed by the
direction of the close, and the ratio of the EMA(14) of signed volume to
the EMA(14) of total volume, scaled to [−100, +100], measures whether
volume is flowing into up closes or down closes. Extreme readings mark
overbought/oversold volume; reversals from the extremes, traded only
with trend context, are the signal.

## Rules

- Trend context: EMA(60) of close + ADX(14) > 18. Uptrend = close above
  EMA(60); downtrend = close below EMA(60).
- Long (uptrend only): VZO crosses above −40 (oversold reversal), or
  VZO crosses above 0 while the lowest VZO in the last 10 bars stayed
  above −40 (failed pullback that never reached oversold).
- Short (downtrend only): VZO crosses below +40, or VZO crosses below 0
  while the highest VZO in the last 10 bars stayed below +40.
- Exit a long on VZO crossing below 0 or the close crossing below
  EMA(60); exit a short on VZO crossing above 0 or the close crossing
  above EMA(60).
- All computation is causal, so signals on bar i use only data through
  bar i's close. ATR stop / trail from the risk layer also applies.

## Source

- Walid Khalil & David Steckler, "Fine-Tuning Trades with the Volume Zone Oscillator", *Technical Analysis of Stocks & Commodities*, June 2011: https://www.luxalgo.com/library/concept/volume-zone-oscillator/
- Wickra indicator reference: https://docs.wickra.org/Indicators/Indicator-Vzo

Paper only, no live execution.
