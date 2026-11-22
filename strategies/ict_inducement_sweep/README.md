# ICT Inducement → Sweep → MSS Entry

The full ICT sequence, mechanically translated: mark the order
block, wait for inducement, wait for the sweep into the POI,
confirm with a market-structure shift plus displacement and a
fair-value gap, enter at the 70.5% OTE retracement.

## The sequence (bullish; bearish is the exact mirror)

1. **Order block / POI.** A displacement bar — range > 1.5×ATR(14),
   closing in the top quarter of its range — marks the POI as the
   last opposing (down) candle in the 10 bars before it. The OB
   zone is that candle's [low, high].
2. **Inducement.** The first minor swing low after the displacement
   (3-bar confirmed) whose low sits above the OB top — between
   price and the POI. Equal lows qualify.
3. **Sweep.** A bar closing below the inducement extreme AND at or
   below the OB top — price takes the inducement liquidity and
   closes into the OB zone.
4. **MSS + displacement + FVG.** After the sweep, a close above the
   highest high from the inducement bar through the sweep bar (the
   minor structure high). The confirming bar is the displacement
   bar itself — in ICT the displacement IS what breaks structure —
   so the break bar must also be a displacement bar (range >
   1.5×ATR(14), strong close) leaving a fair-value gap (its low
   above the high two bars earlier). If the break bar is not
   itself a displacement bar, a displacement bar within the next
   10 bars still confirms. The displacement leg runs from the
   sweep bar through the displacement bar.
5. **OTE entry.** The 70.5% retracement of the displacement leg.
   Entry fires on the first bar whose low touches the level
   (limit-style); if no retracement within 24 bars the setup is
   dropped. If price closes below the OB low first, the POI has
   failed and the setup is dropped.

Timeouts: no inducement within 48 bars of the displacement, no
sweep within 48 bars of the inducement, no MSS within 24 bars of
the sweep, no displacement within 10 bars of the MSS → the setup
is dropped.

## What is NOT implemented

- **No killzone / session filter.** The session/killzone variant
  (MQL5 blog) is not implemented — no time-of-day gate is applied.
- **No discretionary POI selection.** The OB is always the last
  opposing candle before the displacement leg; a human ICT trader
  would pick among several candidate POIs.

## Relation to existing strategies

`liquidity_sweep`, `sfp`, `order_block_retest` and `fvg_mitigation`
already exist. This strategy is distinct ONLY as the FULL sequence
(inducement + sweep + MSS + OTE) — the individual legs are not new,
the conjunction is. The source itself says inducement is
hindsight-friendly: a lone swing low only looks like "inducement"
after price sweeps it. The strict sequence is the defence against
that, and it fires rarely by design — see BACKTEST.md, where the
full sequence produces zero trades in this window.

## Risk

Stop beyond the POI, approximated by 2xATR (see CALIBRATION.md
for the documented deviation); target ~2R at 4xATR; no trail;
72-bar max hold; 1% risk per trade; 3x leverage cap. WARMUP = 100
bars.

Sources: ForexMT4Indicators, "Inducement in ICT Trading
Explained" (https://forexmt4indicators.com/what-is-inducement/);
session/killzone variant (https://www.mql5.com/en/blogs/post/750916,
not implemented).
