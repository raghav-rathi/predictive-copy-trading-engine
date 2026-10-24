# ABCD Harmonic Pattern

The ABCD pattern is the simplest harmonic pattern: two legs in the
same direction separated by a retracement, with the second leg
extending the first by a Fibonacci ratio. Traded here on 5-bar
zigzag pivots.

## Pivot construction

A bar is a swing high when its high is the maximum over [j-5,
j+5], a swing low when its low is the minimum over the same
window. A pivot at j therefore CONFIRMS at bar j+5 — the scan only
ever sees pivots with index <= i-5, so no future bar can change an
emitted signal. Consecutive same-type pivots resolve to the most
extreme one, among pivots confirmed so far.

## Pattern rules

Bullish (A high, B low, C lower high, D low) -> LONG at D:

```
A > B, C > B, C < A, D < B
AB = A - B, BC = C - B, CD = C - D
```

Bearish (A low, B high, C higher low, D high) -> SHORT at D:
the mirror image.

Both require all three ratio bands:

```
BC in [38.2%, 88.6%] of AB     (the retracement)
CD in [127.2%, 161.8%] of BC   (the extension)
|CD| within 20% of |AB|        (0.8 <= CD/AB <= 1.2, the symmetry)
```

A pattern fires exactly once, on the bar its D pivot confirms
(bar D+5); the pivot set must change before another can fire.
The harness executes at the next bar's open, so the entry lands
just after D confirms.

## Exits

- Opposite pattern completion (a bearish ABCD while long, or a
  bullish one while short).
- Pattern failure: price moves 50% of the CD leg BEYOND D against
  the position — long: close <= D - 0.5*CD; short: close >=
  D + 0.5*CD. Half a CD leg past D means the D pivot did not hold.
  In practice the harness's 2xATR stop usually fires first; this
  is the signal-level backstop.

## Risk

2xATR stop, 2.5xATR chandelier trail, 96-bar (~4-day) max hold, 1%
risk per trade, 3x leverage cap. WARMUP = 80 bars.

Source: Harmonic Trading (Scott Carney) — ABCD pattern
(https://harmonictrading.com/).
