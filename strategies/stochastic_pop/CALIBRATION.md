# Stochastic Pop — Calibration

All parameters fixed a priori from Raschke's Street Smarts
setup and the standard fast-stochastic construction. No
in-sample sweep, nothing selected on the backtest window.

| Parameter | Value | Rationale |
|---|---|---|
| fast %K period | 14 | Raschke's fast stochastic; the slow variant belongs to stoch_hook |
| Extreme zones | 80 / 20 | canonical stochastic overbought/oversold |
| Breakout range | prior 20 bars, today excluded | a genuine new 20-bar high/low, not today's own high restated |
| Same-bar rule | %K cross AND breakout on the same bar | the pop is the coincidence of momentum extreme and breakout; either alone is a different setup |
| ATR window | 14 | canonical |
| Stop / trail / target | 1.5xATR / 2xATR / 3xATR | tight stop (pops fail fast), 2:1 target-to-stop |
| Max hold | 72 bars (~3 days) | a pop that has not extended in three days was not a pop |
| Risk | 1% / trade, 3x leverage cap | house standard |

Sensitivity note: the same-bar coincidence rule is the
binding constraint — relaxing it to "breakout within 3 bars
of the %K cross" would add trades but would also admit
ordinary breakouts that merely follow an extreme print, which
is a different (and weaker) thesis. It was not tested here
and must not be fitted to this window.

**Verdict: loser.** -$2,189 combined over 373 trades; only
ETH is green (+$132, PF 1.03) and it does not cover BTC's
-$1,396 or HYPE's -$924. Do not trade this as shipped.
