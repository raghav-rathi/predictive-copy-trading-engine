# Calibration note

## Parameters: fixed a priori, no in-sample selection

Every parameter is taken straight from Larry Williams' original
specification ("The Ultimate Oscillator", Technical Analysis of
Stocks & Commodities, April 1985) or from the mechanization choices
stated in the task brief. Nothing was fit, swept, or tuned on the
backtest data.

| Parameter | Value | Source |
|---|---|---|
| UO lookbacks | 7 / 14 / 28 | Williams (1985) |
| UO weights | 4 : 2 : 1 | Williams (1985) |
| Oversold / overbought | 30 / 70 | Williams (1985) |
| Pivot left / right bars | 3 / 3 | task brief (confirmation delay) |
| Price reference at pivot | bar low (troughs) / bar high (peaks) | task brief |
| Stop | 1.5 x ATR(14) | task brief |
| Trail | 2.0 x ATR chandelier | task brief |
| Target | none (signal exits) | task brief |
| Max hold | 96 bars (~4 days) | task brief |
| Risk per trade | 1% | task brief |
| Max leverage | 3x | task brief |
| Fees / slippage | 0.00045 / 0.0001 per side | desk standard |
| Warmup | 80 bars | UO(28) spin-up + pivot margin |

No parameter sweep was run. No alternative value was evaluated and
discarded. The backtest below is a single out-of-the-box run of the
as-specified strategy -- there is no in-sample selection to overfit.
