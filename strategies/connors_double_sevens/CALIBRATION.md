# Connors Double 7s — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Day definition | UTC calendar day; daily close = last close of the day | The system's "days" are calendar days; UTC matches the 1h candle grid. |
| Trend filter | Daily close above SMA(200) of daily closes | Connors & Alvarez: only buy pullbacks in an uptrend, defined by price above the 200-day average. |
| Long entry | Daily close is the lowest daily close of the last 7 days (incl. today) AND above SMA(200) | The Double 7s entry rule, verbatim. |
| Long exit | Daily close is the highest daily close of the last 7 days (incl. today) | The Double 7s exit rule, verbatim; the only exit in the original system. |
| Signal timing | Evaluated on the day's last 1h bar (23:00 UTC); harness enters/exits at the next bar's open (00:00 UTC) | "Buy on the close" — the signal is known only at the day's close, so this is causal and matches the original. |
| Shorts | None (allow_shorts=False) | The original system is long-only. |
| Stop / target / trail / max hold | 10.0x ATR / None / None / None | The original system has NO stop and NO target. The 10x ATR stop is a harness formality, intended to be effectively inert. |
| ATR window | 14 | Batch-standard risk layer (only used for the formality stop and sizing). |
| risk_frac / max_leverage | 0.01 / 3.0x | Batch-standard sizing. |
| fee / slippage | 0.045% / 0.01% per side | Hyperliquid taker fee + slippage, batch standard. |
| WARMUP | 4800 (200 daily bars x 24) | The SMA(200) needs 200 days of daily closes before the first eligible signal. This leaves only ~40 eligible trading days in the window — the honest, faithful result; 10 closed trades is the cost of the warmup, not a data error. |

## Spec deviations / findings

1. **The 10x ATR stop was not inert.** The brief expected exit_reason
   'stop' to be 0 or near-0. In the backtest 4 of 10 exits were stops
   (BTC 1, ETH 2, HYPE 1), each costing ~1% of equity by construction
   of the risk sizing. Cause: the stop is 10x the *hourly* ATR, but
   positions are held for days (up to 16), and the Oct–Nov 2026
   downtrend's multi-day drift exceeded 10x the 1h ATR. The original
   system has no stop, so a stop-free run would differ; no parameter
   was changed in response, and this is reported as-is.
2. **Day-close bar, not literally 23:00.** The signal is set on the
   last 1h bar of each UTC day present in the frame rather than
   hard-coding hour 23. In this window the grids are complete (BTC/ETH
   5775 bars = the full hourly grid; HYPE 5773, missing only the first
   two hours of 2026-03-14), so every day's last bar is its 23:00 bar
   and this deviation had no effect.
3. **Tie corner case.** If all 7 daily closes are equal, a day is
   simultaneously a 7-day low and a 7-day high. If that close is also
   above the SMA(200), entry and exit fire on the same bar (the
   harness would exit an open long, then re-enter on the same signal).
   This occurred on zero bars in the backtest window; it is documented
   here rather than special-cased, to stay faithful to the rules as
   written.

No spec corrections were needed beyond the above: the daily resample,
7-day low/high, SMA(200) filter, and buy-on-close timing are all
implementable exactly as specified on 24/7 crypto data (no session
gaps involved). Verified against hand-computed cases: flat 100s give
SMA(200) = 100.0 from day 199's close; a crafted 200-days-at-100 then
110→104 pullback gives SMA(200) = 20049/200 = 100.245, 7-day low 104,
and an entry on day 206's 23:00 bar; a 7-day low below the SMA(200)
produces no entry.

No bug fixes requiring re-runs, no PnL-selected tuning.
