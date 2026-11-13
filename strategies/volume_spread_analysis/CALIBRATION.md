# Volume Spread Analysis — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Spread narrow threshold | Range < 0.5 × ATR(20) | Per spec: a narrow spread is half the prevailing ATR; ATR(20) is the standard Williams/Wyckoff volatility read. |
| Volume lower than each of previous two bars | v < v[-1] and v < v[-2] | Per spec: "lower than EACH of the previous two bars" — strictly lower than both, not lower than their average. |
| Stopping-volume decline | Close below close 10 bars ago | Per spec: "after a 10-bar decline". The decline is read as close < close[-10]. |
| Stopping-volume multiple | Volume > 2× trailing 20-bar mean volume | Per spec. |
| Stopping-volume close | Close in the upper half of its range (close > midpoint) | Per spec. |
| Upthrust high | High above the prior 20-bar high (excluding the current bar) | Per spec: "pushing above the 20-bar high". The current bar is excluded from the lookback so the probe is against established supply. |
| Upthrust close | Close in the lower third (close < low + range/3) | Per spec. |
| Upthrust volume | Volume > 1.5× trailing 20-bar mean volume | Per spec. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | ATR(20) + 20-bar volume mean need 20 bars; 60 gives margin. |

## Spec deviations

1. **Decline defined as close < close 10 bars ago.** "After a 10-bar
   decline" could also mean 10 consecutive down closes; the
   close-vs-close-10-bars-ago read is the standard one and is what
   shipped.
2. **Exit masked when both directions fire on one bar.** A down bar
   can be both stopping volume and an upthrust (probe above the
   20-bar high, close in the lower third, climactic volume). On
   such a bar both entries fire and the exits are masked, so the
   bar is an entry bar, not an exit bar; the harness takes the long
   side first when flat.
3. **Harness stop/trail as the practical exit.** Williams' system
   exits on the opposite VSA signal alone. The batch-standard risk
   layer (2xATR stop, 2.5xATR trail, 120-bar max hold) is applied
   on top, per the spec's own instruction, so 607 of 1,124 trades
   end on the stop/trail rather than the opposite signal.

No bug fixes requiring re-runs, no PnL-selected tuning.
