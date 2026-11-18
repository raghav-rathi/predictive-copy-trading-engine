# Swing Failure Pattern (SFP)

A failed breakout at a prior swing high/low: the price sweeps
past the level, then closes back inside it — the breakout traders
are trapped and the reversal is traded.

## Rules

- **Long entry:** the low sweeps below the last confirmed swing
  low (as of the previous bar) AND the close is back above that
  same level AND volume spikes (> 1.5x SMA(volume, 20)).
- **Short entry:** the mirror — the high sweeps above the last
  confirmed swing high (as of the previous bar), the close is back
  below it, volume spikes.
- **Long exit:** the close falls back below the swept swing low
  (the level fails again) OR a bearish SFP prints.
- **Short exit:** the close rises back above the swept swing high
  OR a bullish SFP prints.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

Swing pivots are causal 5-bar pivots: a swing high at centre j
iff h[j] is the max of h[j-2..j+2] (strictly greater than both
left neighbours, >= both right neighbours); a swing low iff l[j]
is the min of l[j-2..j+2]. Pivots are recorded at the confirmation
bar (centre+2), never at the centre bar. The swept level is always
read as of the previous bar, so a pivot confirming on the current
bar can never be swept and reclaimed by that same bar. All
computation is causal, so signals on bar i use only data through
bar i's close.

## Sources

- LuxAlgo, "Swing Failure Pattern" —
  https://www.luxalgo.com/library/concept/swing-failure-pattern/
- Thrive.fi, "Swing Failure Patterns" —
  https://thrive.fi/blog/trading/swing-failure-patterns

Paper only, no live execution.
