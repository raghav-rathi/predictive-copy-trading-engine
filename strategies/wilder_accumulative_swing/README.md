# Wilder Accumulative Swing Index (ASI)

J. Welles Wilder's trend gauge, trend-followed on itself: the ASI
accumulates each bar's swing value, and the trade is the ASI crossing
its own 10-bar EMA — up for long, down for short.

## Mechanism

Per bar i ≥ 1 (C/O = current close/open, Cy/Oy = prior close/open):

- **Numerator:** (C − Cy) + 0.5 × (C − O) + 0.25 × (Cy − Oy)
- **R (exact variant implemented):** R = max(H − Cy, Cy − L, H − L).
  This is the variant specified for this strategy. It differs from
  the candidate list on the BabyPips page (which lists ranges such as
  H − C and L − C); the implemented R is always positive when H > L,
  because H − L is one of the candidates, and it matches the
  TradingKey-style presentation of Wilder's formula that the spec
  follows. When R == 0 (degenerate flat bar, H == L), SI is defined
  as 0.
- **Swing Index:** SI = 50 × numerator / R.
- **ASI:** cumulative sum of SI, with ASI = 0 on bar 0 (SI starts at
  bar 1, since bar 0 has no prior bar).
- **Signal line:** asi_ema = EMA(ASI, 10).

## Entry / exit

- **Long entry:** ASI crosses above asi_ema.
- **Short entry:** ASI crosses below asi_ema.
- **Exit:** the opposite cross. The risk layer adds a 2xATR stop, a
  2.5xATR trail, and a 120-bar max hold.

## Source

- Accumulative Swing Index (ASI), BabyPips Forexpedia (Wilder's ASI,
  SI = 50 × (C − Cy + 0.5 × (C − O) + 0.25 × (Cy − Oy)) / R, ASI =
  cumulative SI — verified by fetching the page):
  https://www.babypips.com/forexpedia/accumulative-swing-index
  The ASI-vs-EMA(10) crossover rule and the exact R variant above are
  this strategy's own construction, documented here rather than
  attributed to the source.

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01% slippage
per side, longs and shorts allowed. WARMUP = 20 bars.

## Honest limitation

The ASI is an unbounded cumulative sum, so its EMA is a lagging
smoother of an already-smoothed trend gauge: crosses fire late, and
in choppy markets the ASI oscillates around its EMA almost every few
bars. The backtest traded 3,299 times across three coins and lost
heavily — see BACKTEST.md. Paper only, no live execution.
