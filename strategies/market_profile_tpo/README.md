# Market Profile TPO Value-Area Breakout

Rolling 168-bar TPO (time-price opportunity) market profile, in the
Steidlmayer / CBOT Market Profile tradition: price is organised by
how much TIME the market spent at each level, not by volume. The
window's range (min low → max high) is split into 24 equal bins and
each bar contributes exactly one TPO to the bin containing its
midpoint ((h + l) / 2). POC is the midpoint of the bin with the most
TPOs; the value area is the smallest contiguous set of bins around
the POC bin holding at least 70% of the window's TPOs (grown
greedily outward, heavier neighbouring bin first, ties go right).
VAH / VAL are the upper / lower edges of that bin set.

## Rules

- Long: close crosses above VAH. Exit on a close breaking below VAL (opposite value-area break).
- Short: close crosses below VAL. Exit on a close breaking above VAH.
- This is a value-area BREAKOUT: price is expected to run once value is accepted outside the 70% TPO band. ATR stop / trail from the risk layer also applies.

## Distinction from volume_profile_poc

The existing `volume_profile_poc` strategy is a VOLUME profile: each
bar's volume is assigned to the bin containing its close, and it
trades POC PULLBACKS (fade back to POC, exit at VAH/VAL). This
strategy is a TIME profile: each bar counts once regardless of
volume, and it trades value-area BREAKOUTS (enter on a close outside
VAH/VAL, exit only on the opposite break). Same window (168 bars),
same bin count (24), same 70% value-area fraction — different
weighting (time vs volume) and opposite trade direction (breakout vs
pullback).

## Source

- Wikipedia — Market profile (Steidlmayer, CBOT): https://en.wikipedia.org/wiki/Market_profile

Paper only, no live execution.
