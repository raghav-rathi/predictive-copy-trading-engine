# Swing High Low Breakout

Swing-structure breakout on 5-bar pivots: trade the break of
market structure, confirmed by the direction of the swing
sequence.

## Rules

- **Swing high:** a high strictly greater than the 2 bars on
  each side. **Swing low:** a low strictly lower than the 2 bars
  on each side. A pivot is only known once the 2 bars to its
  right have closed, so it is recorded at its confirmation bar
  (centre + 2).
- **Long entry:** close breaks above the last swing high AND the
  last two swing lows are ascending (the most recent swing low
  is higher than the one before it — a higher low has formed).
- **Short entry:** close breaks below the last swing low AND the
  last two swing highs are descending (a lower high has formed).
- **Long exit:** close breaks below the last swing low.
- **Short exit:** close breaks above the last swing high.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

This is a pure structure breakout: the entry fires on the break
itself, not on a pullback to the broken level. Pullback entries
after a structure break belong to the support_resistance_flip
strategy, which waits for the retest and the hold.

All computation is causal, so signals on bar i use only data
through bar i's close.

## Source

Swing-structure / market-structure breakout on 5-bar pivots
(classic market-structure concept). No single external source
was specified for this strategy.

Paper only, no live execution.
