# Andrews Pitchfork — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Fractal pivots | 5-bar local extrema, min swing 0.9x ATR(14), confirmed 2 bars late | Spec: swing detector shared across batch 29 geometric strategies. |
| Fork triple | Most recent alternating L/H/L with P2 > P0 (bullish), H/L/H with P2 < P0 (bearish) | Spec (Andrews). |
| Median line | P0 through the midpoint of P1–P2, extended forward in bar-index space | Spec (Andrews). |
| Parallels | Through P1 and P2, same slope as the median line | Spec (Andrews). |
| Touch band | 0.25x ATR(14) | Spec. |
| Entry | Low within the band of the lower parallel + close back above it (long); mirror for shorts | Spec. |
| Exit | Close reaching the median line (target), or close beyond the opposite parallel | Spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 100 | Indicator warmup + margin. |

Spec-interpretation decisions (not PnL tuning):

- Bullish and bearish forks are tracked independently with separate
  line columns, so a bearish fork forming while a bullish one is
  active cannot overwrite the bullish fork's lines (and vice versa).
- A bounce counts once: consecutive bars meeting the same bounce
  condition do not re-fire an entry, so one touch is one signal.
- The median-line target is evaluated against the currently active
  fork each bar, per the spec's "recompute whenever a newer completed
  pivot triple forms".

No bug fixes requiring re-runs, no PnL-selected tuning.
