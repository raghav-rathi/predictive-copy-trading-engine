# Stochastic Divergence

George Lane slow stochastic (%K(14,3), %D(3)) regular and hidden divergence on 5-bar swing pivots: regular divergence signals a reversal, hidden divergence signals trend continuation.

## Rules

- Swing pivots: a bar high/low that is the extreme of the centered 5-bar window; a pivot is only usable once confirmed 2 bars later, and signals are emitted on the confirmation bar (pivot + 2).
- Regular bullish: price lower low at pivot2 vs pivot1 (within 40 bars) AND %K higher low → long entry. Regular bearish is the mirror image → short entry.
- Hidden bullish (uptrend, close > SMA(50)): price higher low AND %K lower low → long entry. Hidden bearish (close < SMA(50)) is the mirror image → short entry.
- Exit long: %K crosses above 80; exit short: %K crosses below 20.
- At most one entry per divergence pair.

## Source

- George Lane stochastic + regular/hidden divergence: https://cryptensive.com/blog/trading-divergences-regular-and-hidden/

Paper only, no live execution.
