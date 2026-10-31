# Woodie Pivots

Woodie daily pivot points traded as 1h breakout levels: the prior
completed UTC day's range sets today's support/resistance grid,
and closes crossing the outer levels trigger entries.

## Mechanism

For each completed UTC day, H = max high, L = min low, C = last
close. Levels for the current day come from the PRIOR day only:

- PP = (H + L + 2 × C) / 4 — the close gets double weight, unlike
  the classic (H + L + C) / 3 pivot
- R1 = 2 × PP − L
- S1 = 2 × PP − H
- R2 = PP + (H − L)
- S2 = PP − (H − L)

Levels are constant across the current day's bars and are fixed
before that day's first bar, so there is no lookahead. The first
day has no levels and no signals.

## Entry / exit

- **Long entry:** close crosses above prior-day R1.
- **Short entry:** close crosses below prior-day S1.
- **Long exit:** close crosses below prior-day PP.
- **Short exit:** close crosses above prior-day PP.
- The risk layer adds a 2xATR stop, a 2.5xATR trail, and a
  120-bar max hold. R2/S2 are computed and reported as levels but
  are not entry triggers in this version.

## Source

- Woodie pivot point formulas (PP, R1, S1, R2, S2 as above):
  https://www.dumblittleman.com/pivot-points/
  (verified; the breakout/exit rule set is this strategy's own
  construction, not the source's.)

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, longs and shorts allowed. WARMUP = 50 bars
(two UTC days plus margin).

## Honest limitation

Daily levels are static all day: after a strong overnight gap the
grid can sit far from price for hours, and a level crossed early
in the day may be re-crossed repeatedly as price oscillates
around it. The strategy has no trend filter, so R1/S1 breakouts
against the prevailing trend are taken at full size (see
BACKTEST.md).

Paper only, no live execution.
