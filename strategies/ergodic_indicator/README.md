# Ergodic Oscillator

William Blau's ergodic oscillator (*Momentum, Direction, and
Divergence*, 1995): one-bar momentum, smoothed twice with EMAs and
normalised by the equally double-smoothed absolute momentum, so the
result is a bounded oscillator in [-100, +100]. It is the same
construction as Blau's True Strength Index — "ergodic" is the label
Blau gave indicators built this way, and the TSI plotted with its
signal line is what most platforms call the Ergodic Oscillator. The
canonical trade is the signal-line cross: long when the ergodic
crosses above its EMA signal line, short on the cross below.

## Rules

- **Long entry:** ergodic crosses above its signal line.
- **Short entry:** ergodic crosses below its signal line.
- **Long exit:** ergodic crosses below its signal line (opposite cross).
- **Short exit:** ergodic crosses above its signal line.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies;
  the shipped system uses the harness stop/trail as the exit mechanism
  plus the opposite cross. Max hold 120 bars.
- This is the raw signal-line cross with no extra filter. The repo's
  `true_strength_index` strategy uses the identical oscillator but
  adds a zero-territory filter to entries (only take a cross up while
  TSI > 0) and a 1.5xATR stop / 2xATR trail; see CALIBRATION.md.

All computation is causal, so signals on bar i use only data through
bar i's close.

## Source

- William Blau, *Momentum, Direction, and Divergence* (Wiley, 1995); TSI first published in *Technical Analysis of Stocks & Commodities*, Nov 1991: https://www.luxalgo.com/library/concept/ergodic-oscillator/

Paper only, no live execution.
