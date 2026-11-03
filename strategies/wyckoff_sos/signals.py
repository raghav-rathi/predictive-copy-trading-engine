"""Wyckoff Sign of Strength signals.

Wyckoff sign of strength / weakness: a close above the prior 40-bar high on volume over 1.5x its 20-bar average is a sign of strength (long); a close below the prior 40-bar low on the same volume condition is a sign of weakness (short). Exits on close back inside the range.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    vol_ok = (df["v"] > 1.5 * df["avg_vol"]).fillna(False)
    long_e = ((df["c"] > df["range_high"]) & vol_ok).fillna(False)
    short_e = ((df["c"] < df["range_low"]) & vol_ok).fillna(False)
    df["long_entry"] = long_e.astype(bool)
    df["short_entry"] = short_e.astype(bool)
    df["long_exit"] = (df["c"] < df["range_high"]).fillna(False).astype(bool)
    df["short_exit"] = (df["c"] > df["range_low"]).fillna(False).astype(bool)
    return df
