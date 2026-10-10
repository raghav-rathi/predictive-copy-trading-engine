"""GMMA signals (Daryl Guppy, Trend Trading).

Entry: the whole short group crosses the whole long group --
  long_entry  = (short_min > long_max) & (prev short_min <= prev long_max)
  short_entry = (short_max < long_min) & (prev short_max >= prev long_min)

Exit: the groups recross (Guppy's "take profit when the bands
re-converge"):
  long_exit  = short_min < long_max
  short_exit = short_max > long_min

Risk-level exits (stop, trailing) come from risk.py.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    prev_short_min = df["short_min"].shift(1)
    prev_long_max = df["long_max"].shift(1)
    prev_short_max = df["short_max"].shift(1)
    prev_long_min = df["long_min"].shift(1)

    bull_aligned = df["short_min"] > df["long_max"]
    bear_aligned = df["short_max"] < df["long_min"]
    prev_bull = (prev_short_min > prev_long_max).fillna(False)
    prev_bear = (prev_short_max < prev_long_min).fillna(False)

    df["long_entry"] = (bull_aligned & ~prev_bull).fillna(False)
    df["short_entry"] = (bear_aligned & ~prev_bear).fillna(False)
    df["long_exit"] = ((df["short_min"] < df["long_max"])).fillna(False)
    df["short_exit"] = ((df["short_max"] > df["long_min"])).fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
