# Sperandeo 2B Reversal — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Extreme lookback | 20 bars | The spec's 2B lookback. |
| Pullback minimum | 5 bars elapsed since the extreme bar | The spec's "pullback of 5–8 bars", counted as bars elapsed (the retest bar is the first bar after the 5-bar pullback; see decision 1). |
| Retest window | 28 bars from the extreme bar | 8-bar max pullback + 20 bars to retest (see decision 2). |
| Failure window | 20 bars from the retest bar | The spec's "retest must occur within 20 bars" applied symmetrically to the failure leg; a stale retest is not traded. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | 20-bar lookback + pullback/retest/failure legs need ~50 bars to seed; 60 gives margin. |

## Spec decisions / ambiguities

1. **Pullback counting.** The spec says "a pullback of 5–8 bars".
   Shipped reading: the pullback is the bars elapsed since the
   extreme bar; the pattern arms once 5 bars have elapsed, and the
   retest bar is the first bar after that whose close exceeds the
   extreme (earliest retest at extreme+6). A bar that closes beyond
   the extreme *before* the 5 bars elapse is itself a fresh 20-bar
   high (its high exceeds the extreme, which is inside the trailing
   20-bar window), so it re-arms the pattern rather than counting
   as a retest — the two readings coincide.
2. **Retest deadline.** The spec says "the retest must occur within
   20 bars after the pullback ends". The pullback "ends" anywhere
   in the 5–8 bar range, so the deadline from the extreme bar is
   5+20=25 to 8+20=28 bars; the shipped 28 uses the loosest end
   (max pullback + 20). A tighter 25-bar deadline would trade
   strictly fewer patterns.
3. **The retest bar is checked before a re-arm.** A retest bar's
   high necessarily exceeds the old extreme, so a naive
   new-high check would re-arm and swallow the retest. The state
   machine checks "close beyond the extreme" first while armed,
   so the retest is recorded and only a *later* fresh extreme
   re-arms.
4. **"Breakdown bar" naming.** The ForexFactory writeup calls the
   bar that closes beyond the extreme the "breakdown bar"; the
   shipped code calls it the retest bar (same bar).
5. **Exits use the arming extreme.** "Close below the new 20-bar
   low extreme that armed the trade" is implemented as the most
   recent arming extreme (`last_bottom_extreme` /
   `last_top_extreme`, forward-filled). If a newer pattern arms
   while a trade is open, the level updates to the newer extreme.
6. **Harness stop/trail as an additional exit.** The spec's exits
   are the opposite-2B signal / invalidation close; the
   batch-standard risk layer (2xATR stop, 2.5xATR trail, 120-bar
   max hold) is applied on top, per the batch instruction.

## What the exits actually did

Shipped run (39 trades): 36 trades ended on the harness
stop/trail and 3 on a signal exit (one per coin). The
invalidation / opposite-signal exit almost never fires before
the 2xATR stop does — once a failed retest is entered, price
usually runs straight into the stop rather than printing the
opposite 2B pattern or closing back through the arming extreme.

No bug fixes requiring re-runs, no PnL-selected tuning.
