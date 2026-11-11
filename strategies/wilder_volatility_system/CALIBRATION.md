# Wilder Volatility System — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| ATR length | 7 | Wilder's own Volatility System length (New Concepts, 1978). |
| ATR smoothing | Wilder (alpha = 1/7) | The shared `strategies.base.atr` primitive is Wilder smoothing by definition. |
| Long trigger | previous bar's high + ATR(7) | Wilder's rule verbatim; the previous bar's high is the range reference, ATR(7) the expansion. |
| Short trigger | previous bar's low - ATR(7) | Mirror of the long rule. |
| ATR reference bar | Current bar's ATR(7) (through bar i's close) | The trigger is evaluated at bar i's close, so the ATR available then is the current-bar value; using the previous bar's ATR would understate the current bar's own volatility expansion. See deviation note. |
| Exit | Reverse trigger, plus harness stop/trail | Per spec: the system reverses on the opposite trigger, and the shipped system uses the harness 2xATR stop / 2.5xATR trail as the exit mechanism plus the reverse signal. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer (note: the risk layer's ATR(14) is separate from the signal ATR(7)). |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 30 | ATR(7) needs 7 bars of Wilder smoothing; 30 gives margin. |

## Spec deviations

1. **Current-bar ATR(7) in the trigger, not the previous bar's.**
   Wilder's text is usually read as the ATR "of the previous day" in
   daily implementations, but the spec as written ("close > previous
   bar's high + ATR(7)") does not pin the ATR to a bar. The shipped
   version uses the current bar's ATR(7) because the signal is
   evaluated at bar i's close with all data through bar i available;
   it is still fully causal. A previous-bar-ATR variant would fire
   slightly more often (smaller ATR after a calm bar) and was not
   used; the choice was fixed before seeing results.
2. **Harness stop/trail as the practical exit.** Wilder's original
   system exits on the reverse trigger alone. The batch-standard risk
   layer (2xATR stop, 2.5xATR trail, 120-bar max hold) is applied on
   top, per the spec's own instruction, so most trades end on the
   stop/trail rather than the reverse signal.

No bug fixes requiring re-runs, no PnL-selected tuning.
