# SMT Divergence — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Pivot width | 5 bars (centre ± 2) | The spec's "causal 5-bar pivots on BOTH series (pivot recorded at confirmation bar centre+2, never at centre)". |
| Divergence | traded lower low + reference higher low (bullish), mirror for bearish | The spec's divergence definition. |
| Low gap | 10 bars max between the two lows/highs (centre distance) | The spec's "the two lows within 10 bars of each other". |
| Entry trigger | first close above the traded coin's prior swing high (bullish) / below its prior swing low (bearish) | The spec's "entry = first close above traded's prior swing high (structure shift)". |
| Entry expiry | 20 bars after arming | The spec's "within 20 bars". |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | Two pivots per series plus the divergence sequence need ~25 bars to form; 60 gives margin. |

## Spec decisions / ambiguities

1. **"Prior swing high" is the most recent one, and it updates.**
   The trigger level is the traded coin's most recent confirmed
   swing high at arming time; while armed, a newly confirmed swing
   high replaces it (it is the freshest structure). The classic ICT
   reading uses the interim high formed after the divergence low,
   which is what this update produces in practice.
2. **A deeper traded extreme while armed moves the invalidation.**
   While a bullish divergence is armed, a newly confirmed traded
   swing low below the divergence low updates the divergence low
   (the exit invalidation level); the mirror applies bearish. The
   trigger level is unaffected by new lows.
3. **A close through the divergence extreme while armed disarms.**
   If price closes below the divergence low (bullish) before the
   structure shift fires, the setup is dead — the divergence failed
   and the trade is not taken. The mirror applies bearish.
4. **Arming is evaluated on confirmed pivots, either order.** The
   divergence arms on the bar when the second of the two lows/highs
   confirms, whichever coin confirms later; the 10-bar gap is
   measured between pivot centres, not confirmation bars.
5. **A divergence pair arms once.** After a pair (traded centre,
   reference centre) arms, the same pair cannot re-arm; a new pair
   (a fresh traded extreme against a fresh reference extreme) can.
   If a setup expires or invalidates, the next divergence is a new
   pair.
6. **Exits use the divergence extreme recorded at the entry
   trigger.** The invalidation level is the divergence swing low/high
   as of the trigger bar (`last_bull_div_low` /
   `last_bear_div_high`, forward-filled). If a newer divergence
   triggers while a trade is open, the level updates to the newer
   one.
7. **Harness stop/trail as an additional exit.** The spec's exits
   are the opposite-SMT signal / divergence invalidation; the
   batch-standard risk layer (2xATR stop, 2.5xATR trail, 120-bar
   max hold) is applied on top, per the batch instruction.

No bug fixes requiring re-runs, no PnL-selected tuning.
