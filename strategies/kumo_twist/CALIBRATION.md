# Ichimoku Kumo Twist — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Tenkan / Kijun / Senkou periods | 9 / 26 / 52 | Spec: standard Ichimoku. |
| Span displacement | None (unshifted, causal) | Spec: spans evaluated from data through bar i, WITHOUT the standard 26-bar forward displacement. |
| Entry / exit | Twist up long, twist down short; exit on opposite twist | Spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 100 | Indicator warmup (52-bar Span B) + margin. |

No spec corrections were needed, but one deliberate construction
choice deserves emphasis (also in the README): textbook Ichimoku
plots Senkou Spans A/B 26 bars ahead, so the cloud visible at bar i
was computed at bar i−26. This strategy uses the spans as known at
bar i, with no displacement — a twist is the CURRENT cloud changing
colour. That is what the brief specified, and it is the only causal
way to trade the twist at bar i: the displaced plot would be a
26-bar-stale signal, and shifting spans forward would be lookahead.
The implementation computes both spans unshifted in `indicators.py`
and never touches the shared helper's shifted Senkou columns;
`test_spans_are_unshifted` proves the stored Span B differs from the
displaced value.

No bug fixes requiring re-runs, no PnL-selected tuning.
