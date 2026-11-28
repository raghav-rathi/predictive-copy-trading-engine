# Opening Range Breakout Failure Fade

The opening-range fade: the first hours of the UTC day set a
range; a breakout that cannot hold it is faded. Breakouts
that are real run; breakouts that fail snap back into the
range, and the fade rides that snap-back.

- **Opening range:** high/low of the FIRST 4 bars of each UTC
  day (00:00-03:00 UTC): or_high / or_low. NaN on the range
  bars themselves, forward-filled for the rest of the day
  (04:00-23:00). No signal can be generated before 04:00.
- **Break:** the close crosses ABOVE or_high (upside break)
  or BELOW or_low (downside break) -- crossed_above /
  crossed_below on the opening-range levels. A break arms a
  pending setup on its side; a new break cancels any pending
  (unfailed) setup and arms its own side.
- **Failure (entry):** within 6 bars after an upside break, a
  close back BELOW the broken or_high enters SHORT; within 6
  bars after a downside break, a close back ABOVE the broken
  or_low enters LONG. The failure is judged against the level
  frozen at the break bar and detected with crossed_below /
  crossed_above on that frozen series, so it is a genuine
  re-cross, not a level condition: only the first failure per
  break counts, a pending setup expires after 6 bars, and a
  new UTC day cancels it.
- **Both triggers same bar:** enter NEITHER -- with OHLC data
  the intrabar order is unknowable. (With a single pending
  setup only one failure can fire per bar, so this is a guard,
  not a live path.)
- **Exit:** close back above the frozen or_high that a short
  faded (the break was real after all), or below the frozen
  or_low that a long faded; or the opposite fade entry fires.
  2xATR hard stop, 3xATR trail, 24-bar max hold behind them.
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 24-bar
  max hold (one UTC day), 1% risk/trade, 3x leverage

Parameters: OR window 4 bars, failure window 6 bars, ATR(14)
for risk. Breaks are CROSS-based (crossed_above /
crossed_below on the opening-range levels) and failures are
CROSS-based on the frozen break level; the single-fire
pending-setup state machine means an entry fires on exactly
one bar per break, never every bar a level condition holds.

Deviations / implementation notes (all documented, none
tuned to PnL):

- or_high/or_low are NaN on the range bars (00:00-03:00) and
  first appear on the 04:00 bar. crossed_above therefore has
  no prior-bar level at 04:00, so the first detectable break
  is the 05:00 bar. A breakout that closes on the 04:00 bar
  itself is not picked up unless price re-crosses the level
  later -- a consequence of the level series starting at
  04:00, not a tuning choice.
- The frozen break level is written into the fail_up_level /
  fail_down_level column on the break bar itself, so the
  failure cross on the next bar has a prior-bar level to
  compare against (the same reason the NR7 bracket column
  includes its arming bar).
- A pending setup is cancelled at the UTC day boundary: the
  old day's range is stale once a new range starts forming.
  A failure is therefore never judged against yesterday's
  range.
- Exit levels are frozen at the entry bar (the or_high / or_low
  that was broken and failed). A live trailing range would
  move the invalidation while the trade is open; with a
  24-bar max hold the trade can cross midnight, and the frozen
  level is the one the trade was actually taken against.
- A failure and a new break can coincide on one bar (e.g. a
  close below or_low both fails a pending upside break and
  breaks down): the failure entry fires and the new break
  arms. The entry is evaluated against the pending setup
  entering the bar, before the new break is processed.

Source: Opening range breakout failure fade — ORB failure --
https://steady-turtle.com/knowledge/opening-range-breakout-strategy

Usage:

```python
from strategies.orb_fade import indicators, signals, risk

df = indicators.add_indicators(df)  # or_n=4 default
sig = signals.add_signals(df)  # failure_bars=6 default
```

See BACKTEST.md for the 2026-03-14 -> 2026-11-28 Hyperliquid 1h
(BTC/ETH/HYPE, batch-49 pinned window) results and
CALIBRATION.md for the OR-window (4/8) and failure-window
(6/12) sensitivity checks.
