"""Prior-week range breakout indicators (UTC week, Monday 00:00 UTC).

Prior-week high = highest high of the previous complete UTC week
(Monday 00:00 UTC to Sunday 23:00 UTC); prior-week low = lowest
low of the same week. The level in force on bar i is the last
COMPLETED week's range: levels update only at week boundaries
(the Monday 00:00 UTC bar), never intraweek.

A week counts as complete only if all 168 hourly bars of it are
present in the frame — the first partial week at the start of the
data therefore yields NaN levels until a full week has been
observed, so no signal can fire before the first completed week.

WEEK_SPAN (default 1) is how many complete prior weeks the range
spans; USE_WICKS (default True) uses the weeks' highs/lows rather
than their closes. Both are shipped at their canonical values.

Columns:
    prior_week_high / prior_week_low -- levels in force (NaN until
        the first completed week)
    atr -- Wilder ATR(14) for the risk layer

No lookahead: the level on bar i comes only from bars of weeks
that ended before bar i's week started.
"""

import pandas as pd

from strategies import base as B

BARS_PER_WEEK = 168  # 24 * 7 hourly bars
WEEK_SPAN = 1        # number of complete prior weeks spanned by the range
USE_WICKS = True     # False -> range from weekly max/min close instead


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ts = pd.to_datetime(df["t"], unit="ms", utc=True)
    # Monday 00:00 UTC of the bar's own week.
    week_start = (ts - pd.to_timedelta(ts.dt.weekday, unit="D")).dt.floor("D")
    hi_s = df["h"] if USE_WICKS else df["c"]
    lo_s = df["l"] if USE_WICKS else df["c"]
    wk = pd.DataFrame(
        {"ws": week_start, "h": hi_s.to_numpy(dtype=float),
         "l": lo_s.to_numpy(dtype=float)}
    )
    g = wk.groupby("ws").agg(hi=("h", "max"), lo=("l", "min"), cnt=("h", "size"))
    complete = g[g["cnt"] == BARS_PER_WEEK]
    # Level in force on a bar = stats of the previous WEEK_SPAN
    # complete weeks. A span week only counts if it is complete.
    hi_map = complete["hi"]
    lo_map = complete["lo"]
    prior_ws = week_start - pd.Timedelta(days=7 * WEEK_SPAN)
    # Walk back week by week: the level is the max/min over the
    # WEEK_SPAN weeks ending with the week before this bar's week.
    import numpy as np

    hi_vals = np.full(len(df), np.nan)
    lo_vals = np.full(len(df), np.nan)
    for k in range(WEEK_SPAN):
        ws_k = prior_ws + pd.Timedelta(days=7 * k)
        hv = ws_k.map(hi_map).to_numpy(dtype=float)
        lv = ws_k.map(lo_map).to_numpy(dtype=float)
        hi_vals = np.fmax(hi_vals, hv)
        lo_vals = np.fmin(lo_vals, lv)
    df["prior_week_high"] = hi_vals
    df["prior_week_low"] = lo_vals
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
