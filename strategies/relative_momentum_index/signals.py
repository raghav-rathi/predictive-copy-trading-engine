"""RMI signals: cross of the 50 midline; exit on the opposite cross.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = crossed_above(df["rmi"], 50)
    dn = crossed_below(df["rmi"], 50)
    df["long_entry"] = up.fillna(False).astype(bool)
    df["short_entry"] = dn.fillna(False).astype(bool)
    df["long_exit"] = dn.fillna(False).astype(bool)
    df["short_exit"] = up.fillna(False).astype(bool)
    return df
