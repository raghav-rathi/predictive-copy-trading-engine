# MACD Histogram — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Fast / slow / signal EMAs | 12 / 26 / 9 | Appel's published defaults, the near-universal standard. |
| Histogram | MACD line − signal line | Aspray's definition; a histogram zero cross is exactly a MACD/signal cross. |
| EMA seeding | pandas ewm (adjust=False), seeded at the first close | The shared `strategies.base.macd` primitive; the standard EMA recursion, no warm-up seeding choice was made here. |
| Exit | Opposite histogram zero cross, plus harness stop/trail | Per spec: exit on the opposite cross; the batch-standard risk layer (2xATR stop, 2.5xATR trail, 120-bar max hold) is applied on top. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 40 | The histogram is NaN until the signal EMA has 9 valid MACD values (bar ~34); 40 gives margin. |

## Spec deviations

1. **Histogram zero cross, not MACD-line zero cross.** The spec
   fixes the histogram (MACD − signal) crossing zero, which is the
   signal-line cross, not the MACD line crossing zero (the 12/26 EMA
   cross). The two are different events: the histogram cross fires
   earlier. This is the spec as written.
2. **Harness stop/trail as the practical exit.** The batch-standard
   risk layer is applied on top, per the spec's own instruction, so
   most trades end on the stop/trail rather than the opposite cross.

No bug fixes requiring re-runs, no PnL-selected tuning.
