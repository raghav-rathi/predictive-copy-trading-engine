"""ICT Power of Three / AMD signals (Michael J. Huddleston).

Distribution entries, one trade per UTC day maximum:

    Long entry:  a low sweep occurred this UTC day (08:00-16:00) and
                 a bar in the distribution window (16:00-22:00 UTC)
                 closes back above the accumulation range low.
    Short entry: a high sweep occurred this UTC day and a bar in the
                 distribution window closes back below the
                 accumulation range high.

Entries are only taken on bars with hour 16-22: a signal on the
23:00 bar would execute at the next day's 00:00 open, i.e. outside
the distribution day, so the 23:00 bar is exit-only.

    Long exit / short exit: the 23:00 UTC bar of the day — the
                 position is closed at the next bar's open, the
                 00:00 UTC open of the following day (end of the
                 UTC day). The harness risk layer's 2xATR stop /
                 2.5xATR trail also applies.

Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import numpy as np
import pandas as pd

DIST_START = 16
DIST_END = 22  # inclusive; 23:00 is exit-only
EXIT_HOUR = 23


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    hour = df["pot_hour"].to_numpy()
    day_start = df["pot_day_start"].to_numpy()
    c = df["c"].to_numpy()
    acc_high = df["pot_acc_high"].to_numpy()
    acc_low = df["pot_acc_low"].to_numpy()
    swept_low = df["pot_swept_low"].to_numpy()
    swept_high = df["pot_swept_high"].to_numpy()

    long_entry = np.zeros(n, dtype=bool)
    short_entry = np.zeros(n, dtype=bool)

    traded = False
    cur_day = None
    for i in range(n):
        if day_start[i] != cur_day:
            cur_day = day_start[i]
            traded = False
        if not traded and DIST_START <= hour[i] <= DIST_END:
            if swept_low[i] and c[i] > acc_low[i]:
                long_entry[i] = True
                traded = True
            elif swept_high[i] and c[i] < acc_high[i]:
                short_entry[i] = True
                traded = True

    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = (hour == EXIT_HOUR)
    df["short_exit"] = (hour == EXIT_HOUR)
    return df
