"""Volume Oscillator signals: zero cross + price trend filter.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = crossed_above(df["vol_osc"], 0) & (df["c"] > df["sma20"])
    dn = crossed_below(df["vol_osc"], 0) & (df["c"] < df["sma20"])
    df["long_entry"] = up.fillna(False).astype(bool)
    df["short_entry"] = dn.fillna(False).astype(bool)
    df["long_exit"] = dn.fillna(False).astype(bool)
    df["short_exit"] = up.fillna(False).astype(bool)
    return df
