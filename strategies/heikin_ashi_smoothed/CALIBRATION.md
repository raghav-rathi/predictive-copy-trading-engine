# Smoothed Heikin-Ashi — Calibration

## Parameter choices

| Parameter | Value | Why |
|---|---|---|
| HA construction | Standard (ha_close = (o+h+l+c)/4, recursive ha_open) | The textbook definition; anything else would not be Heikin-Ashi. |
| Smoothing | EMA(5) on ha_open and ha_close | Short enough to track 1h trends, long enough (in theory) to filter single-bar noise. This is the variant's defining choice. |
| Stop / trail | 2.0x / 2.5x ATR | Batch standard. |
| Max hold | 168 bars (~7 days) | Rarely binds here — the opposite-cross exit fires far sooner in practice. |
| Risk / leverage | 1% / 3x | Batch standard. |

## Sensitivity note

The failure mode is structural, not parametric: exits are the
opposite cross, so the strategy has no flat state and trades
every chop flip. Lengthening the smoothing EMA would delay flips
further (worse entries, same count in sustained chop); shortening
it converges back to raw Heikin-Ashi (more flips). Neither
direction fixes the design, and neither was tuned on this window
— the shipped EMA(5) is the published variant, tested as-is.

## Verdict: loser

Ship as a documented loser, and as a cautionary result: smoothing
a noisy signal is not the same as filtering it. Do not trade this
variant at 1h.
