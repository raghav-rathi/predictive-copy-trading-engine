"""Opening-range breakout-failure fade indicators.

    or_high / or_low -- the UTC-day opening range: the high /
                        low of the FIRST 4 bars of each UTC
                        day (00:00-03:00 UTC). The level is
                        NaN on the range bars themselves
                        (00:00-03:00) and forward-filled for
                        the rest of the day (04:00-23:00).
                        The range completes at the close of
                        the 03:00 bar (04:00 UTC), so no
                        signal can be generated before 04:00.
    new_day -- True on the first bar of each UTC day (used by
               signals.py to cancel a pending break at the
               day boundary; the old day's range is stale
               once a new day starts).

No lookahead: the range of a day is computed only from that
day's 00:00-03:00 bars, and the level is only exposed on
bars from 04:00 on, after every range bar has closed.
"""

import numpy as np
import pandas as pd

OR_N = 4


def add_indicators(df: pd.DataFrame, or_n: int = OR_N) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    ts = pd.to_datetime(df["t"], unit="ms", utc=True)
    hour = ts.dt.hour.to_numpy()
    day = ts.dt.floor("D").to_numpy()
    h = df["h"].to_numpy(float)
    l = df["l"].to_numpy(float)
    is_range_bar = hour < or_n
    # Per-day high/low over the range bars only; a day with
    # no range bars (e.g. the cache starts mid-day) gets NaN.
    tmp_h = pd.Series(np.where(is_range_bar, h, np.nan))
    or_high_day = tmp_h.groupby(day).transform("max").to_numpy(float)
    tmp_l = pd.Series(np.where(is_range_bar, l, np.nan))
    or_low_day = tmp_l.groupby(day).transform("min").to_numpy(float)
    filled = hour >= or_n
    df["or_high"] = np.where(filled, or_high_day, np.nan)
    df["or_low"] = np.where(filled, or_low_day, np.nan)
    new_day = np.ones(n, dtype=bool)
    if n > 1:
        new_day[1:] = day[1:] != day[:-1]
    df["new_day"] = new_day
    return df
