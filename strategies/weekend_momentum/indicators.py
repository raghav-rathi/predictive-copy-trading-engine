"""Weekend crypto momentum indicators (causal, no lookahead).

Pipeline, computed bar by bar using only data through bar i:

1. 168h momentum: mom168 = close[i] - close[i-168] (and the
   percentage form mom168_pct). 168 hourly bars = 7 days, so the
   momentum compares this hour with the same hour last week.
2. UTC session: weekday/hour are derived from the t column
   (pd.to_datetime(df["t"], unit="ms", utc=True)). The weekend
   session is Friday 00:00 UTC through Sunday 23:59 UTC
   (weekday in {4, 5, 6}); is_monday_open marks the Monday 00:00
   UTC bar, the first bar after the weekend session.
3. ATR(14) for the risk layer.

Columns:

    mom168        -- close minus close 168 bars ago (price units)
    mom168_pct    -- close / close 168 bars ago - 1
    weekday       -- UTC weekday (Mon=0 .. Sun=6)
    hour          -- UTC hour of the bar open
    is_weekend    -- True on Fri 00:00 UTC .. Sun 23:59 UTC bars
    is_monday_open -- True on the Monday 00:00 UTC bar
    atr           -- Wilder ATR(14)

No lookahead: momentum reads closes <= i (the 168-bar lag is a
lookBACK, not a lookahead), the session flags are a pure function
of bar i's own timestamp, and ATR reads bars <= i.
"""

import numpy as np
import pandas as pd

from strategies import base as B

MOM_LB = 168  # 7 days of hourly bars


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    lag = c.shift(MOM_LB)
    df["mom168"] = c - lag
    df["mom168_pct"] = c / lag - 1
    dt = pd.to_datetime(df["t"], unit="ms", utc=True)
    df["weekday"] = dt.dt.weekday.to_numpy(dtype=int)
    df["hour"] = dt.dt.hour.to_numpy(dtype=int)
    df["is_weekend"] = df["weekday"].isin([4, 5, 6])
    df["is_monday_open"] = (df["weekday"] == 0) & (df["hour"] == 0)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
