"""London session breakout indicators (fixed-UTC adaptation).

For each UTC day, the range is the highest high / lowest low of
the hourly bars 00:00-08:00 UTC (hours 0-7). The completed range
is assigned to that day's bars 08:00-16:00 UTC (hours 8-15) and
is NaN outside that window. The 08:00 bar is the first entry bar
and the range is complete before it: the 00:00-07:00 bars are all
closed by then, so no lookahead.

Columns:
    hour        -- UTC hour of the bar (0-23)
    london_day  -- UTC date string of the bar
    range_high  -- completed 00:00-08:00 UTC range high for the day
    range_low   -- completed 00:00-08:00 UTC range low for the day
    atr         -- Wilder ATR(14) for the risk layer

No lookahead: the range for a day uses only that day's 00:00-07:00
bars, and is only visible on bars from 08:00 onward.
"""

import pandas as pd

from strategies import base as B

RANGE_START_HOUR = 0
RANGE_END_HOUR = 8
ENTRY_END_HOUR = 16

INDICATOR_COLS = ["hour", "london_day", "range_high", "range_low", "atr"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    dt = pd.to_datetime(df["t"], unit="ms", utc=True)
    df["hour"] = dt.dt.hour.astype(int)
    df["london_day"] = dt.dt.strftime("%Y-%m-%d")
    range_mask = (df["hour"] >= RANGE_START_HOUR) & (df["hour"] < RANGE_END_HOUR)
    rng = (df.loc[range_mask]
             .groupby("london_day")
             .agg(range_high=("h", "max"), range_low=("l", "min")))
    rh = df["london_day"].map(rng["range_high"])
    rl = df["london_day"].map(rng["range_low"])
    in_window = (df["hour"] >= RANGE_END_HOUR) & (df["hour"] < ENTRY_END_HOUR)
    df["range_high"] = rh.where(in_window)
    df["range_low"] = rl.where(in_window)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
