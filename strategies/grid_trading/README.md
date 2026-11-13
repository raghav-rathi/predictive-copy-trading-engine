# Grid Trading

Classic grid trading (range system): split a price range into equal
levels and buy low / sell high inside the range, profiting from
oscillation rather than direction.

## Rules

- Grid = trailing 200-bar high/low range, split into 10 equal levels
  (step = range / 10). Recomputed causally each bar.
- **Long entry:** close falls into the BOTTOM 20% of the grid range
  (grid_pos <= 0.20) — buy the dip of the range.
- **Long exit:** close reaches the range midpoint.
- **Short entry:** close rises into the TOP 20% of the grid range
  (grid_pos >= 0.80) — sell the top of the range.
- **Short exit:** close falls back to the range midpoint.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 250 bars (200-bar grid + margin).

## Single-position approximation

A real grid holds many small orders, one per level. The batch
backtest harness holds one position at a time, so this is a
single-position approximation, documented here and in
CALIBRATION.md: the entry is a level condition (not a one-bar cross),
so while price sits in a grid edge zone the signal stays on and the
harness re-enters after a stop/trail exit; each round trip is
bottom-zone -> midpoint (long) or top-zone -> midpoint (short),
i.e. roughly two grid levels of range travel per trade, not the
per-level scalps of a true grid.

All computation is causal, so signals on bar i use only data through
bar i's close.

## Source

- Grid trading, Investopedia:
  https://www.investopedia.com/terms/g/grid-trading.asp

Paper only, no live execution.
