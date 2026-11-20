# VWAP Bollinger Bands — Calibration

No parameter was tuned to PnL. Every parameter below was fixed a
priori from the spec, and the backtest numbers were reported as-is.
A small sweep (2 alternate settings, run and reported honestly below)
was used only to check robustness, not to select the shipped config.

| Parameter | Value | A priori rationale |
|---|---|---|
| Session anchor | UTC calendar day, reset 00:00 UTC | The spec's anchor. Crypto trades 24/7, so there is no true session open — the UTC day is the adaptation, stated honestly in the README. |
| Typical price | tp = (h + l + c) / 3 | Standard typical price. |
| VWAP | cumulative sum(tp * v) / sum(v) since session start | Standard session VWAP. |
| Band width | VWAP +/- 2.0 volume-weighted SD, SD from cumulative sums: sqrt(sum(v * tp^2) / sum(v) - VWAP^2), floored at 0 | The spec's 2.0 SD bands; the cumulative-sum form keeps it causal. |
| Regime filter | ADX(14) < 25 (Wilder ADX via `strategies.base.adx`) | The spec's ranging-regime gate: only fade bands when there is no strong trend. |
| Exit | close back at/through VWAP | The spec's mean-reversion exit. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 40 | VWAP needs only a few bars, but ADX needs ~28 bars to become valid; 40 gives margin. |

## Sweep (robustness check only — shipped config unchanged)

| Setting | Combined trades | Win% | Net $ | PF | Fees $ |
|---|---|---|---|---|---|
| **Shipped: BAND_K 2.0, ADX < 25** | **1078** | **52.3%** | **-11712.13** | **0.60** | **7588.73** |
| Alt A: BAND_K 1.5 | 1675 | 51.0% | -19033.84 | 0.53 | 8968.71 |
| Alt B: BAND_K 2.5 | 666 | 53.3% | -7462.26 | 0.54 | 5122.71 |

All three settings lose with PF 0.53–0.60. Alt B (wider bands)
loses less in dollars (-$7,462.26) because it trades less often
(666 trades), but its profit factor (0.54) is worse than shipped
(0.60) — the smaller dollar loss is a trade-count effect, not an
edge. The shipped config was kept as specified; no setting was
selected on PnL.

## Spec decisions / ambiguities

1. **Early-day bands are noisy by construction.** At 00:00 UTC
   the cumulative sums restart, so the first bars of each day
   have a VWAP and SD computed from 1–2 bars (SD = 0 on the
   first bar, so the bands equal VWAP). A close below/above the
   band in the first hours of a UTC day is a much weaker signal
   than the same move late in the day. The backtest includes
   this as shipped; no minimum-bars-per-session gate was added
   because the spec does not call for one.
2. **ADX is global, not session-reset.** ADX(14) is computed over
   the whole series, so it is valid after ~28 bars from the
   window start and is NaN (blocking entries) before that.
3. **Volume-weighted SD, not plain SD.** The bands use the
   volume-weighted standard deviation of tp around VWAP, not the
   unweighted rolling std of closes — heavy-volume prices pull
   the SD. With constant volume it reduces to the population std
   of tp within the session.
4. **Zero volume.** If cumulative session volume is 0, VWAP and
   the bands are NaN and no entry fires.

## What the exits actually did

Shipped run (1,078 trades): 761 trades ended on the signal exit
(close back at VWAP) and 317 on the harness stop / trail. The
signal exit works as designed — most trades do revert to VWAP —
but the average win is far smaller than the average loss
(PF 0.60 at a 52.3% win rate), so the exit is booking small
reversions while the losers run.

No bug fixes requiring re-runs, no PnL-selected tuning.
