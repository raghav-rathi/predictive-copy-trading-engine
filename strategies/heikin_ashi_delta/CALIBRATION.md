# Heikin Ashi Delta Momentum — Calibration

## No free parameters — no sweep

The Heikin Ashi delta rule has no tunable lengths: HA_close and
HA_open are fixed formulas, the entry is the delta zero-cross, the
exit is the reverse zero-cross, and the risk layer (2xATR stop,
3xATR trail, 150-bar max hold) was specified in the brief. There is
nothing to sweep without inventing a new rule (e.g. smoothing delta
further, or adding a trend filter) — and inventing one *because* the
backtest is bad would be in-sample rescue, not calibration.

The only choice made here was WARMUP=60. The HA recursion needs no
long spin-up (it is valid from bar 1), so warmup only delays the first
eligible trade; it does not change any signal. No sensitivity run was
needed or run.

## Spec corrections vs the brief

None. The brief was implemented exactly as specified:

- HA_close=(o+h+l+c)/4, HA_open=(prev HA_open+prev HA_close)/2 seeded
  with the first bar's open — as specified.
- Long on a delta cross from negative to positive, with the "delta>0
  after ≥3 bars negative" clause implemented as an OR alongside the
  cross (covers jumps that skip the exact crossing bar) — as specified.
- Exit on delta crossing back through zero; 2xATR stop, 3xATR trail,
  150-bar max hold; warmup 60 — as specified.
- Source URL taken verbatim from a browser search result (BabyPips
  Heikin Ashi lesson), not guessed.
