# Market Profile TPO Value-Area Breakout — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Profile window | 168 bars | Spec (matches volume_profile_poc). |
| Bins | 24 across rolling high–low | Spec. |
| TPO assignment | bar midpoint (h+l)/2, one TPO per bar | Spec: price-time, not volume. |
| POC | max-TPO bin midpoint (ties: lowest bin) | Spec. |
| Value area | contiguous bins around POC holding >= 70% of TPOs, grown greedily (heavier neighbour first, ties right) | Spec. |
| Entry / exit | close crosses above VAH / below VAL; exit on opposite VA break | Spec: VA breakout. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 200 | Indicator warmup (168-bar window) + margin. |

No spec corrections were needed: the TPO profile, POC, 70% value
area, VAH/VAL breakout entries and opposite-break exits are all
implementable exactly as specified on 24/7 crypto data (no session
gaps involved; the classic 30-minute TPO letters collapse to one TPO
per 1h bar). Deliberate distinction from `volume_profile_poc`:
this is a TIME profile (one TPO per bar) trading breakouts, while
that is a VOLUME profile trading POC pullbacks — stated in the
README. One empirical note: all 368 backtest exits hit the ATR
stop/trail, so the opposite-break signal exit never fired in the
window; that is a finding, not a reason to change the rule.

No bug fixes requiring re-runs, no PnL-selected tuning.
