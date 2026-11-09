# Ichimoku Tenkan/Kijun Cross — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Tenkan period | 9 | Spec: standard Ichimoku Tenkan-sen. |
| Kijun period | 26 | Spec: standard Ichimoku Kijun-sen. |
| Entry / exit | Cross up long, cross down short; exit on opposite cross | Spec. |
| Filters | None (no cloud / price / Chikou filter) | Spec: cross alone. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 50 | Indicator warmup (26-bar Kijun) + margin. |

No spec corrections were needed: the Tenkan/Kijun cross is
implementable exactly as specified on 24/7 crypto data (no session
gaps involved). The Tenkan/Kijun lines reuse the shared
`strategies.base.ichimoku` helper; only its tenkan/kijun columns are
copied — the helper's displaced Senkou spans and its Chikou span
(shifted −26, i.e. lookahead) are deliberately discarded, so no
future data enters the signal. The distinction from the existing
`kijun_cross` (close vs Kijun, not Tenkan vs Kijun) was verified
against `strategies/kijun_cross/signals.py` and is stated in the
README; a test proves the two strategies disagree on the same frame.

No bug fixes requiring re-runs, no PnL-selected tuning.
