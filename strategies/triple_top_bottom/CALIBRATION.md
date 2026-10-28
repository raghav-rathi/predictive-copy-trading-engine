# Triple Top / Bottom — Calibration

All parameters fixed a priori from the textbook pattern
description. No in-sample sweep, nothing selected on the backtest
window.

| Parameter | Value | Rationale |
|---|---|---|
| Pivot window | ±2 bars, 2-bar lag | a pivot must be confirmed by bars on both sides; the lag is what makes it causal |
| Tolerance | 1.5% | three "tests of the same level" need a band; 1.5% is tight enough to mean something on 1h crypto |
| Min separation | 5 bars | distinct tests, not one noisy plateau counted three times |
| Max span | 60 bars | a triple forming over longer than ~2.5 days is no longer one pattern |
| Confirmation | close beyond the neckline (lowest intervening low / highest intervening high) | the textbook trigger; unconfirmed patterns never trade |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2.5xATR | roomy for a reversal to develop |
| Target | none | the opposite-pattern exit manages the trade |
| Max hold | 168 bars (~7 days) | a reversal that hasn't reversed in a week was not a reversal |
| Risk | 1% / trade, 3x leverage cap | house standard |

Sensitivity note: the binding constraint is the tolerance band —
widening it manufactures triples out of unrelated highs, and
narrowing it leaves almost no trades. Neither direction has any
evidence of turning this positive on this window.

**Verdict: loser.** -$1,006 combined over 130 trades, negative
on all three coins. Do not trade this as shipped.
