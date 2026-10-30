"""Asian-range breakout signals.

    long_entry  -- first breakout above the day's Asian range
                   high (breakout_dir == +1) while flat, at
                   most one entry per UTC day
    short_entry -- mirror below the range low
    long_exit   -- a bar at UTC hour >= 16 while in a same-day
                   long position (the breakout window ends at
                   16:00 UTC; the harness executes this at the
                   next bar's open), or the first bar of a new
                   UTC day if the 16:00 bar is missing
    short_exit  -- mirror

The risk layer's trailing stop and the 24-bar max hold are the
other exit paths. Boolean columns, no NaN, no lookahead (the
Asian range used is already complete by 08:00 UTC).
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    d = df["breakout_dir"].to_numpy(dtype=int)
    times = pd.to_datetime(df["t"], unit="ms", utc=True)
    hours = times.dt.hour.to_numpy(dtype=int)
    # UTC day number, derived from the bar timestamp alone.
    day_no = (df["t"].to_numpy(dtype=np.int64) // 86_400_000).astype(np.int64)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None
    entry_day = None
    last_entry_day = None
    for i in range(n):
        if pos is not None:
            # Time exit: 16:00 UTC bar of the entry day, or the
            # first bar of a later day if the 16:00 bar is absent.
            if (day_no[i] == entry_day and hours[i] >= 16) or day_no[i] != entry_day:
                if pos == "long":
                    lx[i] = True
                else:
                    sx[i] = True
                pos = None
        if pos is None and d[i] != 0 and day_no[i] != last_entry_day:
            if d[i] == 1:
                le[i] = True
                pos = "long"
            else:
                se[i] = True
                pos = "short"
            entry_day = day_no[i]
            last_entry_day = day_no[i]

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
