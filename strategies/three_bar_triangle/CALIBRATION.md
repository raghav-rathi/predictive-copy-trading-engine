# Raschke 3-Bar Triangle — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Contraction definition | h[i] < max(h[i-1], h[i-2]) AND l[i] > min(l[i-1], l[i-2]) | Raschke's definition, verbatim from the spec. |
| Triangle | max/min of the 3 bars ending at the contraction bar | The spec's triangle high/low. |
| Entry window | 5 bars after the contraction bar | The spec's "within 5 bars". |
| Volume filter | v > 1.25x SMA(v, 20) | The spec's volume-expansion requirement (Raschke requires a volume increase on the directional break). |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | Volume SMA(20) needs 20 bars; 60 gives margin. |

## Spec decisions / ambiguities

1. **The 5-bar window counts from the contraction bar.** Levels
   are valid on the contraction bar itself and the 5 bars after
   it (age 0..5). The contraction bar can never trigger (its
   close is inside its own triangle), so entries effectively occur
   on bars c+1..c+5. A breakout on bar c+6 does not trade.
2. **A new contraction restarts the triangle.** Inside-bar
   contractions cluster: if another contraction prints while a
   triangle is live, the levels are replaced by the new 3-bar
   range and the 5-bar clock restarts. The alternative (keep the
   first triangle until it expires) would trade breaks of a stale,
   wider range.
3. **Volume uses the breakout bar's own volume.** The filter is
   v[j] > 1.25 * SMA(v, 20)[j] on the breakout bar j, with the
   SMA including bar j's volume. The sources do not pin down
   whether the average should exclude the breakout bar; including
   it is the standard SMA reading and slightly raises the bar.
4. **The failed-breakout exit only lives while the triangle
   lives.** "Close below the triangle low" is evaluated against
   the currently valid triangle levels; once the 5-bar window
   expires (or no contraction has printed recently), the exit
   cannot fire and the trade rides on the harness stop/trail or
   the opposite signal. This is a direct consequence of the
   5-bar window, not a separate choice.
5. **Harness stop/trail as an additional exit.** The spec's exits
   are the far-edge close / opposite signal; the batch-standard
   risk layer (2xATR stop, 2.5xATR trail, 120-bar max hold) is
   applied on top, per the batch instruction.

## What the exits actually did

Shipped run (1,134 trades): 767 trades ended on the harness
stop/trail and 367 on a signal exit (BTC 271 stop / 126 signal,
ETH 280 / 123, HYPE 216 / 118). The far-edge exit fires often —
about a third of trades close back inside/below the triangle —
but it does not save them: the 2xATR stop still takes most
trades, and the 33.2% win rate with PF 0.76 says the volume
filter does not separate real breakouts from noise on 1h crypto.

No bug fixes requiring re-runs, no PnL-selected tuning.
