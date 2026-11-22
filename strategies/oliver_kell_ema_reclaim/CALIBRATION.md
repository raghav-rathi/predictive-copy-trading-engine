# Oliver Kell 20-EMA Reclaim — Calibration

All parameters were fixed **a priori** from the published rules
and 1h-bar reasoning — there is no in-sample sweep, so there is
nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| Trend filter | close > rising 200 SMA; 10/20 EMAs rising | the source's leader filter: only buy pullbacks in an established uptrend |
| Pullback depth | 5–19% off the trailing-20-bar high | the source's pullback band: shallow enough to still be a pullback, deep enough to be a real dip |
| Pullback touch | close below the 20 EMA within the prior 10 bars | the source's "pullback to/below the 20 EMA", with a 10-bar window so the touch is recent |
| Quiet volume | entry-bar volume < 20-bar average volume | the source's pullback on quiet volume (no selling pressure) |
| Entry | cross back above the 20 EMA | the source's reclaim trigger |
| Exit | close below the 20 EMA | the source's exit |
| Hard stop | 3% below entry in the source; 2xATR(14) here | see deviation below |
| Max hold | 336 bars (~14 days) | Kell's holds run days to weeks; a reclaim that has not run in two weeks is not the trade |
| Risk | 1% / trade, 3x leverage cap | house standard |

## Documented deviations

1. **3% stop approximated by 2xATR(14).** `RiskConfig`
   expresses stops only as a multiple of ATR, not as a fixed
   percentage. On 1h crypto bars ATR(14) is typically ~1–1.5%
   of price, so 2xATR lands in the 2–3% band the source intends.
   The "under the pullback low" alternative stop is not
   expressible in `RiskConfig` and is not used.
2. **Wedge pop not formalized.** The source's setup starts with
   a "wedge pop" (a breakout from a consolidation wedge) that
   marks the leader. A wedge pop has no published formal rule,
   so it is not coded; the rising-200-SMA / rising-EMA filter is
   the operational proxy for "leader in an uptrend". This makes
   the shipped version slightly more permissive than Kell's
   discretionary filter.
3. **Daily → 1h period mapping.** The source trades daily bars;
   periods (10/20/200) are carried over bar-for-bar to 1h. A
   20-bar pullback on 1h is under a day, where Kell's is ~a
   month — the setup is therefore a faster, noisier cousin of
   the original, and the backtest should be read as such.

No parameter was tuned on the backtest window.
