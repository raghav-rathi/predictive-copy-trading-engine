"""New York open momentum indicators.

The New York open is fixed at 13:00 UTC (winter/GMT reading — see
CALIBRATION.md decision 1; crypto is 24/7, so this is a clock rule,
not a real market open). The first-hour range is the high/low of the
13:00 UTC bar (13:00-14:00). During the 14:00-17:00 UTC window (the
bars opening 14:00, 15:00 and 16:00), a close above the first-hour
high is a long break, a close below the first-hour low a short break;
only the first break of the day per side fires.

Columns:
    ny_high, ny_low -- today's first-hour range (NaN if the 13:00
        bar is missing from the frame)
    ny_time_exit -- True on the 21:00 UTC bar (the time exit;
        the harness executes it at the next bar's open)
    long_trigger / short_trigger -- True only on the entry bar
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

OPEN_HOUR = 13       # New York open, fixed at 13:00 UTC
WINDOW_START = 14    # break window opens 14:00 UTC
WINDOW_END = 17      # break window closes 17:00 UTC (bars 14, 15, 16)
EXIT_HOUR = 21       # time exit on the close of the 21:00 UTC bar

INDICATOR_COLS = ["ny_high", "ny_low", "ny_time_exit",
                  "long_trigger", "short_trigger", "atr"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    times = pd.to_datetime(df["t"], unit="ms", utc=True)
    hours = times.dt.hour.to_numpy(dtype=int)
    days = times.dt.floor("D")

    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    n = len(df)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)

    # Per-day first-hour range from the 13:00 UTC bar.
    first_hour = {}
    tmp = pd.DataFrame({"day": days.to_numpy(), "hour": hours, "h": h, "l": l})
    for day, grp in tmp[tmp["hour"] == OPEN_HOUR].groupby("day"):
        first_hour[day] = (float(grp["h"].max()), float(grp["l"].min()))

    ny_high = np.full(n, np.nan)
    ny_low = np.full(n, np.nan)
    time_exit = np.zeros(n, dtype=bool)
    long_trig = np.zeros(n, dtype=bool)
    short_trig = np.zeros(n, dtype=bool)

    cur_day = None
    fired_long = fired_short = False

    for i in range(n):
        day = days.iloc[i]
        if day != cur_day:
            cur_day = day
            fired_long = fired_short = False
        rng = first_hour.get(day)
        # Only from the 13:00 bar itself: bars earlier in the day must
        # not see a range that has not formed yet.
        if rng is not None and hours[i] >= OPEN_HOUR:
            ny_high[i], ny_low[i] = rng
            if WINDOW_START <= hours[i] < WINDOW_END:
                if not fired_long and c[i] > rng[0]:
                    long_trig[i] = True
                    fired_long = True
                elif not fired_short and c[i] < rng[1]:
                    short_trig[i] = True
                    fired_short = True
        time_exit[i] = hours[i] == EXIT_HOUR

    df["ny_high"] = ny_high
    df["ny_low"] = ny_low
    df["ny_time_exit"] = time_exit
    df["long_trigger"] = long_trig
    df["short_trigger"] = short_trig
    return df
