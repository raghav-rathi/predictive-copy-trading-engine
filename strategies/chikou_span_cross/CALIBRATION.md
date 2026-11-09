# Chikou Span Cross — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Chikou period | 26 bars | Spec (Ichimoku standard). |
| Reference | close 26 bars ago (`close.shift(26)`) | Spec: Chikou span vs the price as of 26 bars ago. |
| Entry / exit | cross above/below the 26-bar-ago close; exit on opposite cross | Spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 50 | Indicator warmup (26-bar lookback) + margin. |

Honest note (also in the README): this is a 26-period momentum
cross, not the full Ichimoku system — no cloud, Tenkan/Kijun, or
confirmation is used. No spec corrections were needed: the cross
rules are implementable exactly as specified on 24/7 crypto data.
One implementation correction worth recording: the shared
`strategies.base.ichimoku` helper computes chikou as
`close.shift(-26)` (plotted forward, uses future data), so it was
NOT used — this module computes the reference with `shift(+26)`,
looking backwards only.

No bug fixes requiring re-runs, no PnL-selected tuning.
