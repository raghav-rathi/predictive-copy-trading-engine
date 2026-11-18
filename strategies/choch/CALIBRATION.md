# Change of Character (ChoCh) — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Swing pivot | 5-bar, centre+2 confirmation | The spec's pivot definition; shared with sfp. |
| Trend | HH/HL = uptrend, LL/LH = downtrend, from the last two confirmed swing highs/lows | The spec's structure definition. |
| Displacement | Body \|close − open\| > 1.5x ATR(14) | The spec's threshold (goforexhub). |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | Pivot sequence + ATR(14) spin-up; 60 gives margin. |

## Spec decisions / ambiguities

1. **Trend and protected levels are read as of bar i-1.**
   The spec does not state this explicitly for ChoCh (it does for
   SFP), but the same discipline is applied: a ChoCh must break
   structure established before the breaking bar. A pivot
   confirming on bar i itself — which can flip the trend or move
   the protected level on that same bar — cannot be the structure
   that bar breaks.
2. **Mixed structure retains the previous trend.** The spec
   defines uptrend (HH/HL) and downtrend (LL/LH) but not the mixed
   case (e.g. higher highs with lower lows). The shipped code keeps
   the last trend instead of resetting to 0, so a single mixed
   pivot pair does not erase the trend state. Trend is 0 only until
   the first HH/HL or LL/LH pair forms.
3. **Protected swing = the low/high that produced the most recent
   swing extreme.** In an uptrend, the protected low is the latest
   swing low with centre before the most recent swing high's
   centre; in a downtrend, the protected high is the mirror. It
   updates only when a new swing extreme confirms, not when a new
   pullback low/high confirms on its own.
4. **Long exit "close above the last swing high".** Read as the
   last confirmed swing high (as of bar i-1), i.e. the head of the
   structure the long was betting against; the short exit is the
   mirror. The opposite-ChoCh leg of the exit is the same
   condition as the opposite entry.
5. **Harness stop/trail as an additional exit.** The spec's exits
   are the opposite ChoCh / close through the last swing extreme;
   the batch-standard risk layer (2xATR stop, 2.5xATR trail,
   120-bar max hold) is applied on top, per the batch instruction.

## What the exits actually did

Shipped run (225 trades): 192 trades ended on a signal exit and
only 33 on the harness stop/trail (BTC 75 signal / 13 stop, ETH
70 / 13, HYPE 47 / 7). The signal exit dominates because the
"close through the last swing extreme" leg fires readily: after a
ChoCh entry the close very often re-crosses the last swing
extreme within a few bars, so trades are cut quickly for small
losses — which is why the drawdown is small (-6.3% combined)
even though the strategy still loses (PF 0.80).

No bug fixes requiring re-runs, no PnL-selected tuning.
