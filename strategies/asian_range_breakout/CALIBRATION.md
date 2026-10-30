# Asian Range Breakout — Calibration

All parameters fixed a priori from the session-range
definition and the batch spec. No in-sample sweep, nothing
selected on the backtest window's PnL.

| Parameter | Value | Rationale |
|---|---|---|
| Asian session | UTC hours [0, 8) | per the batch spec; the 24/7-crypto adaptation of the FX Asian session |
| Asian range | high/low of that day's Asian bars | the session's consolidation extremes; complete at 08:00 UTC, so use from 08:00 onward is causal |
| Entry window | 1h bars with hour in [8, 16) | after the range completes, before the window ends; a breakout at/after 16:00 is not entered |
| Volume filter | bar volume > prior 20-bar average volume | a breakout needs participation, not a thin drift through the level |
| One entry per day | first qualifying breakout only | per the spec; prevents re-entering the same day's chop after a stop or time exit |
| Time exit | 16:00 UTC bar (signal on the hour >= 16 bar; harness executes at the next open) | end of the breakout window; the trade thesis expires with the window |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2.5xATR | roomy for an intraday expansion move |
| Target | none | the time exit manages the trade |
| Max hold | 24 bars (one day) | backstop for the time exit (e.g. a missing 16:00 bar); in practice it never binds (0 max-hold exits) |
| Risk | 1% / trade, 3x leverage cap | house standard |

**Sensitivity note:** the volume filter and the one-entry-
per-day rule are the main filters — without the volume
filter, thin overnight drifts through the range would
enter; without the one-entry rule, a stopped-out day could
re-enter repeatedly. The time exit dominates the exit mix
(326 of 500), so the strategy's result is mostly "hold the
breakout until 16:00" — and that hold loses on BTC and
HYPE. The 24-bar max hold is a backstop only, not a lever.

**Verdict: loser.** -$1,186 combined over 500 trades
(Sharpe -0.50). Do not trade this as shipped.
