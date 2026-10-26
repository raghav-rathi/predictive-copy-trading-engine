"""Dark cloud short, piercing long, opposite pattern exits.

Gap adaptation for 24/7 crypto: there are no overnight gaps, so the
textbook open-beyond-prior-high/low is replaced by open-beyond-prior-
close. The midpoint-close rule (Nison's threshold) is unchanged.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    o, c, h, l = df["o"], df["c"], df["h"], df["l"]
    prev_o, prev_c, prev_h, prev_l, prev_mid = o.shift(1), c.shift(1), h.shift(1), l.shift(1), df["mid"].shift(1)
    dark = (prev_c > prev_o) & (o > prev_c) & (c < prev_c) & (c < prev_mid) & (c > prev_o)
    piercing = (prev_c < prev_o) & (o < prev_c) & (c > prev_c) & (c > prev_mid) & (c < prev_o)
    df["long_entry"] = piercing.fillna(False).to_numpy(dtype=bool)
    df["short_entry"] = dark.fillna(False).to_numpy(dtype=bool)
    df["long_exit"] = dark.fillna(False).to_numpy(dtype=bool)
    df["short_exit"] = piercing.fillna(False).to_numpy(dtype=bool)
    return df
