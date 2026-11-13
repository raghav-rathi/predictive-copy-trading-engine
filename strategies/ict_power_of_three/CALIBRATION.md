# ICT Power of Three — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Session | UTC calendar day | Per spec: crypto has no NY sessions, so the day is the UTC calendar day. This is the adaptation under test (see verdict in BACKTEST.md). |
| Accumulation window | First 8 hours, 00:00–08:00 UTC | Per spec. |
| Manipulation window | 08:00–16:00 UTC | Per spec. |
| Sweep threshold | ≥ 0.25 × ATR(14) beyond the range extreme | Per spec. ATR(14) is the batch-standard volatility read. |
| Distribution window | 16:00–24:00 UTC; entries on bars with hour 16–22 only | Per spec, with the 23:00 bar reserved as exit-only: a signal on the 23:00 bar would execute at the next day's 00:00 open, outside the distribution day. |
| Reclaim | Close back above the range low (after a low sweep) / below the range high (after a high sweep) | Per spec: "closing back through the range in the opposite direction of the sweep". The swept level itself is the reclaim line. |
| First sweep wins | If both sides sweep in a day, the earlier sweep sets the direction; a same-bar tie yields no direction | Not in the spec text; a day cannot distribute both ways, so the first sweep in time is the manipulation. A same-bar two-sided sweep has no identifiable first sweep. |
| One trade per day | Max one entry per UTC day per coin | Per spec. |
| Exit | 23:00 UTC bar (executes at the next day's 00:00 open) | Per spec: "exit at the end of the UTC day". |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 1200 | Per spec: ~50 days of daily context (50 × 24 = 1200 bars). |

## Spec deviations

1. **UTC-day adaptation** (see table): the original ICT AMD is
   anchored to trading sessions (Asian accumulation, London
   manipulation, New York distribution). Crypto trades 24/7, so
   the shipped version fixes the three phases to UTC hour blocks.
   The backtest is a verdict on this adaptation.
2. **Entries restricted to hours 16–22** (see table): the 23:00
   bar is exit-only, so a reclaim signal there cannot execute
   inside the distribution day.
3. **First-sweep-wins rule** (see table): added where the spec is
   silent on two-sided sweep days.
4. **Harness stop/trail as an additional exit.** The spec exits at
   the end of the UTC day. The batch-standard risk layer (2xATR
   stop, 2.5xATR trail, 120-bar max hold) is applied on top, per
   the spec's own instruction, so 94 of 299 trades end on the
   stop/trail rather than the day-end signal.

No bug fixes requiring re-runs, no PnL-selected tuning.
