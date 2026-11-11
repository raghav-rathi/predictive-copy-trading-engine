# MACD + Session VWAP — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| MACD fast / slow / signal | 12 / 26 / 9 | Appel's standard MACD; the shared `strategies.base.macd` primitive. |
| Session VWAP | UTC-day anchored VWAP (typical price, volume-weighted, reset at UTC midnight) | Intraday regime line; crypto trades 24/7 so the session is defined by the UTC calendar day. Shared `strategies.base.anchored_vwap`. |
| Entry gate | long only if close > VWAP; short only if close < VWAP | Trade MACD crosses only with the intraday volume-weighted regime. |
| Exits | Opposite MACD cross, ungated by VWAP | Exits are momentum-state changes; the filter is an entry gate only (documented choice, fixed a priori). |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | MACD line needs 26 bars, signal line 9 more (35 total); 60 bars of margin. |

## Spec deviations

1. **Session = UTC calendar day.** The spec says "session (UTC-day)
   VWAP"; crypto has no exchange session, so the UTC day (00:00–
   24:00 UTC, 24 hourly bars) is the session. Implemented via the
   shared `anchored_vwap`, which floors timestamps to UTC days.
2. **Exits ignore the VWAP filter.** The spec gates entries on VWAP
   and exits on the opposite MACD cross; no VWAP condition was added
   to exits.
3. **No zero-line filter.** Some MACD systems also require the MACD
   line to be above/below zero. The spec does not, so none was added.

No bug fixes requiring re-runs, no PnL-selected tuning.
