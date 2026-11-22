# LazyBear Squeeze Momentum — Calibration

All parameters were fixed **a priori** from the published
strategy and 1h-bar reasoning — there is no in-sample sweep,
so there is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| Bollinger Bands | 20-period, 2σ, SMA mid | the source's squeeze bands |
| Keltner Channels | 20 EMA mid, 1.5×ATR(14) | the source's channels; ATR(14) matches the house TTM convention |
| Momentum | 20-bar linear-regression fitted value of close minus the high-low/SMA midpoint average | LazyBear's momentum definition, as published |
| Momentum extreme | trailing-100-bar low (long) / high (short) | the source's entry gate: enter the release only when momentum is at a local extreme |
| Trend filter | close above/below EMA(100) | the source's trend gate |
| Confirmation | close above/below the prior close | the source's direction confirmation |
| Exit | first momentum downtick (long) / uptick (short) | the source's exit |
| Stop | 2xATR(14) (added) | the source recommends a stop-loss but specifies none; 2xATR is the house backstop |
| Max hold | 120 bars (~5 days) | a squeeze-release move that has not run in five days is not the trade; the momentum exit normally fires far sooner |
| Risk | 1% / trade, 3x leverage cap | house standard |

## Documented deviations

1. **Position sizing.** The source sizes positions at 8% of
   equity; the harness sizes by 1% equity risk on the stop
   distance (house standard). The signal logic is unaffected.
2. **Stop added.** The source has no specified stop; the
   2xATR(14) stop is an addition, not a source parameter. It
   should rarely bind — the first-downtick exit fires first in
   most trades.
3. **Keltner ATR window.** The source says "1.5×ATR" without
   stating the ATR window; ATR(14) is used, matching the house
   TTM squeeze convention.

No parameter was tuned on the backtest window.
