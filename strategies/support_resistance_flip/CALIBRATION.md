# Support Resistance Flip — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Pivot width | 5 bars (2 left, 2 right), strict inequality | The spec's pivot definition, same as swing_high_low_breakout. |
| Pivot timing | Recorded at confirmation bar (centre + 2) | A 5-bar pivot is only knowable once the 2 right-hand bars have closed; recording it at the centre bar would be lookahead. |
| Level window | Trailing 50 bars (pivot centre within the last 50 bars) | The spec's window. Stale levels older than 50 bars drop out of the universe. |
| Touch definition | Bar's low within 0.5x ATR(14) of the level, i.e. \|low - level\| <= 0.5 * ATR | The spec's literal definition ("price touched it (low within 0.5x ATR(14) of the level)"). Applied to both resistance and support levels, using the low as specified. |
| Touch count | >= 2 touches in the trailing 50-bar window through the break bar | The spec's minimum. Touches are counted with the break bar's ATR applied to every bar in the window. |
| Break | Close crosses beyond the level (strict, with prior close on the other side) | A close merely sitting above a level does not re-open a setup every bar; only the crossing bar opens one. |
| Retest window | Next 20 bars after the break bar (break bar excluded) | The spec's expiry. A retest on the break bar itself does not count — the break bar's close is already beyond the level by construction. |
| Retest proximity | \|low - level\| <= 0.5x ATR, using that bar's ATR | The spec's "low comes within 0.5x ATR of the level", evaluated bar by bar. |
| Retest hold | Close back on the flipped side (above for broken resistance, below for broken support) | The spec's "closes back above/below the level". Strict inequality. |
| Exit | Close back across the flipped level (strict) | Per spec: long exits on a close below the flipped level, short on a close above it. |
| Multiple breaks | Newest qualifying break in a direction replaces a still-pending setup in that direction | The most recent break is the level closest to current price and the relevant flipped level. |
| Pending invalidation | A close back across the level during the retest window does NOT cancel the pending setup | The spec is silent; the setup stays pending until a retest-hold fires or the 20 bars expire. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 120 | 50-bar level window + pivot confirmation + touch history + ATR(14); 120 bars is ample margin. |

## Spec decisions / ambiguities resolved

1. **Touch uses the low for both level types.** The spec's
   parenthetical defines a touch by the bar's low ("low within
   0.5x ATR(14) of the level") without distinguishing
   resistance from support, so the shipped code applies the
   low-based definition to both. A high-based touch for
   resistance would be the more conventional reading, but it is
   not what the spec says.
2. **Touch-count ATR.** The touch count at the break is evaluated
   with the break bar's ATR applied uniformly across the
   50-bar window, rather than each historical bar's own ATR.
   The retest proximity, by contrast, uses each retest bar's
   own ATR. Both are documented here.
3. **Break is a crossing, not a state.** Without the crossing
   requirement, every bar closing above a stale resistance
   level would open a fresh 20-bar pending setup forever.
   Only the bar that crosses the level opens a setup.
4. **Pivot levels are individual pivots, not merged zones.**
   Two pivots at (nearly) the same price are separate levels;
   if both break on the same bar, the one nearest the close
   becomes the pending level.
5. **Harness stop/trail as an additional exit.** The spec's exit is
   the close back across the flipped level; the batch-standard
   risk layer (2xATR stop, 2.5xATR trail, 120-bar max hold) is
   applied on top, per the batch instruction.

No bug fixes requiring re-runs, no PnL-selected tuning.
