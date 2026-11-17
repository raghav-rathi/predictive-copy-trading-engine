# Volume MA Breakout

Classic volume-confirmed breakout: a new 20-bar extreme only
counts when volume confirms it.

## Rules

- **Long entry:** close makes a new 20-bar high (high >= trailing
  20-bar high, current bar included) AND volume > 1.5x the
  trailing 20-bar mean volume (previous 20 bars, shifted by 1,
  so the current bar's own spike does not dilute the mean).
- **Short entry:** new 20-bar low AND volume > 1.5x the trailing
  20-bar mean volume.
- **Long exit:** close below the trailing 10-bar low (prior 10
  bars, excluding the current bar — the current bar's own low
  can never be above its close, so an inclusive 10-bar low
  could never trigger the exit).
- **Short exit:** close above the trailing 10-bar high (prior 10
  bars).
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

The volume mean uses the previous 20 bars (so the current bar's
own spike does not dilute the comparison); the 20-bar high/low
includes the current bar (a new extreme is only known at the
close). All computation is causal, so signals on bar i use only
data through bar i's close.

## Source

Classic textbook volume-confirmed breakout (Donchian-style range
breakout with a volume filter). No single external source was
specified for this strategy.

Paper only, no live execution.
