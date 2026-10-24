# ABCD Pattern — Calibration

All parameters were fixed **a priori** from the published ABCD
specification and 1h-bar reasoning — there is no in-sample sweep,
so there is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| Zigzag confirmation | 5 bars each side | the house zigzag standard; a pivot must survive 5 bars of follow-through to count as structure |
| BC retracement band | 38.2%–88.6% of AB | the classical ABCD retracement band (0.382 / 0.886 Fibonacci ratios) |
| CD extension band | 127.2%–161.8% of BC | the classical ABCD extension band (1.272 / 1.618 Fibonacci ratios) |
| CD/AB symmetry band | 0.8–1.2 | the AB=CD symmetry condition, relaxed to +-20% so real pivots qualify |
| CD failure exit | 50% of CD past D | half a leg beyond D is a failed pivot; tighter would stop out on wicks, looser would let failures run |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2.5xATR | roomy enough for a reversal to develop; the trail rides the leg back toward C/A |
| Max hold | 96 bars (~4 days) | a D pivot that hasn't turned in four days was not a turn |
| Risk | 1% / trade, 3x leverage cap | house standard |

The design bet is that strict-ratio ABCD completions mark
exhaustion turns. The backtest (BACKTEST.md) cannot confirm or
refute that bet: the bands are so tight that only 33 completions
fire across three coins in seven months.

No optimization was performed, and the window in BACKTEST.md must
not be used to tune any of these numbers — widening the bands
until the sample looks good would be pure overfitting.
