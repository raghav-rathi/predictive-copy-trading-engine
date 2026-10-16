"""Gann swing signals — pullback entry timing inside the main trend.

  long_entry:  3-bar trend is up AND the 1-bar swing turns up after
               having been down (buy the pullback, not the breakout)
  short_entry: 3-bar trend is down AND the 1-bar swing turns down
               after having been up
  long_exit:   3-bar trend flips down
  short_exit:  3-bar trend flips up

All terms are known at bar i's close; execution is at bar i+1's open.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    sw = df["gann_swing1"]
    tr = df["gann_trend3"]
    sw_prev = sw.shift(1).fillna(0).astype(int)
    df["long_entry"] = (tr == 1) & (sw == 1) & (sw_prev == -1)
    df["short_entry"] = (tr == -1) & (sw == -1) & (sw_prev == 1)
    df["long_exit"] = tr == -1
    df["short_exit"] = tr == 1
    return df
