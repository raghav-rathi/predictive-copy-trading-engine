# EMA Ribbon

EMA ribbon (8, 13, 21, 34, 55): trade the moment the ribbon snaps into full alignment, with the spread confirming expansion. Ribbon spread = (ema8 − ema55)/ema55.

## Rules

- Full bullish alignment: ema8 > ema13 > ema21 > ema34 > ema55. Long on the bar the alignment FIRST becomes fully bullish (not aligned on the previous bar) AND close > ema8 AND ribbon spread > 0.002.
- Full bearish alignment: ema8 < ema13 < ema21 < ema34 < ema55. Short on the bar the alignment FIRST becomes fully bearish AND close < ema8 AND spread < −0.002.
- Exit a long when alignment breaks (ema8 < ema21) or close < ema34. Exit a short on the mirror (ema8 > ema21 or close > ema34).
- All EMAs are causal, so signals on bar i use only data through bar i's close. ATR stop / trail from the risk layer also applies.

## Source

- AlgoMax — Moving Average Ribbon: Read Trend Strength at a Glance: https://algomax.ai/blog/moving-average-ribbon-strategy-explained

Paper only, no live execution.
