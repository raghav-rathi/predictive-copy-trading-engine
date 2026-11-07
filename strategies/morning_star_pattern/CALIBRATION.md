# Morning/Evening Star — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Candle1 body | >= 0.6x ATR(14) | Spec (long body). |
| Candle2 body | <= 0.3x candle1 body | Spec (small body / doji-like). |
| Candle3 close | Beyond midpoint of candle1's body | Spec (confirmation close). |
| Trend filter | SMA(50): morning star requires close below, evening star above | Spec. |
| Gap requirement | None | Spec: crypto trades 24/7, no gaps. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 100 | Indicator warmup + margin. |

No spec corrections were needed: the pattern rules are implementable
exactly as specified on 24/7 crypto data.

No bug fixes requiring re-runs, no PnL-selected tuning.
