# Hurst Exponent Regime Switch — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Hurst window | 200 bars | The spec's window; long enough for scales up to 100 to have ≥2 chunks. |
| Hurst scales | [10, 20, 40, 100] | The spec's scales (log-spaced, 2 chunks at scale 100). |
| R/S chunk rule | non-overlapping chunks, S ddof=1, skip S or R ≤ 1e-12, H = 0.5 if < 2 valid scales, clip H to [0, 1] | The spec's "guard std=0 chunks (skip them; if no valid scale, H=0.5)"; the 1e-12 epsilon covers floating-point residue on constant returns (a constant-return window otherwise yields a spurious slope). |
| Regime bands | H > 0.55 trend, H < 0.45 reversion, else neutral | The spec's bands. |
| Hysteresis | 3 consecutive bars in the same new band | The spec's "mode changes only after 3 consecutive bars in the new band"; implemented per-band, so a bar in a third band restarts the count rather than counting toward a switch. |
| Trend entries | EMA(20/50) crosses | The spec's trend-mode rule, via `base.ema`. |
| Trend exit | opposite cross, or close through EMA(50) | The spec's "exit on opposite cross" plus the mode's invalidation. |
| Reversion entries | RSI(14) cross below 30 / above 70 | The spec's "RSI(14) <30 long / >70 short", implemented as cross events (a level rule would re-fire every bar RSI sits in the extreme; the harness takes one position at a time, but cross events state the entry bar unambiguously). |
| Reversion exit | RSI crossing back through 50 | The spec's exit rule. The "opposite signal" exit is subsumed: an RSI jump from below 50 to above 70 in one bar also crosses 50, so no separate clause is needed. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 250 | 200-bar Hurst window + EMA warmup, per the spec. |

## Spec decisions / ambiguities

1. **Neutral is a mode, not a pause.** After 3 consecutive
   neutral bars the mode becomes 0 (no entries, no signal
   exits). A single neutral bar only breaks a pending streak
   toward the other mode; it does not itself switch the mode.
2. **Exits are mode-gated on the mode in force.** A trade opened
   in trend mode is exited by trend rules while the mode
   persists; if the mode flips mid-trade, the new mode's exit
   rules take over. While the mode is neutral there is no signal
   exit and the harness stop/trail/max-hold carries the trade.
3. **R/S small-sample bias.** On 200-bar windows the R/S
   estimator is biased upward: white noise reads H ≈ 0.59–0.67
   at these scales (verified on synthetic data in the test
   suite). Consequence on the shipped window: mean H ≈ 0.59,
   trend mode 72–75% of bars, reversion mode ~1% of bars. The
   reversion leg is therefore nearly untested by the backtest.
   This is reported, not corrected — widening the bands to
   manufacture reversion trades would be tuning to PnL.
4. **Log returns, first bar 0.0.** `log_ret[0] = 0.0` (no prior
   close); windows containing it are only used before bar 199,
   where H is pinned to 0.5 anyway.
5. **No bug fixes requiring re-runs, no PnL-selected tuning.**

## What the exits actually did

Shipped run (256 trades): 214 exits on the harness stop/trail,
42 on signal exits. The mode-gated signal exits fire, but the
stop/trail dominates — entries are frequent (EMA crosses in a
mostly-trend regime) and positions are usually stopped out
before the opposite cross or invalidation prints.
