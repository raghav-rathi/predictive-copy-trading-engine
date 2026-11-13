# Volume Spread Analysis

Tom Williams' Volume Spread Analysis (*Master the Markets*),
building on Wyckoff's law of effort vs result: volume is the
effort, the spread and the close are the result. A narrow spread
on low volume after a move means the side that should be pushing
is absent; a wide spread on climactic volume into a close that
fails to hold the extreme means absorption by the other side.

## Rules

- **Long entry:** a NO-SUPPLY bar — down bar (close < prior close)
  with narrow spread (range < 0.5 × ATR(20)) and volume lower than
  each of the previous two bars — or a STOPPING VOLUME bar — down
  bar after a 10-bar decline (close below the close 10 bars ago)
  with volume > 2× the trailing 20-bar mean volume and the close
  in the upper half of its range.
- **Short entry:** a NO-DEMAND bar — the mirror image (up bar,
  narrow spread, volume lower than each of the previous two
  bars) — or an UPTHRUST — a bar that pushes above the prior
  20-bar high then closes in the lower third of its range on
  volume > 1.5× the trailing 20-bar mean volume.
- **Long exit:** the opposite VSA signal (no-demand or upthrust).
- **Short exit:** the opposite VSA signal (no-supply or stopping
  volume).
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies;
  max hold 120 bars.

All computation is causal, so signals on bar i use only data
through bar i's close. Volume is compared only to trailing bars.

## Source

- Tom Williams, *Master the Markets* (Volume Spread Analysis):
  https://www.luxalgo.com/library/concept/no-demand-no-supply-bars/
- VSA background: https://eafxstore.com/blog/volume-spread-analysis/

Paper only, no live execution.
