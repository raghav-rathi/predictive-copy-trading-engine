# Fisher ACD Opening Range — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Session | UTC calendar day | Crypto trades 24/7 with no pit open; the UTC day is the standard session boundary for 1h crypto. |
| Opening range | High/low of the first 1h bar of the UTC day (00:00–01:00 UTC) | Spec: the first hour sets the day's range; the OR bar itself is bar 0 of the day. |
| ATR window | 14 (Wilder ATR from `strategies.base`) | Spec; Fisher's A/C offsets are ATR-scaled. |
| A offset | 0.5 × ATR(14) | Spec: A-up = OR high + 0.5 ATR; A-down = OR low − 0.5 ATR. |
| C offset | 1.5 × ATR(14) | Spec: C-up = OR high + 1.5 ATR; C-down = OR low − 1.5 ATR. |
| Daily pivot | (prev UTC day high + low + close) / 3 | Spec: classic floor-trader pivot on the previous completed day. |
| Long entry | Close crosses above A-up AND close > pivot | Spec. |
| Short entry | Close crosses below A-down AND close < pivot | Spec. |
| Long exit (B) | Close below OR low | Spec (Fisher's B exit). |
| Short exit (B) | Close above OR high | Spec. |
| Failed-A reversal | Close below C-down → exit long + short_entry; close above C-up → exit short + long_entry | Spec. |
| No entries on day bar 0 | Entries gated to day_index ≥ 1 | Spec: the OR is only formed at the OR bar's close. |
| ATR window / stop / trail / target / max hold | 14 / 2.0× / 2.5× / None / 24 bars | Batch-standard risk layer, with max_hold 24 bars (one UTC day) per spec so a day trade cannot carry into the next session. |
| Risk frac / leverage / fees / slippage | 1% / 3.0× / 0.045% / 0.01% | Batch-standard risk layer. |
| WARMUP | 48 | Two full UTC days, covering the ATR(14) warmup plus one full day so the previous-day pivot exists. |

## Spec deviations / judgment calls

1. **Reversal entries carry no pivot filter.** The spec says a close
   beyond C "reverses to short/long" without mentioning the pivot, so
   the C-break entry fires on the C break alone (the pivot condition
   applies only to A-point entries). A C break already implies the
   close is far beyond the OR edge, so the pivot would rarely bind.
2. **"Crosses above/below" is the strict one-bar cross** (`crossed_above`
   / `crossed_below` from `strategies.base`): close above the level
   today while at/below it yesterday. A gap that opens above the new
   day's A-up with the previous close already above the old day's A-up
   does not count as a fresh cross.
3. **Exits are not gated to day_index ≥ 1.** The spec gates entries
   only; a position held overnight may exit on the new day's first bar.
4. **No entries on the first UTC day of the window.** The pivot is
   undefined until one full UTC day has completed, so A-point entries
   cannot fire there (the pivot comparison is False on NaN). This is a
   consequence of the spec, not a tuning choice.

No bug fixes requiring re-runs, no PnL-selected tuning.
