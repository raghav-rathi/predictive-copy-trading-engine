# ICT Power of Three

ICT Power of Three / Accumulation–Manipulation–Distribution (AMD),
Michael J. Huddleston (Inner Circle Trader): the daily template of
how price is delivered — range, sweep the range's liquidity, then
distribute in the opposite direction.

## Rules

Adapted to 24/7 crypto on UTC calendar days (documented adaptation:
crypto has no New York open / London session, so the "day" is the
UTC calendar day and the three phases are fixed UTC hour blocks).

- **Accumulation:** the range (high/low) of the first 8 hours of
  the UTC day (00:00–08:00 UTC).
- **Manipulation:** a sweep of the range low/high by ≥ 0.25 ×
  ATR(14) during 08:00–16:00 UTC. The first sweep of the day wins;
  a same-bar sweep of both sides yields no direction.
- **Distribution:** during 16:00–24:00 UTC, price closes back
  through the range in the opposite direction of the sweep —
  long after a low sweep plus a close back above the range low,
  short after a high sweep plus a close back below the range high.
  Entries are taken on bars with hour 16–22 only (a signal on the
  23:00 bar would execute at the next day's 00:00 open).
- **One trade per day maximum.**
- **Exit:** the 23:00 UTC bar of the day — the position closes at
  the next bar's open, the 00:00 UTC open of the following day
  (end of the UTC day). The harness risk layer's 2xATR stop /
  2.5xATR trail also applies; max hold 120 bars.

Signals are computed on the 1h frame with per-bar day-range columns
carried forward causally: the accumulation range is the expanding
high/low of the day's first-8-hours bars while in that window and
freezes to the completed range from 08:00 onward — no bar ever uses
its own day-end values before they exist.

## Source

- ICT Power of Three / AMD:
  https://velotrade.com/blog/accumulation-manipulation-distribution
- AMD background:
  https://www.dhanith.com/blog/accumulation-manipulation-distribution

Paper only, no live execution.
