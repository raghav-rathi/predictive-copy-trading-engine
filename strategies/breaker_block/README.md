# Breaker Block

ICT Smart Money Concepts breaker block (Michael J. Huddleston,
Inner Circle Trader): a failed order block that flips polarity
and becomes a reversal zone traded from the opposite side.

## Rules

- **Order block:** the last down-closed bar before an impulsive
  close above the prior 20-bar high is the bullish order block
  (zone = that bar's [low, high]); the last up-closed bar before
  a close below the prior 20-bar low is the bearish order block.
  Only the most recent order block per direction is kept; a newer
  one replaces the older one.
- **Breaker formation:** price returns to the block and closes
  through it — below the low for a bullish block, above the high
  for a bearish block. A failed bullish block becomes a BEARISH
  breaker; a failed bearish block becomes a BULLISH breaker.
- **Short entry:** on a bearish breaker, after a retest bar (a bar
  that closes back at/into the zone from below), the first bar
  that closes back below the zone low.
- **Long entry:** on a bullish breaker, after a retest bar (a bar
  that closes back at/into the zone from above), the first bar
  that closes back above the zone high.
- **Breaker lifetime:** only the most recent unmitigated breaker
  per direction is active; a breaker expires 200 bars after the
  break-through bar, is consumed once traded, and is invalidated
  if price closes back through the far side of the zone (above
  the high for a bearish breaker, below the low for a bullish
  breaker).
- **Long exit:** the opposite (bearish-breaker) entry signal.
- **Short exit:** the opposite (bullish-breaker) entry signal.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies;
  max hold 120 bars.

All computation is causal, so signals on bar i use only data
through bar i's close. Only body closes (not wicks) form, break,
and retest blocks.

## Source

- ICT Smart Money Concepts (Michael J. Huddleston):
  https://www.fundedenigma.com/education/ict-concepts-decoded/power-of-three
- Breaker-block reference (SMC: order blocks, breaker blocks):
  https://tradingwyckoff.com/en/smart-money-concepts/

Paper only, no live execution.
