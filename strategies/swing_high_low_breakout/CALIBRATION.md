# Swing High Low Breakout — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Pivot width | 5 bars (2 left, 2 right), strict inequality | The spec's pivot definition: a swing high is a high strictly greater than the 2 bars on each side. A high merely equal to a neighbour is not a pivot. |
| Pivot timing | Recorded at confirmation bar (centre + 2) | A 5-bar pivot is only knowable once the 2 right-hand bars have closed. Placing it at the centre bar would be lookahead; placing it at centre + 2 keeps every value causal. |
| Ascending / descending | Strict: last pivot strictly above/below the previous one | The spec's "ascending" / "descending" read strictly; equal swing lows are not a higher low. |
| Break | Close strictly above/below the last pivot level | A close exactly at the level is not a break. |
| Exit | Opposite structure break (close beyond the last swing low/high) | Per spec: a long exits on a close below the last swing low, a short on a close above the last swing high. Note this makes long_exit identical to the short-breakout condition and short_exit identical to the long-breakout condition. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | Several pivots must form before the two-pivot ascending/descending test can pass; 60 bars is ample margin over the 5-bar pivot plus confirmation. |

## Spec deviations

1. **Pivot confirmation lag.** The spec defines pivots by the 2
   bars on each side. The shipped code records a pivot at its
   confirmation bar (centre + 2) rather than at the centre bar,
   because the pivot does not exist as information until those
   2 right-hand bars close. An entry can therefore fire at
   earliest 2 bars after the pivot bar itself.
2. **"Last two swing lows are ascending" uses the two most
   recently confirmed swing lows**, including one confirmed on
   the entry bar itself if applicable. No minimum separation
   between the pivots is imposed.
3. **Pure structure breakout, distinct from Dow-theory pullback
   entries.** This strategy enters on the break of the last
   swing high/low itself, with no pullback, retest, or
   confirmation beyond the break and the ascending/descending
   pivot sequence. A trader waiting for price to return to the
   broken level and hold is running a different system — that
   is support_resistance_flip, not this one. The ascending-lows
   / descending-highs filter is a trend-sequence condition, not
   a pullback entry.
4. **Harness stop/trail as an additional exit.** The spec's exit is
   the opposite structure break; the batch-standard risk layer
   (2xATR stop, 2.5xATR trail, 120-bar max hold) is applied on
   top, per the batch instruction.

No bug fixes requiring re-runs, no PnL-selected tuning.
