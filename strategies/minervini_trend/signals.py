"""Minervini Trend Template signals.

  long_entry:  the bar the template flips false -> true (stage-2 entry)
  long_exit:   template breakdown — c < SMA(50d) OR SMA(50d) < SMA(150d)
  short_entry / short_exit: never (Minervini does not short; the risk
             config also sets allow_shorts=False).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    t = df["mt_template"].fillna(False).astype(bool)
    prev = t.shift(1).fillna(False).astype(bool)
    df["long_entry"] = t & ~prev
    df["short_entry"] = pd.Series(False, index=df.index)
    df["long_exit"] = (
        (df["c"] < df["mt_sma50"]) | (df["mt_sma50"] < df["mt_sma150"])
    ).fillna(False)
    df["short_exit"] = pd.Series(False, index=df.index)
    return df
