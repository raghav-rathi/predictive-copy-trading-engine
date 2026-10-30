# Money Flow Index — Calibration

All parameters fixed a priori from the Quong/Soudack MFI
definition and the house standard. No in-sample sweep,
nothing selected on the backtest window's PnL.

| Parameter | Value | Rationale |
|---|---|---|
| MFI period | 14 | creators' default, as in the source |
| Oversold / overbought | 20 / 80 | canonical MFI extremes, as in the source |
| Entry | cross BACK above 20 / below 80 | the recovery/fade turn, not the touch into the extreme |
| Exit | 50-midline cross against the position | the neutral line: the reversion has run its course |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2.5xATR | house standard |
| Target | none | the midline cross manages the trade |
| Max hold | 120 bars (~5 days) | house standard; never bound (0 max-hold exits) |
| Risk | 1% / trade, 3x leverage cap | house standard |
| WARMUP | 20 | MFI(14) plus margin |
| Edge cases | all-inflow window → 100; flat window → 50 | avoids divide-by-zero without inventing signal |

Sensitivity note: the midline exit is reached in only 106
of 382 trades; the stop fires first in 276. Tightening the
stop would just pay fees faster, and loosening it or moving
the 20/80 levels on this window's numbers would be post-hoc
tuning, so neither is adopted. The honest read is that
MFI mean reversion has no edge on 1h crypto here.

**Verdict: loser.** −$3,626 combined over 382 trades
(PF 0.77–0.80 per coin). Do not trade this as shipped.
