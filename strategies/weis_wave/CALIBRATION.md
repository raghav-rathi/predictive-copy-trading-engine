# Weis Wave — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Swing reversal | 1.5 * ATR(14) | Spec: wave ends when the close reverses 1.5x ATR(14) from the running swing extreme. ATR is Wilder ATR(14) from `strategies.base`, computed causally through the current bar. |
| ATR window | 14 | Spec / batch-standard ATR window. |
| Volume comparison | completed wave volume < 0.85 x previous completed wave volume | Spec: the just-completed wave's effort drying up to under 85% of the wave before it. |
| Wave direction start | +1 (up) from the first bar | Spec: start in "up" direction from the first bar. |
| Wave volume | sum of bar volumes from wave start through current bar, inclusive | Spec. |
| Entry | on the bar the new wave starts (wave_dir flips) with the volume gate passing | Spec's usable form (see deviations). |
| Exit | start of a new wave in the opposite direction | Spec: long exits when a down-wave starts, short exits when an up-wave starts. |
| ATR stop / trail / max hold | 2.0x / 2.5x / 240 bars | Batch-standard risk layer (spec). |
| Risk frac / leverage / fees | 0.01 / 3.0x / 0.00045 + 0.0001 | Batch-standard risk layer (spec). |
| WARMUP | 60 | ATR(14) needs 14 bars + wave construction needs several completed waves before any entry can fire; 60 bars of margin. |

## Spec deviations / clarifications

1. **Entry timing (spec as written is unusable).** The spec's first
   form — enter when the new wave's volume exceeds the previous
   wave's by 15–20% — cannot be evaluated at wave start, because the
   new wave has ~1 bar of volume. Implemented instead the spec's own
   standard usable form: enter on the bar the new wave starts when
   the just-completed wave's volume was under 85% of the wave before
   it (effort drying up into the turn). No other entry rule was used.
2. **Reversal-bar volume assignment.** The spec says volume is summed
   "from wave start through current bar, inclusive" and that the
   reversal bar is the bar "on which the previous wave ended and the
   new wave begins". The reversal bar is therefore counted as the
   FIRST bar of the new wave, not the last bar of the completed wave:
   a completed wave's volume runs from its start through the bar
   before the reversal bar. The alternative (counting the reversal
   bar in the completed wave) would shift every completed-wave volume
   by one bar's volume.
3. **ATR warmup.** `strategies.base.atr` returns NaN for the first 13
   bars, so no reversal can trigger before bar 14. This is a property
   of the shared ATR primitive, not a spec change; WARMUP = 60 covers
   it.
4. **No session gaps.** The Weis Wave was designed for session-based
   markets; on 24/7 crypto the swing definition runs continuously
   with no day-boundary reset. No reset was added — the spec does not
   call for one.

The implementation was verified against hand-computed cases: on a
flat frame the wave never flips and volume accumulates exactly
10/bar; on crafted frames the completed-wave volumes are exactly
2500 / 50 (long entry) and 250 / 1000 / 50 (short entry), the volume
gate blocks an entry when the completed wave carries 2500 vs a 2125
threshold, and appending future bars changes no earlier indicator or
signal value.

No bug fixes requiring re-runs, no PnL-selected tuning.
