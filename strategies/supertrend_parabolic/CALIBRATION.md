# Supertrend Parabolic — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Supertrend period / multiplier | 10 / 3.0 | The spec's Supertrend parameters; the standard setting. |
| PSAR step / max AF | 0.02 / 0.20 | Wilder's standard PSAR parameters, per the spec. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | Supertrend needs ~10 bars to seed, PSAR seeds immediately; 60 gives margin for the agreement condition to settle. |

## Spec decisions / ambiguities

1. **Entry is the turn-on bar, not every agreement bar.** The spec
   says "the bar on which price becomes above BOTH lines", so the
   entry fires only when the combined condition switches from
   false to true (prior-bar value of the combined condition).
   Holding while already above both lines does not re-enter.
2. **Exit is either tool flipping.** "c < supertrend OR c < psar"
   — a single disagreement exits, even if the other tool still
   agrees. This is the strict reading of the spec.
3. **PSAR initialisation.** The Wilder loop is seeded long with
   SAR = low[0] and EP = high[0] (bar 0 only, so no lookahead).
   An alternative seed (trend from the first two closes) would
   peek at bar 1 when computing bar 0's SAR; the shipped seed
   avoids that. The PSAR flips to a downtrend within one bar on
   a falling open, so the seed has no lasting effect.
4. **PSAR flip-bar SAR value.** On a flip bar the SAR is set to
   the prior extreme point (the standard Wilder rule), which is
   on the far side of price — so the flip bar itself already
   satisfies the exit condition for the old direction.
5. **Harness stop/trail as an additional exit.** The spec's exits
   are the either-line flips; the batch-standard risk layer
   (2xATR stop, 2.5xATR trail, 120-bar max hold) is applied on
   top, per the batch instruction.

## What the exits actually did

Shipped run (937 trades): 618 trades ended on the harness
stop/trail and 319 on a signal exit (BTC 201 stop / 101 signal,
ETH 219 / 76, HYPE 198 / 142). The either-line-flip exit fires
often, but it does not save the trades — most agreement
entries are already late, and price reverses into the 2xATR
stop before either line flips back.

No bug fixes requiring re-runs, no PnL-selected tuning.
