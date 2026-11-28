"""Day-of-week effect signals.

The harness executes a signal on bar i at bar i+1's open, so
each leg is signalled on the 23:00 bar of the prior UTC day:

    long_entry  -- Sunday 23:00 (weekday 6, hour 23): executed
                   at Monday 00:00 open; the Monday long.
    long_exit   -- Monday 23:00 (weekday 0, hour 23): executed
                   at Tuesday 00:00 open.
    short_entry -- Wednesday 23:00 (weekday 2, hour 23):
                   executed at Thursday 00:00 open; the
                   Thursday short.
    short_exit  -- Thursday 23:00 (weekday 3, hour 23):
                   executed at Friday 00:00 open.

Each signal fires on exactly one bar per week by construction
(a single weekday+hour combination), so there is no re-fire
issue -- this is the documented exception to the house
CROSS-based entry rule. The house 2xATR hard stop / 3xATR
trail sit behind the timed exits, with a 30-bar max hold.

Variants (calibration only; shipped config is the defaults):
    mon_long   -- include the Monday long leg
    thu_short  -- include the Thursday short leg
    wed_long   -- additionally LONG Wednesdays: enter Tuesday
                  23:00 (executed Wednesday 00:00), exit
                  Wednesday 23:00 (executed Thursday 00:00).
                  The Wednesday 23:00 bar then carries both a
                  long exit and the Thursday short entry; the
                  harness exits first and enters second at the
                  same open, so the legs do not collide.

Signal columns are boolean, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd


def add_signals(
    df: pd.DataFrame,
    mon_long: bool = True,
    thu_short: bool = True,
    wed_long: bool = False,
) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    wd = df["weekday"].to_numpy(int)
    hr = df["hour"].to_numpy(int)
    sun23 = (wd == 6) & (hr == 23)
    mon23 = (wd == 0) & (hr == 23)
    tue23 = (wd == 1) & (hr == 23)
    wed23 = (wd == 2) & (hr == 23)
    thu23 = (wd == 3) & (hr == 23)

    long_entry = np.zeros(n, dtype=bool)
    long_exit = np.zeros(n, dtype=bool)
    short_entry = np.zeros(n, dtype=bool)
    short_exit = np.zeros(n, dtype=bool)
    if mon_long:
        long_entry |= sun23
        long_exit |= mon23
    if wed_long:
        long_entry |= tue23
        long_exit |= wed23
    if thu_short:
        short_entry |= wed23
        short_exit |= thu23

    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = long_exit
    df["short_exit"] = short_exit
    return df
