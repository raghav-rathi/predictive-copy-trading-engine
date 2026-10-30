# Liquidity Sweep — Calibration

All parameters fixed a priori from the sweep definition.
No in-sample sweep, nothing selected on the backtest
window's PnL.

| Parameter | Value | Rationale |
|---|---|---|
| Reference level | min low / max high of the prior 20 bars, excluding the current bar | the spec's "prior 20-bar swing low/high", operationalised as the 20-bar extreme so the level is defined on every bar (a pivot-only level would leave long gaps with no reference) |
| Sweep | wick beyond the level (low < level, or high > level) | the stop-grab itself |
| Reclaim | close back inside the level, on the sweep bar or the next bar | the spec's window; a close that stays beyond is a breakdown, not a sweep, and never fires |
| One fire per sweep | a next-bar reclaim only counts if the sweep bar did not already reclaim | prevents one sweep entering twice |
| Exit | opposite sweep signal | the mirror event invalidates the reversal premise |
| ATR window | 14 | canonical |
| Stop / trail | 2xATR / 2.5xATR | roomy: a sweep's wick extreme is volatile, so the stop sits beyond normal reclaim noise |
| Target | none | the opposite-sweep exit manages the trade |
| Max hold | 120 bars (~5 days) | reversals get a long leash; in practice it never binds (0 max-hold exits) |
| Risk | 1% / trade, 3x leverage cap | house standard |

**Sensitivity note:** the 20-bar window is the main
judgement call — a shorter window would make levels chase
price and fire far more often on noise; a longer window
would make levels stale and sweeps rare. Neither was
tested on PnL. The binding fact is the exit mix: 358 of
516 exits are stops, so the reclaim's follow-through, not
the level definition, is what fails.

**Verdict: loser.** -$4,761 combined over 516 trades
(Sharpe -2.36, negative on all three coins). Do not trade
this as shipped.
