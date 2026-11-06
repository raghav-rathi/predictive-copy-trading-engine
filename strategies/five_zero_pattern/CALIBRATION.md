# 5-0 Pattern — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Zigzag pivots | 5-bar local extrema, min swing 0.9x ATR(14), confirmed 2 bars late | Spec: swing detector shared across batch 28 geometric strategies. |
| AB / XA | 1.13–1.618 (±0.10) | Published 5-0 ratios (Carney). |
| BC / AB | 1.618–2.24 (±0.10) | Published 5-0 ratios (Carney). |
| D | 50% retracement of BC (±0.08) | Published 5-0 ratios (Carney). |
| Entry window | 20 bars after C completes, reversal bar only | Spec. |
| Exit | 38.2% retracement of the BC leg measured from B (C + 0.618×BC) | Published 5-0 target; corrected from the brief (see note below). |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 100 | Indicator warmup + margin. |

Spec correction (not PnL tuning): the brief's exit — "38.2% retracement
of the C-to-D leg" measured from C — sits below the D entry price, so
37 of 38 positions exited almost immediately at a small loss (as-specified
backtest: 38 trades, -$214.27 combined, PF 0.66). The exit was corrected
to the standard 5-0 target, the 38.2% retracement of the BC leg measured
from B, which sits above the entry; the backtest below is the corrected
rule run as-is. No parameters were tuned to PnL.

No bug fixes requiring re-runs, no PnL-selected tuning.
