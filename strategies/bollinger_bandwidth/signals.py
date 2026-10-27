"""Bandwidth breakout signals: close outside the band while bbw is
expanding; exit on a close back through the mid-band.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    expanding = df["bbw"] > df["bbw_ma"]
    up = crossed_above(df["c"], df["bb_upper"]) & expanding
    dn = crossed_below(df["c"], df["bb_lower"]) & expanding
    df["long_entry"] = up.fillna(False).astype(bool)
    df["short_entry"] = dn.fillna(False).astype(bool)
    df["long_exit"] = crossed_below(df["c"], df["bb_mid"]).fillna(False).astype(bool)
    df["short_exit"] = crossed_above(df["c"], df["bb_mid"]).fillna(False).astype(bool)
    return df
