# Balanced Price Range — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| FVG definition | bullish low[i] > high[i-2], bearish high[i] < low[i-2]; gap confirmed at bar i | The spec's / standard ICT FVG definition; the gap is known only at bar i, so it is recorded then. |
| Second-gap window | 60 bars | The spec's window: the two gaps must be near each other in time to be one structure. |
| Overlap | strict (max bottoms < min tops) | A zero-width "overlap" (gaps merely touching) is not a zone. |
| "Traded beyond" | a CLOSE beyond the zone (above the top / below the bottom) | Interpretation choice: the spec says "price had traded above the zone"; the shipped reading uses closes, not wicks, so a wick poke without a close beyond does not arm the entry. |
| Zone expiry | 100 bars after formation | The spec's expiry. |
| Invalidation | close through the zone (below a bullish bottom / above a bearish top) | The spec's rule; the zone is published for the invalidation bar itself so the signal layer sees the exit close. |
| One entry per zone | entry fires once, then the zone is exit-only | The spec's "first close inside"; later touches of the same zone do not re-enter. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | FVGs need 3 bars and a BPR needs two gaps; 60 gives margin. |

## Spec decisions / ambiguities

1. **The later gap sets direction.** A BPR formed by a bullish
   gap followed by a bearish gap is bearish, and vice versa — the
   zone is the same overlap either way, but the traded direction
   follows the second gap.
2. **A newer BPR replaces the old one on the same side.** When a
   new overlapping pair forms, the fresh zone (with a fresh
   100-bar clock and un-armed entry) replaces the old one, even
   if the old one had already armed its entry. The old zone is
   gone, not queued.
3. **The first gap is not consumed.** After a BPR forms, the two
   gaps stay on record: a third gap of either direction can pair
   with the most recent opposite gap to form a new BPR. Only the
   most recent gap per direction is kept.
4. **FVG gaps are not reflection-symmetric.** A bull gap is
   [high[i-2], low[i]] while a bear gap is [low[i], high[i-2]];
   mirroring a frame does not map bull gaps to bear gaps with the
   same endpoints. The mirrored-frame test asserts the zone the
   code actually produces ([98,99]), not the naive reflection.
5. **Expiry kills the exit too.** Once a zone expires (100 bars),
   its columns go NaN, so a later close through the old zone
   does not produce a signal exit; an open trade then relies on
   the harness stop/trail/max-hold.

## What the exits actually did

Shipped run (509 trades): 337 trades ended on a signal exit
(close through the zone or opposite signal) and 172 on the
harness stop / trail. The zone-invalidation exit is the working
exit here — most BPR trades end by closing through the zone
shortly after entry, which is also why the win rate is low
(25.9%) while the profit factor is ~1.02: a minority of trades
run far enough to offset many small zone-exit losses.

No bug fixes requiring re-runs, no PnL-selected tuning.
