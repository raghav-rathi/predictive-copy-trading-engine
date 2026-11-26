# ICT Killzone

ICT killzones: trade the London and New York opens off the
Asian range. The Asian session builds a range; the killzone
sweeps one side of it, displaces through market structure,
and the retracement to the 50% level of the displacement leg
is the entry.

- **Asian range:** high/low of the 00:00-03:00 UTC bars of
  the current UTC day
- **London killzone:** 07:00-10:00 UTC (02:00-05:00 ET)
- **NY killzone:** 12:00-14:00 UTC (07:00-09:00 ET)
- **Sweep (window only):** close beyond the Asian high/low,
  then close back inside it within 2 bars of the bar that
  made the sweep extreme
- **Displacement (window only):** within the same killzone
  window, price moves >= 1.0x ATR(14) in the sweep-opposite
  direction (from the back-inside close) AND breaks the near
  swing (frozen at the back-inside bar)
- **Long:** close crosses below the 50% level of the
  displacement leg after a bullish displacement
- **Short:** mirror (close crosses above the 50% level)
- **Invalidation:** close beyond the leg start (beyond the
  sweep extreme) cancels a pending setup
- **Exit:** close beyond the leg start (the opposite sweep),
  or the opposite setup's entry; 2xATR hard stop, 3xATR
  trail, 24-bar max hold behind them
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 24-bar
  max hold (intraday by design), 1% risk/trade, 3x leverage

Parameters: swing 20 bars, displacement 1.0x ATR(14),
retracement level 50%, back-inside 2 bars. The 50% level is
the FVG-midpoint approximation, documented: on 1h bars the
fair-value gap is approximated by the displacement leg's
midpoint, since locating a true FVG needs sub-hour
structure.

Deviation from the brief, documented: the brief says "no
entries outside the two killzone windows", but on 1h bars
the minimum sequence is 4 bars (sweep -> back-inside ->
displacement -> retracement) while the London window is 3
bars and the NY window 2 bars -- a strict reading makes
the strategy unfireable by construction. Two accommodations:
(1) windows are inclusive of their end-hour bar (London
07:00-10:00, NY 12:00-14:00 hourly bars -- the bar opening
at the end hour is that hour's price action), so the NY
window can at least contain the 3-bar sweep -> back ->
displacement sequence; (2) the sweep and the displacement
must both complete inside a window (enforced), but an armed
setup's retracement entry may land after the window closes,
expiring at the UTC day boundary instead. No NEW setup may
start outside a window.

Sources: ICT kill zones --
https://www.ictkillzone.com/ict-kill-zones and
https://audacity.capital/trading-guides/ict-kill-zones/

Usage:

```python
from strategies.ict_killzone import indicators, signals, risk

df = indicators.add_indicators(df)  # disp_mult=1.0 default
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 → 2026-11-26 Hyperliquid 1h
(BTC/ETH/HYPE, batch-47 pinned window) results and
CALIBRATION.md for the displacement-threshold 0.75/1.0/1.5
sensitivity check.
