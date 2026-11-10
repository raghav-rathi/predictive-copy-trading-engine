# Weis Wave

David Weis's Weis Wave: volume grouped by price swing instead of per
bar. Each wave runs from one swing extreme to the next, and the wave's
volume is the sum of the bar volumes inside it. A wave carrying much
less volume than the wave before it shows effort drying up; a wave
carrying much more shows effort. (David Weis, *Trades About to
Happen*, Wiley 2013.)

## Rules

- A swing ends when the close reverses at least 1.5x ATR(14) from the
  running swing extreme (max high in an up-wave, min low in a
  down-wave). The reversal bar starts the new wave; the completed
  wave's volume runs through the bar before it.
- Long: a new up-wave starts AND the just-completed down-wave's volume
  was less than 85% of the completed up-wave before it. Exit when a
  new down-wave starts.
- Short: mirror — a new down-wave starts AND the just-completed
  up-wave's volume was less than 85% of the completed down-wave before
  it. Exit when a new up-wave starts.
- All computation is causal, so signals on bar i use only data through
  bar i's close. ATR stop / trail from the risk layer also applies.

## Source

- David Weis, *Trades About to Happen: A Modern Adaptation of the
  Wyckoff Method* (Wiley, 2013)
- Weis Wave indicator overview: https://forexcalculator.pro/weis-wave-volume-indicator-mt5/
- Weis Wave / neoclassical trend-swing indicator reference: https://easycators.com/thinkscript/weis-wave-ord-volume-and-neoclassical-trend-swing-indicator/

Paper only, no live execution.
