"""Opening-range breakout-failure fade signals.

Break: the close crosses ABOVE or_high (upside break) or
BELOW or_low (downside break) -- crossed_above /
crossed_below on the opening-range levels. A break arms a
pending setup on its side; a new break cancels any pending
(unfailed) setup and arms its own side.

Failure (entry): within 6 bars after an upside break, a
close back BELOW the broken or_high enters SHORT; within 6
bars after a downside break, a close back ABOVE the broken
or_low enters LONG. The failure is judged against the level
frozen at the break bar (fail_up_level / fail_down_level)
and detected with crossed_below / crossed_above on that
frozen series, so it is a genuine re-cross, not a level
condition: only the first failure per break counts (the
pending setup is consumed on the failure bar), a pending
setup expires after 6 bars, and a new UTC day cancels it.
If both failure triggers would fire on the same bar, enter
NEITHER (intrabar order unknowable; in practice impossible
with a single pending setup -- a guard, not a live path).

Exit: the close goes back above the frozen or_high that a
short faded (the break was real after all), or below the
frozen or_low that a long faded; or the opposite fade entry
fires. Exit levels are frozen at the entry bar. The house
2xATR hard stop / 3xATR trail sit behind these exits, and
the 24-bar max hold caps a trade that never resolves.

Note on the first break bar: or_high/or_low are NaN on the
range bars (00:00-03:00), so crossed_above has no prior-bar
level at 04:00 and the first detectable break is the 05:00
bar. A breakout that closes on the 04:00 bar itself is not
picked up unless price re-crosses the level later -- a
consequence of the level series starting at 04:00, not a
tuning choice.

Signal columns are boolean, no NaN, no lookahead
(execution at next-bar open is handled by the harness).
"""

import numpy as np
import pandas as pd

from strategies.base import crossed_above, crossed_below

FAILURE_BARS = 6


def add_signals(df: pd.DataFrame, failure_bars: int = FAILURE_BARS) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy(float)
    or_high = df["or_high"].to_numpy(float)
    or_low = df["or_low"].to_numpy(float)
    new_day = df["new_day"].fillna(False).to_numpy(bool)
    up_break = (
        crossed_above(df["c"], df["or_high"]).fillna(False).to_numpy(bool)
    )
    down_break = (
        crossed_below(df["c"], df["or_low"]).fillna(False).to_numpy(bool)
    )

    # Frozen break levels, live while a setup is pending.
    fail_up = np.full(n, np.nan)
    fail_down = np.full(n, np.nan)
    pend_up_bar = -1
    pend_up_level = np.nan
    pend_down_bar = -1
    pend_down_level = np.nan
    for i in range(n):
        # A new UTC day cancels any pending setup: the old
        # day's range is stale once a new range starts forming.
        if new_day[i]:
            pend_up_bar = -1
            pend_up_level = np.nan
            pend_down_bar = -1
            pend_down_level = np.nan
        if pend_up_bar >= 0 and i - pend_up_bar > failure_bars:
            pend_up_bar = -1
            pend_up_level = np.nan
        if pend_down_bar >= 0 and i - pend_down_bar > failure_bars:
            pend_down_bar = -1
            pend_down_level = np.nan
        # Carry the pending levels into this bar's columns.
        if pend_up_bar >= 0:
            fail_up[i] = pend_up_level
        if pend_down_bar >= 0:
            fail_down[i] = pend_down_level
        # A failure on this bar consumes the pending setup.
        # The column keeps the level on this bar so the
        # crossed_below / crossed_above below can detect it;
        # it goes NaN from the next bar, so no second failure
        # can fire for the same break.
        if pend_up_bar >= 0 and c[i] < pend_up_level:
            pend_up_bar = -1
            pend_up_level = np.nan
        if pend_down_bar >= 0 and c[i] > pend_down_level:
            pend_down_bar = -1
            pend_down_level = np.nan
        # A new break cancels any pending setup and arms its
        # own side. The level is written into the frozen-level
        # column on the break bar itself, so the failure cross
        # on the next bar has a prior-bar level to compare
        # against (same reason the NR7 bracket column includes
        # its arming bar). Both breaks on one bar would need a
        # close above or_high and below or_low at once --
        # impossible (or_low <= or_high) -- so arm neither as
        # a guard.
        if up_break[i] and down_break[i]:
            pass
        elif up_break[i]:
            pend_up_bar = i
            pend_up_level = or_high[i]
            pend_down_bar = -1
            pend_down_level = np.nan
            fail_up[i] = or_high[i]
        elif down_break[i]:
            pend_down_bar = i
            pend_down_level = or_low[i]
            pend_up_bar = -1
            pend_up_level = np.nan
            fail_down[i] = or_low[i]

    df["or_break_up"] = up_break
    df["or_break_down"] = down_break
    df["fail_up_level"] = fail_up
    df["fail_down_level"] = fail_down

    long_raw = (
        crossed_above(df["c"], pd.Series(fail_down, index=df.index))
        .fillna(False)
        .to_numpy(bool)
    )
    short_raw = (
        crossed_below(df["c"], pd.Series(fail_up, index=df.index))
        .fillna(False)
        .to_numpy(bool)
    )
    # Ambiguous intrabar order: both triggers on one bar -> neither.
    both = long_raw & short_raw
    long_entry = long_raw & ~both
    short_entry = short_raw & ~both

    long_exit = np.zeros(n, dtype=bool)
    short_exit = np.zeros(n, dtype=bool)
    held_long_level = None   # or_low frozen at the long entry bar
    held_short_level = None  # or_high frozen at the short entry bar
    for i in range(n):
        # Exits are judged against levels from entries on earlier bars.
        if held_long_level is not None and (
            c[i] < held_long_level or short_entry[i]
        ):
            long_exit[i] = True
            held_long_level = None
        if held_short_level is not None and (
            c[i] > held_short_level or long_entry[i]
        ):
            short_exit[i] = True
            held_short_level = None
        if held_long_level is None and long_entry[i]:
            held_long_level = fail_down[i]
        if held_short_level is None and short_entry[i]:
            held_short_level = fail_up[i]
    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = long_exit
    df["short_exit"] = short_exit
    return df
