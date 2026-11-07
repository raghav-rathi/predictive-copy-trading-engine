"""Bollinger Band squeeze breakout signals.

Entry only while a squeeze is armed (a squeeze within the last 10
bars): close above the upper band -> long; close below the lower band
-> short. Entries are crosses — the previous close must still have
been inside the band — so a position is opened once per breakout, not
on every bar spent outside the band. Exit when the close comes back
inside the bands (close < upper for longs, close > lower for shorts).
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy()
    upper = df["bb_upper"].to_numpy()
    lower = df["bb_lower"].to_numpy()
    armed = df["bb_squeeze_armed"].to_numpy(dtype=bool)
    long_entry = np.zeros(n, dtype=bool)
    short_entry = np.zeros(n, dtype=bool)
    long_exit = np.zeros(n, dtype=bool)
    short_exit = np.zeros(n, dtype=bool)
    for i in range(1, n):
        if armed[i]:
            if c[i] > upper[i] and c[i - 1] <= upper[i - 1]:
                long_entry[i] = True
            elif c[i] < lower[i] and c[i - 1] >= lower[i - 1]:
                short_entry[i] = True
        if np.isfinite(upper[i]) and c[i] < upper[i]:
            long_exit[i] = True
        if np.isfinite(lower[i]) and c[i] > lower[i]:
            short_exit[i] = True
    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = long_exit
    df["short_exit"] = short_exit
    return df
