# Cypher Harmonic Pattern

## Mechanism

Scott Carney's Cypher is a 5-point harmonic reversal pattern
(X-A-B-C-D) read off lagged 5-bar swing pivots. A pivot at bar j
is only confirmed at bar j+5, so every signal is strictly causal:
no future bar can change an emitted signal. The five pivots must
span at most 60 bars.

Bullish Cypher (X low, A high, B low, C high, D low):

- AB retraces 38.2–61.8% of XA.
- BC extends 113–141.4% of AB — C pushes past A, the Cypher's
  signature extension (unlike Gartley/Bat, where C stays inside A).
- CD completes at 78.6% retracement of XC — D is a deep pullback
  toward X, and the long entry.
- Each ratio carries a ±8 percentage-point tolerance
  (AB/XA 30.2–69.8%, BC/AB 105–149.4%, CD/XC 70.6–86.6%), plus
  structure checks (X < B < A, C > A, X < D < B).

Bearish Cypher is the exact mirror.

## Entry / exit rules

- **Long entry:** bullish Cypher completion (the bar the D pivot
  confirms); the harness executes at the next bar's open.
- **Short entry:** bearish Cypher completion.
- **Exit:** the opposite pattern's completion, or the 168-bar
  (~7-day) max hold. There is deliberately no pattern-failure
  signal exit — a D that has not turned is left to the 2xATR stop
  / 2.5xATR trail.
- Risk layer: 2xATR hard stop, 2.5xATR chandelier trail, no fixed
  target, 1% equity risk per trade, 3x leverage cap.

## Source

Scott Carney, *Harmonic Trading* — Cypher pattern
(harmonictrading.com).

## Honest caveats

- Completions are rare by design: 8 trades across three coins in
  seven months (see BACKTEST.md). The ratio bands were NOT loosened
  to manufacture trades — the ±8pp tolerance is documented and
  fixed, and the result is reported as-is.
- With 8 trades, no win rate or profit factor means anything.
  The pattern mechanics are unit-tested (bullish and bearish
  completions fire exactly once on crafted paths), but the
  empirical verdict is "inconclusive", not "works".
- Harmonic patterns on 1h crypto pivots are fragile: a 5-bar
  pivot that later gets replaced by a more extreme same-type pivot
  can silently rewrite which 5 pivots form the pattern (history
  already emitted is never rewritten, but future completions
  shift).
