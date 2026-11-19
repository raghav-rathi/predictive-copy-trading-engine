# Judas Swing

The ICT Judas swing: a session-open fakeout. Price sweeps the Asian
range in the London window, fails to hold outside it, reclaims the
range, and then breaks structure in the reversal direction.

## Rules

- **Asian range:** high/low of the prior evening's bars with UTC
  hour in [20, 24) (the 20:00, 21:00, 22:00 and 23:00 bars).
- **London window:** bars with UTC hour in [7, 10).
- **Long entry (bullish Judas):** within the window a bar's low
  sweeps below the Asian low; a later close gets back above the
  Asian low (reclaim); then a close above the highest high printed
  since the sweep bar (bars after the sweep bar, before the current
  bar) — long on that close.
- **Short entry (bearish Judas):** the mirror — sweep above the
  Asian high, reclaim close back below it, close below the lowest
  low printed since the sweep bar.
- **Entries valid only until 12:00 UTC** (trigger checks require
  hour < 12); one signal per UTC day per side.
- **Long exit:** an opposite bearish-Judas signal OR a close below
  the sweep low (invalidation).
- **Short exit:** an opposite bullish-Judas signal OR a close above
  the sweep high (invalidation).
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 48 bars.
- Warmup 60 bars.

A deeper sweep before any reclaim moves the sweep extreme and
restarts the "since sweep" extreme. All computation is causal, so
signals on bar i use only data through bar i's close.

## Sources

- FundingPips, "Judas Swing":
  https://fundingpips.com/ar/blog/judas-swing-forex

Paper only, no live execution.
