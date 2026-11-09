# DeMark Range Expansion Index — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| REI summation window | 5 bars | DeMark's canonical window (see correction below). |
| REI momentum lag | 2 bars | Spec: high/low vs two bars earlier. |
| Gate | DeMark A/B overlap conditions | Spec: as published (bars 5–6 / closes 7–8 back). |
| Long level / short level | −60 / +60 | Spec: cross above −60 long, cross below +60 short. |
| Exits | Opposite extreme cross | Spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 50 | Indicator warmup (gate needs 8 bars + 5-bar sums) + margin. |

## Spec correction: the "8-bar window"

The brief described REI as an "8-bar window". The published DeMark
formula uses a **5-bar** summation window (`100 × Sum(Num, 5) /
Sum(Den, 5)` — AmiBroker AFL library, Wickra TD REI docs, and
DeMark's own Stocks & Commodities V15:8 description all agree).
Eight bars is the DATA lookback the gate requires: the B-condition
references closes 7–8 bars back, so REI is only defined once 8 bars
of history exist. This implementation ships the canonical 5-bar sum
with the full gate, and the discrepancy is recorded here rather than
silently shipping an 8-bar sum that no reference documents.

No bug fixes requiring re-runs, no PnL-selected tuning.
