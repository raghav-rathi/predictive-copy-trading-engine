# Grid Trading — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Grid window | 200 bars | Trailing range long enough to be a real range on 1h crypto (~8 days); round-number choice from the spec. |
| Grid levels | 10 | Even split of the range; the canonical grid construction (equal intervals). The level count sets the step size (range/10) but the traded zones are defined by range fractions, below. |
| Long zone | Bottom 20% of range (grid_pos <= 0.20) | The bottom two grid levels: buy the dip of the range. |
| Short zone | Top 20% of range (grid_pos >= 0.80) | The top two grid levels: sell the top of the range. |
| Exit | Range midpoint (grid_pos 0.50) | Half the range of travel per round trip; symmetric for longs and shorts. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 250 | 200-bar grid window + 50 bars margin. |

## Spec deviations

1. **Single-position harness approximation.** A true grid holds one
   order per level and accumulates many small positions. The
   batch harness holds one position at a time, so the shipped system
   trades one round trip per zone visit (edge zone -> midpoint)
   instead of per-level scalps. Entries are therefore level
   conditions (signal stays on while price is in the zone) rather
   than one-bar crosses, so the harness can re-enter after a
   stop/trail exit while price is still in the zone. This is the
   closest faithful mapping of a grid onto a single-position
   harness, and it is stated here rather than hidden.
2. **Grid includes the current bar.** The trailing 200-bar high/low
   uses bars through the current close (the standard rolling-window
   definition); the close's position in that range is only known at
   the close, so there is no lookahead.
3. **Harness stop/trail as an additional exit.** The spec's exit is
   the midpoint; the batch-standard risk layer (2xATR stop,
   2.5xATR trail, 120-bar max hold) is applied on top, per the
   batch instruction. In a trending market this stop is what ends
   most grid trades, which is the known failure mode of grid
   trading (range breaks and never comes back).

No bug fixes requiring re-runs, no PnL-selected tuning.
