# Camarilla Pivot Breakout — Calibration

No parameter was tuned to PnL. Every parameter below was fixed a
priori from the spec, and the backtest numbers were reported as-is.
Two alternates were run after the fact as a robustness check only;
neither was adopted.

| Parameter | Value | A priori rationale |
|---|---|---|
| R3 / S3 | C_prev ± (H_prev - L_prev) * 1.055 | Spec-assigned factor; levels from the prior completed UTC day only. |
| Day grouping | UTC date from t | Spec: prior completed UTC day. |
| Long entry | close crosses above prior-day R3 (transition only) | Spec: breakout above R3. |
| Short entry | close crosses below prior-day S3 (transition only) | Spec: breakdown below S3. |
| Long exit | close crosses back below R3 | Spec. |
| Short exit | close crosses back above S3 | Spec. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 200 | First levels appear after one full UTC day (24 bars) plus margin; 200 is deliberately generous. |

## Sweep results (same window, local cache only)

| Config | Trades | Net $ | PF | Fees $ |
|---|---|---|---|---|
| **Shipped factor 1.055** | **250** | **-1523.04** | **0.84** | **1839.10** |
| Alt-A factor 0.275 (canonical R3) | 1125 | -8784.60 | 0.77 | 7598.32 |
| Alt-B factor 0.55 (R4-style) | 625 | -4746.42 | 0.79 | 4549.29 |

Per-coin, Alt-A: BTC -3367.66, ETH -3572.98, HYPE -1843.97.
Per-coin, Alt-B: BTC -3014.69, ETH -1468.32, HYPE -263.41.
Both alternates lose money on all three coins while trading far more
often — closer levels just mean more failed breakouts and more fees.
Nothing was changed as a result of the sweep.

## Spec decisions / ambiguities

1. **The 1.055 factor is not canonical Camarilla.** The standard
   Camarilla R3 (BabyPips, TradingView, Strike) is
   R3 = C + (H - L) * 1.1 / 4 = C + (H - L) * 0.275, and R4 is
   C + (H - L) * 0.55. The assigned 1.055 is ~3.8x the canonical R3
   offset and ~1.9x the canonical R4 offset — the level sits more
   than a full prior-day range from the prior close. It was
   implemented exactly as assigned; the canonical 0.275 factor was
   run as Alt-A above and loses far more (-$8,784.60), so the
   discrepancy does not flip the verdict either way.
2. **Crosses are judged against the current bar's level** for both
   the current and previous close. The level only changes at a
   UTC-day boundary; comparing the previous close to the previous
   bar's (stale) level would let a level jump alone fire a signal
   with no price move. A dedicated test covers this.
3. **No levels before the first full day completes.** Bars in the
   first UTC day have NaN R3/S3 and cannot signal, even if the
   window starts mid-day — the first usable levels come from the
   first fully observed day.
4. **The prior day's close is the last close of that day**, and the
   prior day's high/low are that day's extremes — standard
   Camarilla inputs.

## What the exits actually did

Shipped run (250 trades): 145 trades ended on the harness stop /
trail and 105 on the signal exit (price crossing back through the
level). The signal exit rate (42%) is high for a breakout system —
most breakouts of a level a full range away fail and come straight
back, which is why the win rate is only 24.0%.

No bug fixes requiring re-runs, no PnL-selected tuning.
