"""Morning star long, evening star short, opposite star exits."""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    o, c, h, l = df["o"], df["c"], df["h"], df["l"]
    body = df["body"]
    first, star = body.shift(2), body.shift(1)
    big = first.abs() > 0.01 * c.shift(2)
    small = star.abs() < 0.003 * c.shift(1)
    morning = (
        (first < 0) & big & small
        & (o.shift(1) < c.shift(2))  # 24/7 crypto has no gaps: open below prior close stands in for the gap
        & (c > df["mid"].shift(2))
        & (c > o)
    )
    evening = (
        (first > 0) & big & small
        & (o.shift(1) > c.shift(2))  # same gap adaptation as morning star
        & (c < df["mid"].shift(2))
        & (c < o)
    )
    df["long_entry"] = morning.fillna(False).to_numpy(dtype=bool)
    df["short_entry"] = evening.fillna(False).to_numpy(dtype=bool)
    df["long_exit"] = evening.fillna(False).to_numpy(dtype=bool)
    df["short_exit"] = morning.fillna(False).to_numpy(dtype=bool)
    return df
