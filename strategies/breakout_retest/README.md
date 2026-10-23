# Breakout-Retest Throwback

The polarity principle: old resistance becomes new support, old
support becomes new resistance. A range extreme breaks, price
throws back to the broken level, and — if the level holds — the
rejection close enters in the breakout direction.

## Mechanism

1. **Level:** 20-bar rolling extreme — `level_high = max(h, 20)`,
   `level_low = min(l, 20)`.
2. **Breakout:** close crosses above/below the *prior-bar* level.
   The breakout bar's level (its own 20-bar extreme, including its
   wick) is stored as the line to retest.
3. **Retest window:** the next 20 bars. Evaluated in order on each
   bar's close:
   - **Failed retest (cancel):** a close beyond `level ∓ 0.5×ATR`
     kills the setup — no entry will ever fire for it.
   - **Clean retest (entry):** the wick touches the zone
     (`l ≤ level + 0.1×ATR` for longs, `h ≥ level − 0.1×ATR` for
     shorts) AND the close rejects back across the line
     (`c > level` long, `c < level` short).
   - **Expiry:** a touch after the 20th bar does not count.
4. **Exit:** the entered position keeps its level as anchor;
   `long_exit` fires on a close below `level − 0.5×ATR`
   (level lost), `short_exit` mirrors. Only the most recent
   breakout setup is tracked per side.

Parameters (fixed a priori, no optimization): 20-bar range,
20-bar retest window, 0.1/0.5 ATR touch/loss bands, ATR(14).
WARMUP=80.

## Risk

1.0×ATR hard stop (the canon "tight stop under the retest low" —
a retest that immediately loses 1 ATR is a failed polarity flip),
2.0×ATR measured-move target (~2R), no chandelier trail, 96-bar
(~4-day) max hold. 1% risk/trade, 3× leverage cap, both
directions, 0.045% + 0.01% costs per side.

Usage:

```python
from strategies.breakout_retest import indicators, signals, risk

sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the a-priori parameter note.

Sources:

- Breakout-retest mechanics —
  https://agentictrading.info/learn/what-is-a-breakout-retest.html
- Breakout-retest trading strategy —
  https://daytradingtoolkit.com/strategies/breakout-retest-trading-strategy
