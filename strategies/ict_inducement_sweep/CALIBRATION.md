# ICT Inducement → Sweep → MSS Entry — Calibration

All parameters were fixed **a priori** from the ICT source
material and 1h-bar reasoning — there is no in-sample sweep, so
there is nothing to select on this window. (The backtest produced
0 trades, so there is no PnL to tune to in any case.)

## Translation choices (mechanical ICT → code)

Every step below is a judgement call; each is recorded so the
specification can be argued with, rather than silently assumed.

| Parameter / choice | Value | Rationale |
|---|---|---|
| Displacement | range > 1.5xATR(14), close in the outer quarter of the range | the source's "displacement leg" is an impulsive move; 1.5xATR is the house displacement threshold (also used by the existing liquidity-sweep family), and the outer-quarter close is the "closing strongly" test |
| Order block | last opposing candle in the 10 bars before the displacement leg; zone = that candle's [low, high] | the source's "last opposing candle before a displacement leg"; 10 bars bounds the search to the immediate pre-impulse structure |
| Inducement | first 3-bar-confirmed swing low/high after the displacement, sitting above the OB top / below the OB bottom | the source's "first minor swing low/high — or equal lows/highs — sitting between price and the POI"; 3-bar confirmation is the house minor-swing standard; equal extremes qualify via the min/max-window test |
| Sweep | close beyond the inducement extreme AND into the OB zone (close <= OB top for longs) | the source's "price sweeps through the inducement into the POI"; requiring the close (not just a wick) into the zone keeps it mechanical and avoids wick-only false sweeps |
| MSS level | highest high / lowest low from the inducement bar through the sweep bar | the minor structure extreme the sweep retraced from; breaking it is the structure shift |
| MSS + displacement | the break bar should itself be the displacement bar (range > 1.5xATR, strong close) leaving an FVG; if not, a displacement bar within 10 bars still confirms | **translation correction, documented:** in ICT the displacement IS what breaks structure — MSS and displacement are one confirming event, not two sequential bars. An earlier draft required a separate displacement bar after the MSS bar; the diagnostic showed that two-bar requirement never completes (0 of 11 MSS events), which is an artifact of the drafting, not of the market. The shipped rule accepts the break bar itself as the displacement bar. The backtest result is 0 trades under either reading, so this choice optimizes no outcome |
| FVG | bullish: displacement bar's low above the high two bars earlier (bearish mirror) | the standard 3-candle FVG definition; the gap must be left by the displacement bar itself |
| OTE level | 70.5% retracement of the displacement leg (sweep bar → displacement bar) | the source's "70.5% OTE" (optimal trade entry); the leg is measured from the sweep extreme, the point the displacement launched from |
| OTE entry trigger | first bar whose low/high touches the level (limit-style) | a limit order at the OTE level fills on a touch; the harness executes at the next bar's open, so the fill is near the level, not exactly on it |
| OTE expiry | 24 bars after the displacement bar | a setup that hasn't retraced in a day was not the setup; bounds the wait so stale setups don't fire on unrelated later touches |
| POI failure | close beyond the OB extreme before entry drops the setup | the OB is the invalidation: a close through it means the POI did not hold |
| Timeouts | inducement 48 bars, sweep 48, MSS 24, displacement 10 | generous enough for 1h structure to develop, tight enough that stale setups don't linger; all fixed a priori |
| Killzone filter | NOT implemented | the session/killzone variant is a separate thesis (time-of-day gate); adding it would conflate two ideas and is documented in README.md |
| ATR window | 14 | canonical |
| Stop | 2xATR | **deviation from source:** ICT stops go "beyond the POI" (past the OB extreme). RiskConfig has a single ATR window and ATR-based stops, so the stop distance cannot be set to the OB extreme. 2xATR is the closest faithful mapping: the OTE-to-OB distance on 1h bars is typically ~1–2xATR. It is an approximation, not the source rule |
| Target | 4xATR (= 2x the stop distance) | **same deviation, carried through:** the source targets the next liquidity pool at ~2R; with a 2xATR stop, 4xATR is the 2R target in the only units RiskConfig supports |
| Trail | None | a trail would cut the run to the 2R target short; the source rides to the liquidity pool |
| Max hold | 72 bars (~3 days) | an OTE entry that hasn't reached target or stop in three days is not the trade |
| Risk | 1% / trade, 3x leverage cap | house standard |
| Warmup | 100 bars | ATR spin-up + displacement + a full sequence of structure |

The design bet is that the full inducement → sweep → MSS → OTE
conjunction marks high-probability reversals, and that the
conjunction (not any single leg) is the edge. The backtest
(BACKTEST.md) cannot confirm or refute that bet: the conjunction
never completes in this window (0 trades), and the diagnostic
funnel shows the binding constraint is the final 70.5%
retracement, not the earlier stages.

No optimization was performed, and the window in BACKTEST.md must
not be used to tune any of these numbers — in particular, do not
widen the OTE band, drop the FVG requirement, or shorten the
displacement threshold to manufacture a sample.
