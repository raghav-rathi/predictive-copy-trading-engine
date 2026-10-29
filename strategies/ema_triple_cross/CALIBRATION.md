# EMA Triple Cross — Calibration

All parameters fixed a priori from the textbook triple-MA
setup. No in-sample sweep, nothing selected on the backtest
window.

| Parameter | Value | Rationale |
|---|---|---|
| EMA periods | 3 / 8 / 21 | short stack that reacts within a day on 1h bars while the 21-bar leg anchors the trend |
| Entry | stack direction while flat | trade only with the stack; no counter-trend entries |
| Exit | unstacking | the stack breaking is the trend failing, by definition |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 3xATR | roomy for a trend leg to develop |
| Target | none | the unstack exit manages the trade |
| Max hold | 336 bars (~14 days) | a trend leg that hasn't paid in two weeks is not a trend leg |
| Risk | 1% / trade, 3x leverage cap | house standard |

Sensitivity note: the exit is the weak link — exiting on ANY
unstacking turns EMA noise into 971 signal exits over 1,451
trades. Requiring the stack to break for 2–3 consecutive bars
before exiting, or requiring a fast/mid cross rather than any
unstack, would cut churn sharply, but neither was tested here
and neither must be fitted to this window.

**Verdict: loser.** -$11,917 combined over 1,451 trades,
negative on every coin. Do not trade this as shipped.
