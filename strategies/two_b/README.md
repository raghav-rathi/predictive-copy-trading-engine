# Sperandeo 2B Reversal

A failed retest of a 20-bar extreme, per Victor Sperandeo's 2B
pattern: the market makes a new extreme, pulls back, retests the
extreme, and fails — that failure is the entry.

## Rules

- **Short entry:** a new 20-bar high, then a pullback of at least 5
  bars with no new high, then a retest bar that closes above the
  high, then a bar that closes below the retest bar's low.
- **Long entry:** the mirror — new 20-bar low, 5+ bar pullback,
  retest bar closes below the low, then a bar closes above the
  retest bar's high.
- **Long exit:** an opposite 2B-top signal OR a close below the
  20-bar low extreme that armed the long (invalidation).
- **Short exit:** an opposite 2B-bottom signal OR a close above the
  20-bar high extreme that armed the short.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

The 20-bar extreme is the extreme of the previous 20 bars
(excluding the current bar). A fresh 20-bar extreme while a
pattern is armed re-arms the pattern on the new extreme. The
retest must occur within 28 bars of the extreme bar and the
failure within 20 bars of the retest bar, or the pattern expires.
All computation is causal, so signals on bar i use only data
through bar i's close.

## Sources

- RoboForex, "Trading Like Sperandeo: 1-2-3 Reversal and 2B
  Pattern":
  https://roboforex.com/blog/education/trading-like-sperandeo-1-2-3-reversal-and-2b-pattern/
- ThePatternSite, "2B":
  https://thepatternsite.com/2B.html

Paper only, no live execution.
