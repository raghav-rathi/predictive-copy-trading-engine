# Order Block Retest

ICT/SMC order-block trading: find where institutional flow
displaced price, then enter when price comes back to that origin
level.

## Mechanics

1. **Displacement.** A 3-bar close-to-close move of at least
   1.5xATR(14) in one direction, ending at bar i:

   ```
   bullish: c[i] - c[i-3] >= 1.5 * atr[i]
   bearish: c[i] - c[i-3] <= -1.5 * atr[i]
   ```

   A move that size in three bars is the footprint of aggressive
   flow, not drift.

2. **Order block.** The range (low..high) of the LAST
   opposite-color candle before the displacement leg, scanning
   back from bar i-3 (the base bar of the move) up to 20 bars.
   Bullish displacement wants the last bearish candle
   (close < open); bearish wants the last bullish candle. If no
   opposite-color candle is found in the scan window, no block
   forms. A newer displacement replaces the active block.

3. **Entry.** Once price has first LEFT the block on the
   displacement side (close above the block high for a bullish
   block, below the block low for a bearish one), a later close
   back INSIDE the block range — while the block is at most 48
   bars old — enters in the displacement direction. One entry per
   block: later re-entries into the same block do not fire again.

4. **Exit.** Close beyond the far side of the entry block (below
   the block low for a long, above the block high for a short —
   block violated), or a new displacement in the opposite
   direction. The harness's 2xATR stop / 2xATR trail / 96-bar max
   hold do the rest of the trade management.

## Risk

2xATR stop, 2xATR chandelier trail, 96-bar (~4-day) max hold, 1%
risk per trade, 3x leverage cap. WARMUP = 60 bars.

Source: ICT (Inner Circle Trader) Smart Money Concepts — order
blocks (https://www.youtube.com/@InnerCircleTrader).
