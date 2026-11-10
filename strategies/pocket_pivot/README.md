# Pocket Pivot

Gil Morales & Chris Kacher's pocket pivot ("Trade Like an O'Neil
Disciple", 2010): a volume-footprint early entry inside a base. Instead
of waiting for a breakout above the base, you buy the first up day
whose volume exceeds the largest down-day volume of the previous 10
days — institutional accumulation showing its hand before the breakout.

## Rules

Day-scale rules expressed in 1h bars (1 trading day = 24 bars):

- **Volume test:** an UP bar (close > open) whose volume exceeds the
  largest volume of any DOWN bar (close < open) over the previous 240
  bars (10 trading days), excluding the current bar.
- **Qualifiers (all on the same bar):** close above EMA(240); EMA(240)
  above EMA(1200); EMA(240) rising (above its value 24 bars ago); not
  extended — close < 1.10 × EMA(240).
- **Long entry:** all of the above on the same bar. Long-only.
- **Long exit:** close below EMA(240) (base broken / support lost).
- ATR stop / trail from the risk layer also applies; max hold 240 bars.

All computation is causal, so signals on bar i use only data through
bar i's close.

## Source

- Gil Morales & Chris Kacher, *Trade Like an O'Neil Disciple* (2010)
- LuxAlgo pocket pivot concept: https://www.luxalgo.com/library/concept/pocket-pivot/
- New Trader U, "Ten Rules for Trading Pocket Pivots": https://www.newtraderu.com/2012/08/21/ten-rules-for-trading-pocket-pivots-2/

Paper only, no live execution.
