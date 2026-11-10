# Fisher ACD Opening Range

Mark Fisher's ACD system from *The Logical Trader*: the opening range
(OR) of a session sets the day's tone. A points sit just outside the OR
and are the entries; B points (the OR edges themselves) are the exits;
C points sit further out and mark failed-A reversals. Adapted here to
24/7 crypto on 1h bars, with the UTC day as the session and the first
1h bar of the day (00:00–01:00 UTC) as the opening range.

## Rules

- Opening range = high/low of the first 1h bar of each UTC day; the
  day's OR levels stay fixed for the whole day and recompute at each
  new UTC day.
- A-up = OR high + 0.5 × ATR(14); A-down = OR low − 0.5 × ATR(14).
  C-up = OR high + 1.5 × ATR(14); C-down = OR low − 1.5 × ATR(14).
- Daily pivot = (previous UTC day's high + low + close) / 3.
- Long: close crosses above A-up AND close is above the daily pivot.
  Short: close crosses below A-down AND close is below the daily pivot.
- Exit long on a close below the OR low (B point); exit short on a
  close above the OR high. A close below C-down reverses a long to
  short; a close above C-up reverses a short to long.
- No entries on the first bar of the day (the OR bar itself); signals
  may fire from bar 1 onward.
- Risk layer: 2.0× ATR stop, 2.5× ATR chandelier trail, no target,
  24-bar max hold, 1% risk per trade, 3× leverage cap.
- All computation is causal, so signals on bar i use only data through
  bar i's close. ATR stop / trail from the risk layer also applies.

## Source

- Mark Fisher, *The Logical Trader* (ACD method)
- Investopedia, "The Logical Trader: Understanding ACD": https://www.investopedia.com/articles/technical/04/032404.asp

Paper only, no live execution.
