# Heikin Ashi + MACD Momentum Filter — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Heikin Ashi candles | HA-close=(o+h+l+c)/4, HA-open=(prev HA-open+prev HA-close)/2, HA-high=max(h,HA-open,HA-close), HA-low=min(l,HA-open,HA-close) | The standard Heikin Ashi definition from the source script. |
| HA-open seed | First bar: (o + c) / 2 | The source script seeds the recursion the same way; there is no previous HA bar to average with. |
| MACD | 12 / 26 / 9 on the HA close | The source script's MACD on the Heikin Ashi close, not the raw close. |
| Entry | Histogram zero-cross AND same-direction HA candle (HA close > HA open for longs, < for shorts) | Per spec: both conditions on the same bar. |
| Exit | Opposite histogram zero-cross | Per spec; the exit does NOT require the HA candle to agree — the cross alone exits. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | MACD slow leg 26 + signal 9 needs ~35 bars; 60 gives margin. |

## Spec deviations

1. **Exit ignores the HA candle.** The spec says "Exit: opposite
   histogram zero-cross" with no HA condition attached, so the exit
   fires on the cross alone. Requiring a confirming HA candle
   would be a different system.
2. **HA-open seed.** The spec defines HA-open recursively but does
   not state the first-bar seed; (o + c) / 2 is the conventional
   TradingView seed and is what the source script uses.
3. **Harness stop/trail as an additional exit.** The batch-standard
   risk layer (2xATR stop, 2.5xATR trail, 120-bar max hold) is
   applied on top of the spec's exit, per the batch instruction.
   754 of 1168 trades ended on the stop/trail, 414 on the signal
   exit, so both exits matter here.
4. **Same-bar coincidence required.** The cross and the HA
   direction must agree on the same bar; a cross on a bar whose HA
   candle points the other way is not an entry, and the entry is
   not deferred to the next bar. This is the literal spec reading.

No bug fixes requiring re-runs, no PnL-selected tuning.
