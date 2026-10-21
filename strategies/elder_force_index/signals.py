"""Force Index signals (Alexander Elder, "Trading for a Living", 1993).

Elder's pullback timing applied to the Force Index: buy the dip while
the bulls are in charge, sell the rally while the bears are.

  * long_entry  = (fi13 > 0) & crossed_below(fi2, 0): 13-EMA says the
    bulls are in charge, the 2-EMA dips below zero = the pullback.
  * short_entry = (fi13 < 0) & crossed_above(fi2, 0): mirrored.
  * long_exit   = crossed_below(fi13, 0): the balance of power flipped —
    the trend gauge itself turned, so the bull premise is gone.
  * short_exit  = crossed_above(fi13, 0): mirrored.

NaN-safe: any comparison involving a NaN indicator is False, so no
signal fires before the EMAs are warm. Fully vectorized.
"""

import pandas as pd


def _crossed_below(a: pd.Series, b) -> pd.Series:
    return ((a.shift(1) >= b) & (a < b)).fillna(False)


def _crossed_above(a: pd.Series, b) -> pd.Series:
    return ((a.shift(1) <= b) & (a > b)).fillna(False)


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    fi2 = df["fi2"]
    fi13 = df["fi13"]
    long_entry = (fi13 > 0) & _crossed_below(fi2, 0)
    short_entry = (fi13 < 0) & _crossed_above(fi2, 0)
    long_exit = _crossed_below(fi13, 0)
    short_exit = _crossed_above(fi13, 0)
    for col, s in (
        ("long_entry", long_entry),
        ("short_entry", short_entry),
        ("long_exit", long_exit),
        ("short_exit", short_exit),
    ):
        df[col] = s.fillna(False).astype(bool)
    return df
