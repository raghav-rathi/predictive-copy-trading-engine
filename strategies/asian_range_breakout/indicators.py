"""Asian-session range breakout indicators (causal, no lookahead).

Adapted to 24/7 crypto: for each UTC day, the Asian range is
the high/low of that day's bars with UTC hour in [0, 8). The
range is only usable once the Asian session has closed, so
bars at hour >= 8 use their own day's range, and bars before
08:00 carry the previous completed day's range in
``asian_high`` / ``asian_low`` (a display/continuity column;
no signal is ever generated before 08:00, so the previous
day's range on those bars cannot enter a trade).

``breakout_dir`` is +1 on the first qualifying post-08:00 bar
type: a 1h bar with hour in [8, 16) whose close breaks above
that day's Asian range high AND whose volume exceeds its
prior 20-bar average volume. Mirror for -1. Whether it is the
day's *first* breakout is enforced in signals.py (one entry
per UTC day).

Columns:
    asian_high, asian_low -- completed Asian range (see above)
    vol_avg20             -- prior-20-bar average volume
    breakout_dir          -- +1 / -1 breakout bar, else 0
    atr                   -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B

VOL_LOOKBACK = 20


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    times = pd.to_datetime(df["t"], unit="ms", utc=True)
    hours = times.dt.hour.to_numpy(dtype=int)
    days = times.dt.floor("D")

    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    v = df["v"].to_numpy(dtype=float)
    n = len(df)

    # Per-day Asian range from bars with UTC hour in [0, 8) only.
    asian = {}
    tmp = pd.DataFrame({"day": days.to_numpy(), "hour": hours, "h": h, "l": l})
    for day, grp in tmp[tmp["hour"] < 8].groupby("day"):
        asian[day] = (float(grp["h"].max()), float(grp["l"].min()))

    asian_high = np.full(n, np.nan)
    asian_low = np.full(n, np.nan)
    for i in range(n):
        day = days.iloc[i]
        if hours[i] >= 8:
            rng = asian.get(day)
        else:
            rng = asian.get(day - pd.Timedelta(days=1))
        if rng is not None:
            asian_high[i], asian_low[i] = rng

    vol_avg = pd.Series(v).rolling(VOL_LOOKBACK, min_periods=VOL_LOOKBACK).mean().shift(1).to_numpy(dtype=float)

    breakout_dir = np.zeros(n, dtype=int)
    for i in range(n):
        if 8 <= hours[i] < 16 and np.isfinite(asian_high[i]) and np.isfinite(vol_avg[i]):
            if c[i] > asian_high[i] and v[i] > vol_avg[i]:
                breakout_dir[i] = 1
            elif c[i] < asian_low[i] and v[i] > vol_avg[i]:
                breakout_dir[i] = -1

    df["asian_high"] = asian_high
    df["asian_low"] = asian_low
    df["vol_avg20"] = vol_avg
    df["breakout_dir"] = breakout_dir
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
