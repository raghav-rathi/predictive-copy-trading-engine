# Follow-Through Day (O'Neil)

William O'Neil's CANSLIM market-direction signal, scaled from
daily bars to 1h bars (1 "day" = 24 bars, UTC-midnight aligned):
after a correction, a rally attempt either confirms with a
strong up day on rising volume (the follow-through day) or
fails by undercutting its low.

- **Daily aggregates:** d_close = close of the day's 23:00
  bar; d_low = minimum low of the day; d_vol = sum of the
  day's 24 volumes.
- **Correction gate:** d_close <= 0.92 * trailing 20-day max
  of d_close (>= 8% below the 20-day high).
- **New low:** d_low <= trailing 20-day min of d_low
  (prior 20 days, excluding the current day).
- **Attempt:** day 1 = the first day that closes UP
  (d_close > prior day d_close) after a new-low day, while
  the correction gate is/was true. attempt_day counts 1, 2,
  3, ... from day 1.
- **attempt_low:** d_low of the day immediately BEFORE day 1
  (the new-low day). Documented choice: the single prior
  day's low, not the minimum over all correction days -- the
  prior day is the day that printed the 20-day low, so
  undercutting it is a fresh 20-day low by construction.
- **Attempt fails** and resets if any later day's d_low
  undercuts attempt_low (checked on attempt-days 2-7; day 1's
  own intraday dip below the prior day's low does not fail
  it -- the check applies to later days). The undercutting
  day becomes a fresh awaiting low. An attempt with no FTD
  expires after attempt-day 7.
- **FTD (long entry):** on attempt-day 4-7, a day with day
  return (d_close / prior d_close - 1) >= 1.5% AND d_vol >
  prior day d_vol. The entry fires on that day's 23:00 bar
  (crossed_above on the 0/1 ftd_day flag -- exactly one bar
  per confirmed attempt). Long only; there is no opposite
  in O'Neil's FTD.
- **Exit:** a later day's close (d_close at its 23:00 bar)
  below attempt_low. 2xATR hard stop, 3xATR trail, 240-bar
  (10-day) max hold behind it.
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 240-bar
  max hold, 1% risk/trade, 3x leverage

Parameters: correction drop 8%, lookback 20 days, gain
threshold 1.5%, FTD window attempt-days 4-7, ATR(14) for
risk, WARMUP 528 bars (~22 days: 20-day lookback + 48).
Entries are CROSS-based (crossed_above on the ftd_day flag),
never level conditions.

Deviations / implementation notes (all documented, none
tuned to PnL):

- O'Neil's original is a daily-index signal; the 24-bar
  UTC-day aggregation is the shipped scaling to 1h crypto.
- The correction gate uses a 20-day max of closes including
  the current day; the new-low test uses the prior 20 days'
  lows excluding the current day (including it would make
  every day a "new low").
- attempt_low is the prior day's low (see above), not the
  min over the correction -- a deliberate reading of the
  brief, stated here so it can be challenged.
- The FTD test is evaluated only on the completed (23:00)
  bar; intraday bars carry the prior completed day's close
  in d_close, so no intraday poke can trigger an entry.
- The first day in the cache (2026-03-14) has only 2 bars
  (22:00, 23:00); its d_vol is a 2-bar partial. It is inside
  warmup and does not affect any trade.

Sources: William O'Neil, "How to Make Money in Stocks" --
https://traderlion.com/trading-strategies/follow-through-day/

Usage:

```python
from strategies.follow_through_day import indicators, signals, risk

df = indicators.add_indicators(df)  # gain_pct=0.015, attempt 4-7 default
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 -> 2026-11-27 Hyperliquid 1h
(BTC/ETH/HYPE, batch-49 pinned window) results and
CALIBRATION.md for the gain-threshold (1.0/1.5/2.0%) and
attempt-window (4-7/4-10) sensitivity checks.
