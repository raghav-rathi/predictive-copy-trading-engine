# Volatility Contraction Pattern (VCP) — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Swing pivot | 5-bar, centre+2 confirmation | The spec's pivot definition; shared with sfp. |
| Contraction shrink | depth[k] < 0.95 * depth[k-1] | The spec's 0.95 shrink factor. |
| Pullback depth | (high − low) / high; rally depth (high − low) / low | Percent move of the leg; pullbacks measured off the high, rallies off the low. |
| Trend filter | Long: c > SMA(50) AND SMA(50) > SMA(200); short mirror | The spec's Stage-2 uptrend proxy (1h bars) and its symmetric mirror. |
| Breakout volume | v > 1.5x SMA(volume, 50) | The spec's expansion threshold. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 250 | SMA(200) needs 200 bars; 250 gives margin. |

## Spec decisions / ambiguities

1. **A leg that extends the same starting pivot updates in place.**
   A swing high can be followed by two successive swing lows
   (e.g. a shallow dip, then a deeper low) before the next swing
   high. The shipped code treats the later low as an extension of
   the same pullback (recomputed depth/trough/volume), not as a
   second pullback — otherwise one high with two lows would
   falsely count as a two-leg contraction chain. Same for rallies.
2. **Legs with depth <= 0 are not pullbacks/rallies.** A swing low
   that prints above the preceding swing high (possible when the
   market drifts up between pivots) has negative depth and is
   ignored rather than counted as a contraction leg.
3. **The pivot is the high/low of the last completed leg, tracked
   even before the base validates.** pivot_high is set as soon as
   the first pullback completes; the entry additionally requires
   vcp_valid, so the level alone never triggers a trade. The exit
   "close back below the pivot" keys off the same latest-leg pivot,
   which can move if a new pullback completes while a trade is open.
4. **The short side is a symmetric extension, not Minervini's
   original.** Minervini's VCP is long-only; the short base (successive
   rallies, each shallower, each peak lower, volume declining) and
   the downtrend filter are the mirror image, built the same way.
   Rally depth is measured off the low ((high − low) / low) while
   pullback depth is measured off the high, so each is the percent
   move of its own leg.
5. **vcp_valid is a separate column from the trend filter.**
   The pattern flag is purely structural (>= 2 qualifying legs);
   the SMA(50)/SMA(200) filter lives in signals, not indicators.
   An extra vcp_valid_short column carries the short base so the
   single vcp_valid column stays long-only.
6. **Harness stop/trail as an additional exit.** The spec's exits
   are the failed breakout back through the pivot / opposite VCP
   signal; the batch-standard risk layer (2xATR stop, 2.5xATR
   trail, 120-bar max hold) is applied on top, per the batch
   instruction.

## What the exits actually did

Shipped run (180 trades): 103 trades ended on a signal exit and
77 on the harness stop/trail (BTC 34 signal / 29 stop, ETH 37 /
22, HYPE 32 / 26). The failed-breakout exit fires on well over
half the trades: most pivot breakouts close back below the pivot
within a few bars, so the pattern's breakout leg rarely runs —
the base validates often (~25% of bars on BTC/ETH) but the
breakout does not follow through on 1h crypto. The base validates
on ~29% of bars on BTC/ETH (~23% on HYPE), so the pattern is
common; the breakout leg is what fails.

No bug fixes requiring re-runs, no PnL-selected tuning.
