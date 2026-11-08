"""Rolling volume-profile POC signals.

Bias: close above POC = long bias, below POC = short bias.
Long: the bar's low dips to within 0.5x ATR(14) of POC (low <= POC +
0.5*ATR) and the close comes back above POC, while the prior bar's
close was above its POC (a pullback to POC from above, not a cross
from below). Short mirror.
Exit: long_exit at close >= VAH or close < POC; short_exit at close
<= VAL or close > POC. All levels use only data through bar i's
close.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    l = df["l"]
    h = df["h"]
    poc = df["vp_poc"]
    vah = df["vp_vah"]
    val = df["vp_val"]
    a = df["atr14"]
    prev_close_above = (c.shift(1) > poc.shift(1))
    prev_close_below = (c.shift(1) < poc.shift(1))
    df["long_entry"] = (
        (l <= poc + 0.5 * a) & (c > poc) & prev_close_above
    ).fillna(False).astype(bool)
    df["short_entry"] = (
        (h >= poc - 0.5 * a) & (c < poc) & prev_close_below
    ).fillna(False).astype(bool)
    df["long_exit"] = ((c >= vah) | (c < poc)).fillna(False).astype(bool)
    df["short_exit"] = ((c <= val) | (c > poc)).fillna(False).astype(bool)
    return df
