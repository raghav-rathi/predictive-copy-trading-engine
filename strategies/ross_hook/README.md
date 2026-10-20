# Ross Hook Continuation

Joe Ross's 1-2-3 + Hook: the continuation leg of a completed 1-2-3
formation. After the 1-2-3 completes and price breaks out past point 2,
the first small corrective "hook" that holds is the entry trigger.

Detection is pivot-based — a faithful, fully mechanical simplification
of Ross's discretionary chart pattern (documented as such; Ross himself
trades it by eye):

- **Pivots:** 5-bar fractal pivots (2 bars each side), confirmed with a
  2-bar shift so no future data leaks in.
- **Bullish 1-2-3:** pivot low P1 → pivot high P2 → pivot low P3 with
  P3 > P1 (higher low). **Breakout:** close above P2. **Hook:** the
  first pivot high after the breakout that stays above P3.
  **Long** on a close above the hook high.
- **Bearish:** mirror image (P1 high, P2 low, P3 < P1, close below P2,
  hook = first pivot low after the breakdown staying below P3, short on
  a close below the hook low).
- **Invalidation:** a close back through P1 after the 1-2-3 completes
  resets the sequence. The sequence also resets after an entry fires.
- **Exits:** opposite-sequence entry is a structural exit; the harness
  adds a 1.5xATR stop (proxy for "below the hook low"), 2.5xATR target
  (~the measured 1-2-3 swing projection), 60-bar max hold.
- **Risk:** 1% equity risk/trade, 3x leverage cap, 0.045% fee + 0.01%
  slippage per side.

See BACKTEST.md for the 2026-03-14 → 2026-10-20 Hyperliquid 1h
(BTC/ETH/HYPE) results — an honest loser — and CALIBRATION.md for the
pivot-length sensitivity check.
