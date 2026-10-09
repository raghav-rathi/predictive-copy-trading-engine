"""Keltner + ADX signals.

Long  when close crosses above Keltner upper AND ADX > 25
Short when close crosses below Keltner lower AND ADX > 25
Exit long  when close crosses below Keltner mid (trend exhaustion)
Exit short when close crosses above Keltner mid.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    valid = df["kc_upper"].notna() & df["adx"].notna()
    regime = df["adx"] > 25.0
    df["long_entry"] = crossed_above(df["c"], df["kc_upper"]) & regime & valid
    df["short_entry"] = crossed_below(df["c"], df["kc_lower"]) & regime & valid
    df["long_exit"] = crossed_below(df["c"], df["kc_mid"])
    df["short_exit"] = crossed_above(df["c"], df["kc_mid"])
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
