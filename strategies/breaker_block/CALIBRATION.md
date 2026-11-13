# Breaker Block — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Structure lookback | 20 bars | Per spec: the impulsive move breaks the 20-bar high/low. |
| Order-block search window | Last opposing closed bar within 10 bars before the breakout bar | Per spec: "the last down-closed bar before an impulsive up move". The 10-bar window bounds the search to the bars that actually led into the impulse; a down bar 50 bars back did not cause this move. |
| Order-block zone | The opposing bar's [low, high] | Per spec. |
| Break-through | Close through the zone (below the low / above the high) | Per spec: closes, not wicks — a wick through the zone is a sweep, not a failure. |
| Retest | First bar closing back into the zone after the break, then the first bar closing back out of it (below the low / above the high) | Per spec: "short on the retest of the broken zone (first bar closing back below the zone after the break-through)". The retest bar is the return into the zone; the entry bar is the rejection out of it. |
| Breaker expiry | 200 bars after the break-through bar | Per spec. |
| Breaker invalidation | Close back through the far side of the zone (above the high for a bearish breaker, below the low for a bullish breaker) | Standard SMC: a full reclaim of the zone negates the role-reversal. Not in the spec text; added as the documented invalidation rule. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 100 | Structure lookback 20 + OB search 10 + breaker expiry horizon; 100 gives margin for the state machine to form its first blocks. |

## Spec deviations

1. **Liquidity-sweep precondition not enforced.** The canonical
   SMC breaker requires a liquidity sweep (a run beyond a prior
   swing high/low) before the structure break; the spec as given
   defines the breaker purely as a close through the order-block
   zone after a 20-bar-high/low break. The shipped code follows
   the spec as given — the 20-bar break itself is the displacement
   event — and does not add a separate sweep filter.
2. **Breaker invalidation on far-side reclaim** (see table above):
   a bearish breaker is void if price closes above the zone high,
   a bullish breaker if price closes below the zone low.
3. **Harness stop/trail as the practical exit.** The spec exits on
   the opposite breaker signal alone. The batch-standard risk layer
   (2xATR stop, 2.5xATR trail, 120-bar max hold) is applied on top,
   per the spec's own instruction, so 174 of 189 trades end on the
   stop/trail rather than the opposite signal.

No bug fixes requiring re-runs, no PnL-selected tuning.
