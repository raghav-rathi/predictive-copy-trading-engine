# Ehlers Instantaneous Trendline — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| alpha | 0.07 | Ehlers' published default for the simplified Instantaneous Trendline recursion. |
| Recursion | IT_t = (alpha − alpha²/4)·c_t + 0.5·alpha²·c_{t−1} − (alpha − 0.75·alpha²)·c_{t−2} + 2·(1−alpha)·IT_{t−1} − (1−alpha)²·IT_{t−2} | Ehlers' formula verbatim (as published in the FMZ strategy writeup and the Systematic Algo Trader reproduction of the book's code). |
| Seed | IT_0 = c_0, IT_1 = mean(c_0, c_1) | The spec says "seeded with SMA over the first bars". The shipped seed is the SMA of the closes available so far — causal, no future data. Warmup (60 bars) far exceeds the filter's settling time, so the seed cannot affect traded bars. |
| Input price | Close | The spec's formula is written on c_t. Some platform ports feed the (H+L)/2 midpoint instead; the spec fixes closes, and closes are used. |
| Trigger line | Not used | The common presentation pairs the trendline with a 2-bar projected trigger line (2·IT_t − IT_{t−2}) whose crossings mark trend changes. The spec fixes the plain close/trendline cross, so no trigger line is computed. |
| Cross tolerance | 1e-9 relative (signals.py) | The Ehlers recursion on a perfectly flat series leaves the trendline ~1e-14 above/below the price, which a strict comparison reads as a cross. A cross now requires the close/trendline gap to exceed 1e-9 of the trendline's magnitude (~$0.0001 on a $100k coin). This suppresses only sub-tick float noise; every genuine cross is orders of magnitude larger. |
| Exit | Opposite close/trendline cross, plus harness stop/trail | Per spec: exit on the opposite cross; the batch-standard risk layer (2xATR stop, 2.5xATR trail, 120-bar max hold) is applied on top. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | The recursion is defined from bar 0, but 60 bars lets the filter fully settle from its seed before any signal is traded. |

## Spec deviations

1. **Simplified fixed-alpha recursion, not the adaptive version.**
   Ehlers' full construction measures the dominant cycle with Hilbert
   Transform techniques and resizes the averaging window bar by bar.
   The spec fixes the simplified recursion with alpha = 0.07, which
   is the widely ported form (LazyBear / FMZ / cTrader) and the one
   the book's Chapter 3 trading system uses.
2. **No trigger line.** The common presentation adds a 2-bar
   projected trigger line and trades its crossings with the
   trendline. The spec fixes the close/trendline cross, so the
   trigger line is not computed.
3. **Harness stop/trail as the practical exit.** The batch-standard
   risk layer is applied on top, per the spec's own instruction, so
   most trades end on the stop/trail rather than the opposite cross.

No bug fixes requiring re-runs, no PnL-selected tuning.
