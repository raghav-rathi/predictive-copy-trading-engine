# Fair Value Gap Retest

A mechanization of the ICT / Smart Money Concepts **Fair Value Gap**
(the 3-candle imbalance): when a displacement candle leaves an untraded
band between candle i−2's high and candle i's low, ICT treats that band
as an inefficiency price tends to revisit. The rule is *"wait for price
to return to the gap, enter in the impulse direction, stop beyond the
far edge"* — this module implements exactly that, with no lookahead.

## Mechanism

**Detection (at bar i, using data through bar i's close only):**

- **Bullish FVG:** `l[i] > h[i-2]` (untraded band between candle i−2's
  high and candle i's low) **AND** the displacement candle i−1 was
  impulsive: `range(i-1) > 1.5 × ATR(14)[i-1]`.
  Zone = `[fvg_low = h[i-2], fvg_high = l[i]]`.
- **Bearish FVG:** mirror — `h[i] < l[i-2]`, zone = `[h[i], l[i-2]]`.

The gap is only knowable once candle i closes; detection reads no
future data.

**Zone lifecycle:** only the most recent unmitigated FVG per direction
is kept. A bullish zone dies on the first bar whose low trades below
`fvg_low` (`l < fvg_low`); a bearish zone dies when `h > fvg_high`.
Columns `fvg_bull_low/high`, `fvg_bear_low/high` carry the active zone,
NaN when none is live (forward-filled by a simple loop).

**Signals:**

- **Long entry:** active bullish zone AND `l[i] < fvg_high` (dipped
  INTO the gap) AND `c[i] > fvg_high` (closed back above the top edge =
  rejection). The inequalities are deliberately strict: on the
  formation bar `l[i]` is identically equal to `fvg_high`, so `<`
  excludes it — entry requires a genuine later-bar retest, not the
  displacement bar's own close.
- **Short entry:** mirror (`h[i] > fvg_low` AND `c[i] < fvg_low`).
- **Long exit:** zone mitigated (first bar with `l < fvg_low`, detected
  via the zone column flipping active→NaN) OR a `short_entry`
  (opposite-direction signal). **Short exit:** mirror.

**Risk:** 2.0xATR hard stop — wide by design, approximating *"beyond
the far edge + buffer"* (the harness cannot place a zone-relative
stop, so this is documented as an approximation, not the rule
itself); 2.0xATR chandelier trail; no fixed target (exits are
signal-driven); 72-bar (~3-day) max hold; 1% risk/trade; 3x leverage;
both sides. WARMUP=80.

Usage:

```python
from strategies.fair_value_gap import indicators, signals, risk

sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the a-priori parameter record.

Sources:

- ICT Fair Value Gap trading strategy —
  https://innercircletrader.net/tutorials/fair-value-gap-trading-strategy/
- Fair Value Gap (FVG): the complete guide for ICT traders —
  https://www.equiti.com/sc-en/news/trading-ideas/fair-value-gap-fvg-the-complete-guide-for-ict-traders/
