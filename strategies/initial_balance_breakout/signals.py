"""Initial Balance breakout signals.

Long entry: the first bar AFTER the IB bar whose close is above the IB
high (closed-bar breakout). Short entry: the first bar after the IB bar
whose close is below the IB low. First side broken wins; ONE trade per
UTC day -- after an entry signal, no new entry signals fire until the
next UTC day. No entry signals on bars outside 01:00-13:00 UTC.

Exits (signal exits): exit a long on a close back below the IB high
(reclaim = idea wrong) or on a close at/above the 1x IB extension
target (IB high + IB range). Exit a short on a close back above the
IB low or on a close at/below IB low - IB range.

State is tracked in a causal simulation: the simulated position opens
on the entry-signal bar and closes on the exit-signal bar, so exits
only fire for the side actually entered and entries are suppressed
while a simulated position is open. A simulated position carried past
midnight keeps evaluating exits against the new day's IB levels (see
CALIBRATION.md). All inputs use data through bar i's close only, so
signals on bar i use no future data.
"""

import numpy as np
import pandas as pd

ENTRY_FIRST_HOUR = 1
ENTRY_LAST_HOUR = 13


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    long_entry = np.zeros(n, dtype=bool)
    short_entry = np.zeros(n, dtype=bool)
    long_exit = np.zeros(n, dtype=bool)
    short_exit = np.zeros(n, dtype=bool)
    if n:
        t = pd.to_datetime(df["t"], unit="ms", utc=True)
        hour = t.dt.hour.to_numpy()
        day = t.dt.floor("D").to_numpy()
        c = df["c"].to_numpy(dtype=float)
        ib_high = df["ib_high"].to_numpy(dtype=float)
        ib_low = df["ib_low"].to_numpy(dtype=float)
        ib_range = df["ib_range"].to_numpy(dtype=float)
        cur_day = None
        entered_today = False
        sim = None  # 'long' / 'short' / None
        for i in range(n):
            d = day[i]
            if cur_day is None or d != cur_day:
                cur_day = d
                entered_today = False
                # sim is NOT reset: a position carried past midnight keeps
                # evaluating exits against the new day's IB levels.
            if not (np.isfinite(ib_high[i]) and np.isfinite(ib_low[i])):
                continue
            if sim is None and not entered_today:
                hr = hour[i]
                if ENTRY_FIRST_HOUR <= hr <= ENTRY_LAST_HOUR:
                    if c[i] > ib_high[i]:
                        long_entry[i] = True
                        entered_today = True
                        sim = "long"
                        continue
                    if c[i] < ib_low[i]:
                        short_entry[i] = True
                        entered_today = True
                        sim = "short"
                        continue
            if sim == "long":
                if c[i] < ib_high[i] or c[i] >= ib_high[i] + ib_range[i]:
                    long_exit[i] = True
                    sim = None
            elif sim == "short":
                if c[i] > ib_low[i] or c[i] <= ib_low[i] - ib_range[i]:
                    short_exit[i] = True
                    sim = None
    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = long_exit
    df["short_exit"] = short_exit
    return df
