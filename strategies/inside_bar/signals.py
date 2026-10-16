"""Inside-bar breakout signals.

An inside bar with trend bias arms a breakout watch: the first of the
next ``expiry`` bars whose high (long) exceeds the mother bar's high or
whose low (short) breaks the mother bar's low fires the entry. Unfilled
setups expire. No lookahead: a signal on bar i uses bar i's own high/low
(known at bar i's close) against the mother of the earlier setup bar.
"""

import pandas as pd


def add_signals(df: pd.DataFrame, expiry: int = 2) -> pd.DataFrame:
    df = df.copy()
    setup_long = df["inside"] & df["long_bias"]
    setup_short = df["inside"] & df["short_bias"]
    h, l = df["h"], df["l"]

    long_entry = False
    short_entry = False
    for k in range(1, expiry + 1):
        armed_long = setup_long.shift(k).fillna(False).astype(bool)
        armed_short = setup_short.shift(k).fillna(False).astype(bool)
        # mother of the setup at bar j is bar j-1 -> h[j-1] is h.shift(k+1) at bar i
        long_entry = long_entry | (armed_long & (h > h.shift(k + 1)))
        short_entry = short_entry | (armed_short & (l < l.shift(k + 1)))

    df["long_entry"] = long_entry.fillna(False).astype(bool)
    df["short_entry"] = short_entry.fillna(False).astype(bool)
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    return df
