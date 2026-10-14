"""VWAP reversion signals.

Long  when VWAP z-score < -1.5 (stretched below the day's VWAP)
Short when VWAP z-score > +1.5 (stretched above)
Exit long  when z >= 0 (back to VWAP); exit short when z <= 0.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    valid = df["vwap_z"].notna()
    df["long_entry"] = (df["vwap_z"] < -1.5) & valid
    df["short_entry"] = (df["vwap_z"] > 1.5) & valid
    df["long_exit"] = df["vwap_z"] >= 0
    df["short_exit"] = df["vwap_z"] <= 0
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
