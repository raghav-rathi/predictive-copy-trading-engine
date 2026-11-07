# Bollinger Band Squeeze Breakout

John Bollinger's squeeze breakout: BB(20, 2) with BandWidth (upper − lower) / mid in the lowest 15% of the last 50 bars marking a squeeze; entry only while a squeeze is armed (within 10 bars of a squeeze): close above the upper band goes long, close below the lower band goes short; exit when the close comes back inside the bands.

## Rules

- Squeeze: BandWidth percentile rank within the last 50 bars ≤ 15% (ties ranked lowest, so a dead-flat band counts as squeezed).
- Long: close crosses above the upper band while a squeeze is armed.
- Short: close crosses below the lower band while a squeeze is armed.
- Exit: close back inside the bands (close < upper for longs, close > lower for shorts), plus ATR stop / trail from the batch-standard risk layer.
- Signals use only data through the current bar's close — no lookahead.

## Source

- Bollinger Band squeeze breakout strategy (Traderspy): https://blog.traderspy.app/en/blog/bollinger-band-squeeze-breakout-strategy/

Paper only, no live execution.
