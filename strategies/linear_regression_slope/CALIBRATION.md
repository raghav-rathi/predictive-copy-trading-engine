# Linear Regression Slope — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| LinReg window | 20 bars | Spec: LinReg(20). |
| Normalized slope | slope / close | Spec; makes the slope comparable across coins. |
| Entry R² threshold | ≥ 0.5, at the turn bar | Spec. |
| Exit R² threshold | < 0.3 | Spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 50 | Indicator warmup + margin. |

Spec correction needed (no change made — shipped as briefed): the
entry rule as specified is structurally near-impossible to satisfy.
Requiring R² ≥ 0.5 on the exact bar the slope flips sign fails
because a 20-bar window straddling a reversal has a poor linear fit
by construction (BTC: 311 slope turns, max R² at any turn 0.265,
mean 0.029; R² ≥ 0.5 occurs 42% of the time overall but essentially
never at a turn). A workable variant would check R² a few bars after
the turn, or require R² ≥ 0.5 on the bar *before* the turn — but
either change would be a different rule, so it was not implemented
and no re-run was done. The zero-trade outcome is the honest result
of the briefed rule.

One implementation bug was found and fixed during testing (before any
backtest): the first SS_tot computation paired each bar with its own
trailing mean instead of the window mean, understating R² (a perfect
line scored R² = 0.37). Fixed to SS_tot = Σy² − n·ȳ² and verified
against `numpy.polyfit` slope and `numpy.corrcoef` R². No backtest
numbers were produced before the fix.

No PnL-selected tuning.
