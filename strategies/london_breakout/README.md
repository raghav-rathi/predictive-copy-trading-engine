# London Session Breakout

London session breakout (PatternsWizard exact-rules version,
adapted to fixed UTC hours): take the overnight 00:00–08:00 range
and trade its first break in the 08:00–12:00 window, out by 16:00.

## Rules

- **Range:** highest high / lowest low of the hourly bars
  00:00–08:00 UTC (hours 0–7) of each UTC day.
- **Long entry:** first 08:00–12:00 UTC bar whose close breaks
  above the range high.
- **Short entry:** first 08:00–12:00 UTC bar whose close breaks
  below the range low.
- **Both-sides break:** if the first break bar of the day breaks
  both sides (high above the range high AND low below the range
  low), no entry that day.
- **Long exit:** close below the range low (opposite-side break)
  OR the 16:00 UTC bar (time exit).
- **Short exit:** close above the range high OR the 16:00 UTC bar.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

The range is complete before the 08:00 bar opens, so the entry
signal on a break bar uses only data through that bar's close.
All computation is causal.

## Source

- London breakout strategy (PatternsWizard) — https://patternswizard.com/london-breakout-strategy/

Paper only, no live execution.
