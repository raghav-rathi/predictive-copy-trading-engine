"""Williams A/D signals.

Long when price is above its 50-bar SMA (uptrend) AND WAD crosses above
its 20-bar SMA (fresh accumulation). Short mirrors: price below the
50-bar SMA and WAD crosses below its 20-bar SMA (fresh distribution).

Exits are the cross back through the WAD SMA: a long exits when WAD
crosses back below its SMA (distribution resumes), a short exits when
WAD crosses back above its SMA.

All signal columns are boolean, no NaN; execution at next-bar open is
handled by the harness.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    uptrend = (df["c"] > df["price_sma50"]).fillna(False)
    downtrend = (df["c"] < df["price_sma50"]).fillna(False)
    cross_up = B.crossed_above(df["wad"], df["wad_sma20"]).fillna(False)
    cross_dn = B.crossed_below(df["wad"], df["wad_sma20"]).fillna(False)
    df["long_entry"] = (cross_up & uptrend).fillna(False).astype(bool)
    df["short_entry"] = (cross_dn & downtrend).fillna(False).astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
