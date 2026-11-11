# Donchian ADX — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Donchian length | 20 bars | Same entry as `donchian_channel`; the classic 4-week (20-day) Donchian length, expressed in 1h bars. |
| Breakout reference | Prior bar's channel (shift 1) | A close can never exceed its own bar's channel; the prior bar's values are the tradeable breakout level. |
| ADX length | 14 | Wilder's standard ADX length. |
| ADX entry threshold | > 25 | Wilder's conventional "trend present" threshold; breakouts only count while a trend is measurably in force. |
| ADX exit threshold | < 20 | Hysteresis below the entry level: trend strength decaying under 20 exits even without a reversal, avoiding whipsaw around a single 25 line. |
| Exit | ADX < 20 OR opposite breakout | Per spec; the opposite breakout is the reversal exit, the ADX decay is the trend-death exit. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | Donchian needs 20 bars; ADX needs 14 bars of Wilder smoothing plus time for the smoothed DX to stabilise; 60 gives margin. |

## Spec deviations

None. The spec is implemented exactly: Donchian 20 breakout with an
ADX(14) > 25 entry filter, exit on ADX(14) < 20 or the opposite
breakout. The ADX exit threshold (20) is below the entry threshold
(25) by design, per the spec's own asymmetry.

No bug fixes requiring re-runs, no PnL-selected tuning.
